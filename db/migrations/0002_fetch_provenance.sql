-- ============================================================================
--  MIGRATION 0002 — fetch provenance
--
--  Governed by: D-023 (every fetch records source URL, retrieval timestamp and
--  a hash of the payload; raw filings are not stored because accession plus
--  hash makes any row re-derivable), OPEN-34, D16 §2.
--
--  RUN AS: a schema_admin. See OPEN-27.
--  NO TRANSACTION CONTROL IN THIS FILE — the runner owns it.
--
--  WHY THIS IS 0002 AND NOT A THIRD AMENDMENT TO 0001
--  --------------------------------------------------
--  0001 has still never been applied to a surviving database, so amending it
--  again would be defensible. It is 0002 anyway, for two reasons given in D16
--  §2.4. The "never applied" argument is true and was becoming a habit — and a
--  habit is what it looks like from outside once it has been used three times.
--  And the runner's forward-only, sequence-gap, high-water-mark and duplicate-
--  version guards have only ever run against synthetic migrations; a real 0002
--  exercises them against the thing they exist for, at no cost, before
--  production does.
--
--  WHY PROVENANCE CANNOT BE RETROFITTED, EXPRESSED AS A REFUSAL
--  ------------------------------------------------------------
--  A provenance row describes a fetch: its URL, the moment it happened, and the
--  hash of what came back. Once a fetch has happened unrecorded, that record
--  cannot be reconstructed — not from the database, not from EDGAR, not from
--  anything. Re-fetching produces a NEW fetch, not evidence of the old one.
--
--  So this migration does not backfill. If rows already exist without
--  provenance, there is no honest value to give them, and inventing one would
--  put a fabricated fetch behind real data — indistinguishable from a real one
--  forever after. It RAISES instead, and says why. The impossibility is the
--  argument for doing this before the fact slice, and it is encoded here rather
--  than asserted in a comment.
-- ============================================================================


-- ----------------------------------------------------------------------------
--  fetch — one row per RETRIEVAL EVENT, not per URL and not per payload
--
--  ========================================================================
--   THE KEY CHOICE, AND WHAT IT MAKES IMPOSSIBLE
--  ========================================================================
--  Uniqueness is (url, retrieved_at). It is NOT (url), and NOT (url, sha256).
--
--  (url) is the key that looks right — one row per thing we fetched. It is the
--  same defect as (cik, concept, period) in 0001: it permits exactly one row
--  per URL, so a second fetch can only be stored by overwriting the first. The
--  history of retrievals is destroyed, and with it the only evidence of when a
--  payload changed.
--
--  (url, sha256) is subtler and also wrong. It collapses repeated identical
--  fetches into one row, which silently discards the most useful thing an
--  unchanged re-fetch tells you: that the resource was STILL unchanged at a
--  later moment. That is not a duplicate. It is a second observation, and it
--  bounds the window in which a change did not happen.
--
--  WHAT (url, retrieved_at) MAKES IMPOSSIBLE:
--
--  1. It is impossible to lose a retrieval by re-fetching. Every fetch is an
--     event and every event gets a row.
--
--  2. It is impossible to answer "what did this URL contain?" as though that
--     were a property of the URL. It is a property of a MOMENT, and the schema
--     will only answer it that way.
--
--  3. It is impossible for two fetches to be indistinguishable. Same URL, same
--     bytes, different instant — two rows, correctly.
--
--  THE TWO CASES, AND WHICH ONE IS A FINDING (D16 §2.5):
--
--  Same URL, SAME sha256, twice   -> two rows. NOT a finding. This is evidence
--                                    the resource was unchanged across that
--                                    interval, which is worth having.
--
--  Same URL, DIFFERENT sha256     -> two rows, and THIS IS THE FINDING.
--                                    EDGAR changed underneath us. It is exactly
--                                    the event D-023's re-derivability claim is
--                                    about: "accession plus hash makes any row
--                                    re-derivable" becomes FALSE for every row
--                                    derived from the superseded payload,
--                                    because that payload no longer exists
--                                    anywhere.
--
--  The schema does not forbid the second case — it is a real-world event, not a
--  data error, and a constraint that rejected it would simply stop us recording
--  the truth. It makes it DETECTABLE instead: see the fetch_content_change view.
-- ----------------------------------------------------------------------------
CREATE TABLE fetch_log (
    fetch_id        bigint      GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    url             text        NOT NULL,
    retrieved_at    timestamptz NOT NULL,
    -- Hash of the payload as received. D-023's third required field, and the
    -- one that makes a change detectable at all.
    sha256          text        NOT NULL,
    -- Cheap, and it distinguishes "the document changed" from "the fetch was
    -- truncated", which look identical through a hash alone.
    content_bytes   bigint      NULL,

    CONSTRAINT fetch_log_sha256_shape CHECK (sha256 ~ '^[0-9a-f]{64}$'),
    CONSTRAINT fetch_log_bytes_sane   CHECK (content_bytes IS NULL OR content_bytes >= 0),
    CONSTRAINT fetch_log_one_per_moment UNIQUE (url, retrieved_at)
);

