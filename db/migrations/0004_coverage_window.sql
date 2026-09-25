-- ============================================================================
--  0004 — the coverage window, recorded as DATA
--
--  OPEN-51's condition, and it is a condition rather than a nicety:
--
--      "Coverage recorded as data — loaded quarters as rows with per-quarter
--       fact counts, and every validation states its window in its own output.
--       Without it a 2013 backtest against a 2015 store returns a well-formed
--       nearly-empty answer that looks like a result."
--
--  That is the whole argument. A backtest whose window is wrong does not fail;
--  it succeeds against less data and reports a number. The number is not
--  obviously wrong, it is quietly unfounded, and nothing in the output says so.
--
--  This does NOT weaken `store, don't filter`. The boundary recorded here is a
--  LOAD decision — which archives we retrieved — not a filter applied to data
--  we hold. Nothing in the fact store is excluded by it.
--
--  Why a table and not a derived count over `fact`: the two answer different
--  questions. A quarter that was loaded and legitimately contained no facts for
--  some filer is indistinguishable, from `fact` alone, from a quarter never
--  loaded at all. Absence of rows is not evidence of absence of data, and the
--  distinction is the entire point.
-- ============================================================================

CREATE TABLE coverage_quarter (
    -- The FSDS archive identifier, e.g. '2026q2'. Natural, stable, and what
    -- the SEC names the file.
    quarter             text        PRIMARY KEY,

    -- Provenance, like everything else that came from a retrieval.
    source_fetch_id     bigint      NOT NULL REFERENCES fetch_log (fetch_id),
    loaded_at           timestamptz NOT NULL DEFAULT now(),

    -- What the archive claimed, and what we did with it. These are counters of
    -- a LOAD, not of the store: re-loading the same quarter must leave them
    -- unchanged, which is why the loader writes them once per quarter.
    submissions_seen    integer     NOT NULL,
    facts_seen          bigint      NOT NULL,
    facts_loaded        bigint      NOT NULL,

    -- Refusals, counted rather than silent. Each is a chosen refusal with a
    -- register entry behind it; a refusal we cannot count is indistinguishable
    -- from a silence.
    refused_coreg       bigint      NOT NULL,  -- OPEN-39: per-fact entity unresolvable
    refused_malformed   bigint      NOT NULL,  -- unparseable segments / value / period
    -- A fact whose filing is not in the store. This is NOT malformed data: it
    -- is the two ruled sources disagreeing about which filings exist -
    -- `filing` comes from submissions.zip (ruling 5), facts come from FSDS.
    -- Folded into `refused_malformed` it would read as bad input from the SEC;
    -- counted separately it reads as what it is, a coverage gap between two
    -- archives, which is a finding about OUR load rather than about theirs.
    refused_unknown_filing bigint   NOT NULL DEFAULT 0,
    quarantined         bigint      NOT NULL,  -- OPEN-55: collisions that disagreed
    -- Exact duplicates: rows sharing 0001's key AND agreeing on value. One is
    -- stored and the rest collapse, which loses nothing - but it is neither a
    -- load nor a refusal, and without its own counter those rows simply go
    -- missing from the arithmetic.
    --
    -- This column exists because the CHECK below caught its absence on the
    -- loader's first real run: 11 facts seen, 10 accounted for. The category
    -- was invisible until the constraint refused the row.
    collapsed_duplicates bigint     NOT NULL DEFAULT 0,

    -- OPEN-48: filer extension tags are COUNTED AND REPORTED, never dropped.
    extension_facts     bigint      NOT NULL,

    CONSTRAINT coverage_quarter_shape   CHECK (quarter ~ '^[0-9]{4}q[1-4]$'),
    CONSTRAINT coverage_counts_sane     CHECK (
        submissions_seen >= 0 AND facts_seen >= 0 AND facts_loaded >= 0
        AND refused_coreg >= 0 AND refused_malformed >= 0
        AND refused_unknown_filing >= 0 AND collapsed_duplicates >= 0
        AND quarantined >= 0 AND extension_facts >= 0
    ),
    -- Every fact seen was loaded, refused, or quarantined. Nothing evaporates.
    -- This is the arithmetic that makes the counters an account rather than a
    -- set of unrelated numbers.
    CONSTRAINT coverage_accounts_for_every_fact CHECK (
        facts_seen = facts_loaded + refused_coreg + refused_malformed
                     + refused_unknown_filing + collapsed_duplicates
                     + quarantined
    )
);

COMMENT ON TABLE coverage_quarter IS
    'Which FSDS quarters were loaded, and what happened to every fact in them. '
    'OPEN-51: a validation whose window is wrong returns a well-formed answer '
    'against less data. The window must be stateable from the store itself.';

COMMENT ON CONSTRAINT coverage_accounts_for_every_fact ON coverage_quarter IS
    'Every fact seen was loaded, refused or quarantined. A counter set that '
    'does not add up is how a silent drop hides among honest refusals.';


-- ----------------------------------------------------------------------------
--  The window, as a single readable fact.
--
--  Exists so that "state your window in your own output" is one query rather
--  than an instruction people remember. An instruction that must be remembered
--  at every call site is not a control.
-- ----------------------------------------------------------------------------
CREATE VIEW coverage_window AS
SELECT
    min(quarter)                                   AS earliest_quarter,
    max(quarter)                                   AS latest_quarter,
    count(*)                                       AS quarters_loaded,
    sum(facts_loaded)                              AS facts_loaded,
    sum(quarantined)                               AS quarantined,
    sum(refused_coreg + refused_malformed
        + refused_unknown_filing)                  AS refused,
    sum(refused_unknown_filing)                    AS facts_without_a_filing,
    sum(collapsed_duplicates)                      AS collapsed_duplicates,
    -- A gap is not the same as a short window and must not look like one.
    -- Quarters between the bounds that were never loaded are the case a
    -- min/max pair silently misrepresents.
    (SELECT count(*) FROM (
        SELECT y || 'q' || q AS expected
        FROM generate_series(
                 (SELECT left(min(quarter), 4)::int FROM coverage_quarter),
                 (SELECT left(max(quarter), 4)::int FROM coverage_quarter)) AS y,
             generate_series(1, 4) AS q
        WHERE y || 'q' || q BETWEEN (SELECT min(quarter) FROM coverage_quarter)
                                AND (SELECT max(quarter) FROM coverage_quarter)
        EXCEPT
        SELECT quarter FROM coverage_quarter
     ) AS missing)                                 AS gaps
FROM coverage_quarter;

COMMENT ON VIEW coverage_window IS
    'The store''s coverage in one row, including GAPS. A min/max pair alone '
    'describes a contiguous window that may not exist.';
