-- ============================================================================
--  MIGRATION 0001 — the point-in-time fact store
--
--  Governed by: D-021 (forward-only numbered SQL, own runner, own transaction,
--  session advisory lock, verification query), ruling 5 (universe from filing
--  history), TDD §5.1 (point-in-time), D8 handover §1-§3.
--
--  RUN AS: a schema_admin. A `writer` is refused CREATE TABLE by design
--  (A-017, D-031), so this cannot run as the application account. See OPEN-27.
--
--  LOCKING NOTE — deliberate departure from D-021's literal wording.
--  D-021 says "session advisory lock". This uses pg_advisory_xact_lock, which
--  is TRANSACTION-scoped. Reason: the app connects through pgbouncer
--  (F-next/app-connects-via-pgbouncer). A session-scoped pg_advisory_lock is
--  unreliable under transaction pooling — the session a lock is taken on is not
--  guaranteed to be the session the next statement runs on. A transaction-scoped
--  lock is held for exactly the transaction that holds the migration, which is
--  the unit D-021 already specifies, and it releases on COMMIT or ROLLBACK
--  without an explicit unlock that a crash could skip.
--  This is stricter than D-021, not looser. Recorded rather than done quietly.
--
--  THIS MIGRATION CREATES NO PRICE TABLES. The vendor is unchosen and two
--  disqualifying properties are unanswered (OPEN-9). A price schema written
--  before the vendor is known would be written to the wrong shape.
-- ============================================================================

BEGIN;

-- Lock key 20260001: arbitrary, project-scoped, one per migration number.
SELECT pg_advisory_xact_lock(20260001);

-- Needed for the EXCLUDE constraint on filer_ticker (btree equality inside a
-- GiST exclusion constraint). Requires schema_admin.
CREATE EXTENSION IF NOT EXISTS btree_gist;


-- ----------------------------------------------------------------------------
--  filer — identity, and ONLY identity
--
--  Identity is CIK. Not ticker. A ticker may now belong to a different company,
--  and symbols get reassigned (ruling 5, and EODHD's own documentation warning
--  from the vendor side). A universe keyed on ticker is wrong in both
--  directions: it loses dead companies and silently merges live ones.
--
--  The `current_*` columns are named that way ON PURPOSE. They are EDGAR
--  submissions metadata, which describes the filer TODAY. A 2014 backtest that
--  reads current_sic gets 2026's classification. The column name is the warning,
--  and it is the cheapest possible place to put one — a query writer sees it at
--  the point of use without reading any documentation.
--
--  For point-in-time SIC, use filing.sic_at_filing instead.
-- ----------------------------------------------------------------------------
CREATE TABLE filer (
    cik                 bigint      PRIMARY KEY,
    current_name        text        NOT NULL,
    current_sic         text        NULL,
    current_sic_desc    text        NULL,
    -- When the current_* columns were last refreshed from EDGAR. Without this,
    -- "current" is an unbounded claim.
    metadata_as_of      date        NOT NULL,
    CONSTRAINT filer_cik_positive CHECK (cik > 0)
);

COMMENT ON TABLE filer IS
    'One row per EDGAR filer, keyed on CIK. current_* columns are as-of '
    'metadata_as_of and are NOT point-in-time. Use filing.sic_at_filing for '
    'historical classification.';


-- ----------------------------------------------------------------------------
--  filer_ticker — ticker as a TIME-BOUNDED ATTRIBUTE, never an identity
--
--  The EXCLUDE constraint is the load-bearing part. It makes it impossible for
--  one ticker to resolve to two CIKs at the same time, while still permitting
--  the same ticker to be reassigned to a different CIK later. That is exactly
--  the real-world behaviour, and it is enforced by the database rather than by
--  remembering to check.
--
--  valid_to NULL means "still in force". The daterange is half-open [from, to),
--  so a ticker that moves on 2019-06-01 has the old row ending and the new row
--  starting on that date with no overlap and no gap.
-- ----------------------------------------------------------------------------
CREATE TABLE filer_ticker (
    cik         bigint      NOT NULL REFERENCES filer (cik),
    ticker      text        NOT NULL,
    exchange    text        NULL,
    valid_from  date        NOT NULL,
    valid_to    date        NULL,
    CONSTRAINT filer_ticker_range_sane CHECK (valid_to IS NULL OR valid_to > valid_from),
    CONSTRAINT filer_ticker_no_overlap EXCLUDE USING gist (
        ticker WITH =,
        daterange(valid_from, valid_to, '[)') WITH &&
    )
);