CREATE INDEX fetch_log_url_time_idx ON fetch_log (url, retrieved_at DESC);
-- Supports the change-detection query below without a sequential scan.
CREATE INDEX fetch_log_url_hash_idx ON fetch_log (url, sha256);

COMMENT ON TABLE fetch_log IS
    'One row per retrieval EVENT. Keyed on (url, retrieved_at), never on url '
    'alone — what a URL contained is a property of a moment, not of the URL.';


-- ----------------------------------------------------------------------------
--  fetch_content_change — the finding, as a standing query
--
--  A URL whose payload hash has changed between retrievals. Every row here is
--  a case where D-023's re-derivability claim has lapsed for the data loaded
--  from the earlier fetch.
--
--  A view rather than a trigger or a constraint, deliberately. This is not
--  corruption to be prevented; it is an event to be noticed. A trigger would
--  have to decide what to do about it at write time, when the only correct
--  answer is "tell a human".
-- ----------------------------------------------------------------------------
CREATE VIEW fetch_content_change AS
SELECT
    url,
    count(DISTINCT sha256)              AS distinct_payloads,
    count(*)                            AS retrievals,
    min(retrieved_at)                   AS first_seen,
    max(retrieved_at)                   AS last_seen
FROM fetch_log
GROUP BY url
HAVING count(DISTINCT sha256) > 1;

COMMENT ON VIEW fetch_content_change IS
    'URLs whose payload changed between retrievals. Each row means EDGAR '
    'changed underneath us and re-derivability has lapsed for rows loaded from '
    'the superseded payload. Not an error — a finding.';


-- ----------------------------------------------------------------------------
--  Every stored row is traceable to the fetch that produced it
--
--  NOT NULL is the point. A nullable column would make an unprovenanced row
--  representable, and a row that is merely *supposed* to carry provenance is
--  the same class of thing as a guard that is merely supposed to be checked.
--
--  Which fetch? The one whose payload the row was FIRST derived from. That is
--  well defined because every loader insert is ON CONFLICT DO NOTHING: a row is
--  written once, by one fetch, and re-ingests do not touch it. So the column
--  answers "where did this row come from", not "when did we last see it" — the
--  second question is answered by the fetch table, which keeps every retrieval.
-- ----------------------------------------------------------------------------
ALTER TABLE filer        ADD COLUMN source_fetch_id bigint NULL REFERENCES fetch_log (fetch_id);
ALTER TABLE filer_ticker ADD COLUMN source_fetch_id bigint NULL REFERENCES fetch_log (fetch_id);
ALTER TABLE filing       ADD COLUMN source_fetch_id bigint NULL REFERENCES fetch_log (fetch_id);


-- ----------------------------------------------------------------------------
--  The refusal to retrofit, executed rather than asserted
--
--  Columns are added NULL above so that this block can inspect what exists. If
--  any pre-existing row cannot be given a real fetch, the migration fails and
--  the transaction unwinds — nothing is half-applied, and no fabricated
--  provenance is written.
--
--  This is not defensive coding for a case we expect. It is the argument of
--  D16 §2.1 made executable: provenance is unretrofittable, so a migration that
--  encounters data it cannot provenance must stop rather than improvise.
-- ----------------------------------------------------------------------------
DO $$
DECLARE
    orphans bigint;
BEGIN
    SELECT
        (SELECT count(*) FROM filer        WHERE source_fetch_id IS NULL)
      + (SELECT count(*) FROM filer_ticker WHERE source_fetch_id IS NULL)
      + (SELECT count(*) FROM filing       WHERE source_fetch_id IS NULL)
    INTO orphans;

    IF orphans > 0 THEN
        RAISE EXCEPTION
            '0002 REFUSES TO BACKFILL: % row(s) exist that were loaded before '
            'provenance was recorded. A provenance row describes a fetch - its '
            'URL, its moment, and the hash of what came back - and once a fetch '
            'has happened unrecorded that record cannot be reconstructed. '
            'Re-fetching produces a NEW fetch, not evidence of the old one. '
            'Inventing a value here would put a fabricated fetch behind real '
            'data, indistinguishable from a real one forever after. '
            'Resolution: truncate the affected tables and re-ingest with '
            'provenance, or decide deliberately that this data is '
            'unprovenanced and record THAT.', orphans;
    END IF;
END $$;

-- Only reachable when every existing row carries provenance, which today means
-- there are no rows. From here on an unprovenanced row is not representable.
ALTER TABLE filer        ALTER COLUMN source_fetch_id SET NOT NULL;
ALTER TABLE filer_ticker ALTER COLUMN source_fetch_id SET NOT NULL;
ALTER TABLE filing       ALTER COLUMN source_fetch_id SET NOT NULL;

CREATE INDEX filer_source_fetch_idx        ON filer (source_fetch_id);
CREATE INDEX filer_ticker_source_fetch_idx ON filer_ticker (source_fetch_id);
CREATE INDEX filing_source_fetch_idx       ON filing (source_fetch_id);

COMMENT ON COLUMN filing.source_fetch_id IS
    'The fetch whose payload this row was first derived from. NOT NULL: an '
    'unprovenanced row is not representable.';