CREATE INDEX filer_ticker_cik_idx ON filer_ticker (cik);
CREATE INDEX filer_ticker_ticker_idx ON filer_ticker (ticker);

COMMENT ON TABLE filer_ticker IS
    'Ticker is an attribute of a filer over a date range, not an identity. '
    'The EXCLUDE constraint forbids one ticker resolving to two CIKs at the '
    'same instant while permitting reassignment over time.';


-- ----------------------------------------------------------------------------
--  filing — the unit of "what was knowable, and when"
--
--  filing_date is the knowability boundary. Every point-in-time query in this
--  project reduces to "filing_date <= D".
--
--  period_of_report is the period the filing describes, and is NOT the same
--  thing. A 10-K for FY2022 filed in 2023 is knowable from its filing_date,
--  describes period_of_report. Conflating the two is the lookahead bug.
--
--  amends_accession is nullable because EDGAR does not always make the link
--  explicit and we will not invent it. A NULL there means "not established",
--  not "not an amendment" — is_amendment carries that separately.
-- ----------------------------------------------------------------------------
CREATE TABLE filing (
    accession           text        PRIMARY KEY,
    cik                 bigint      NOT NULL REFERENCES filer (cik),
    form_type           text        NOT NULL,
    filing_date         date        NOT NULL,
    period_of_report    date        NULL,
    sic_at_filing       text        NULL,
    -- Derived from form_type at ingest. Stored rather than computed so that a
    -- change in how we detect amendments does not silently restate history.
    is_amendment        boolean     NOT NULL,
    amends_accession    text        NULL REFERENCES filing (accession),
    CONSTRAINT filing_accession_shape CHECK (accession ~ '^[0-9]{10}-[0-9]{2}-[0-9]{6}$'),
    CONSTRAINT filing_no_self_amend CHECK (amends_accession IS DISTINCT FROM accession)
);

CREATE INDEX filing_cik_date_idx  ON filing (cik, filing_date);
CREATE INDEX filing_date_idx      ON filing (filing_date);
-- Supports the universe query: CIKs with a given form in a date window.
CREATE INDEX filing_form_date_idx ON filing (form_type, filing_date);

COMMENT ON COLUMN filing.filing_date IS
    'The knowability boundary. Point-in-time queries filter on this, never on '
    'period_of_report.';


-- ----------------------------------------------------------------------------
--  fact — one numeric XBRL fact, bound to the filing that asserted it
--
--  ========================================================================
--   THE KEY CHOICE, AND WHAT IT MAKES IMPOSSIBLE
--  ========================================================================
--  The uniqueness is (accession, concept, period, unit, dimensions).
--  It is NOT (cik, concept, period).
--
--  (cik, concept, period) is the key that LOOKS right — it reads like the
--  natural identity of a financial fact. It is the defect. It permits exactly
--  one row for "Apple's FY2022 revenue", so when a 10-K/A arrives with a
--  restated figure the only way to store it is UPDATE, or INSERT ... ON
--  CONFLICT DO UPDATE. That overwrite destroys the point-in-time property
--  silently and permanently, and TDD §13 says it must be caught in review
--  rather than in backtest. This is that review.
--
--  WHAT THE CHOSEN KEY MAKES IMPOSSIBLE:
--
--  1. It is impossible to overwrite a fact with an amended value. An amended
--     value arrives under a DIFFERENT accession, so it cannot collide. There is
--     no constraint for it to violate and therefore no upsert to be tempted by.
--
--  2. It is impossible to express "the current value of revenue for FY2022" as
--     a row. There is no such row and no unique index that would produce one.
--     Currency is a QUERY — order by filing_date, take the latest at or before
--     D — and a query can be asked "as of when?". A row cannot.
--
--  3. It is impossible to ingest the same filing twice into different rows.
--     ON CONFLICT on this key can only ever fire for a re-ingest of the same
--     accession, which is idempotency. That is the one case where DO NOTHING is
--     correct, and it is the only case the key permits.
--
--  What it deliberately does NOT prevent: two filings asserting different
--  values for the same concept and period. That is not corruption. That is the
--  restatement, and recording both is the entire point.
--  ========================================================================
--
--  dimensions: XBRL facts may be qualified by segment, geography, product and
--  so on. The consolidated fact has none. '{}' means consolidated.
--  Storing this rather than discarding it is defensive: silently mixing a
--  segment revenue with a consolidated revenue is a classic and invisible
--  error, and a schema that cannot represent the distinction cannot refuse it.
--  v1 queries filter dimensions = '{}'.
--
--  period_type: instants (balance sheet) carry period_start = period_end.
--  Using equal dates rather than a NULL start keeps every column of the
--  uniqueness key NOT NULL — NULLs in a unique key do not compare equal, and a
--  key that silently stops enforcing on NULL rows is worse than no key.
-- ----------------------------------------------------------------------------
CREATE TABLE fact (
    fact_id         bigint      GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    accession       text        NOT NULL REFERENCES filing (accession),
    concept         text        NOT NULL,
    taxonomy        text        NOT NULL DEFAULT 'us-gaap',
    unit            text        NOT NULL,
    period_type     text        NOT NULL,
    period_start    date        NOT NULL,
    period_end      date        NOT NULL,
    value           numeric     NOT NULL,
    dimensions      jsonb       NOT NULL DEFAULT '{}'::jsonb,

    CONSTRAINT fact_period_type_valid CHECK (period_type IN ('instant', 'duration')),
    CONSTRAINT fact_period_ordered    CHECK (period_start <= period_end),
    CONSTRAINT fact_instant_is_a_point CHECK (
        period_type <> 'instant' OR period_start = period_end
    ),

    -- The key. See the block comment above for what it forecloses.
    CONSTRAINT fact_one_per_filing UNIQUE (
        accession, taxonomy, concept, unit, period_type,
        period_start, period_end, dimensions
    )
);

-- The point-in-time workhorse. Answers "this concept, for this filer, as
-- known at date D" once joined to filing.
CREATE INDEX fact_concept_period_idx ON fact (concept, period_end, period_start);
CREATE INDEX fact_accession_idx      ON fact (accession);
-- Consolidated facts are the overwhelming majority of reads; a partial index
-- keeps the v1 access path narrow.
CREATE INDEX fact_consolidated_idx   ON fact (concept, period_end)
    WHERE dimensions = '{}'::jsonb;

COMMENT ON TABLE fact IS
    'One numeric XBRL fact as asserted by one filing. An amendment INSERTS a '
    'new row under its own accession; nothing is ever updated. Currency is a '
    'query over filing_date, not a property of a row.';


-- ----------------------------------------------------------------------------
--  schema_migration — the runner''s own ledger
--
--  D-021 requires our own runner. The runner needs somewhere to record what it
--  has applied, and that record belongs in the database it applied them to —
--  not in a file that can travel separately from the schema it describes.
-- ----------------------------------------------------------------------------
CREATE TABLE schema_migration (
    version         integer     PRIMARY KEY,
    name            text        NOT NULL,
    applied_at      timestamptz NOT NULL DEFAULT now(),
    -- Checksum of the migration file as applied. A migration whose file has
    -- changed since it ran is a different migration wearing the same number.
    sha256          text        NOT NULL
);

INSERT INTO schema_migration (version, name, sha256)
VALUES (1, '0001_fact_store', 'SET-BY-RUNNER');

COMMIT;
