-- ============================================================================
--  0004 verification
--
--  The check worth reading is B3. A min/max pair over loaded quarters describes
--  a window that may have holes in it, and a holed window reads exactly like a
--  short one. That is OPEN-51's failure mode arriving through the instrument
--  built to prevent it.
-- ============================================================================

-- ----------------------------------------------------------------------------
--  PART A — structural
-- ----------------------------------------------------------------------------
DO $$
BEGIN
    IF to_regclass('public.coverage_quarter') IS NULL THEN
        RAISE EXCEPTION 'A1 FAILED: coverage_quarter absent';
    END IF;
    IF to_regclass('public.coverage_window') IS NULL THEN
        RAISE EXCEPTION 'A1 FAILED: coverage_window view absent';
    END IF;

    -- A2 — this table must satisfy 0003's derived provenance rule. Stated here
    -- as well as inherited, because 0004 is the FIRST migration written after
    -- the inversion and is therefore the first real test of it: a new table
    -- arriving in a later migration is in the check set by default.
    IF NOT EXISTS (
        SELECT 1 FROM pg_attribute
        WHERE attrelid = 'public.coverage_quarter'::regclass
          AND attname = 'source_fetch_id' AND attnotnull
    ) THEN
        RAISE EXCEPTION 'A2 FAILED: coverage_quarter.source_fetch_id missing or '
                        'nullable - and 0003 A2 should already have refused this';
    END IF;

    RAISE NOTICE 'PART A passed: coverage objects exist and are provenanced.';
END $$;


-- ----------------------------------------------------------------------------
--  Fixtures
-- ----------------------------------------------------------------------------
INSERT INTO fetch_log (url, retrieved_at, sha256, content_bytes)
VALUES ('https://example.invalid/fsds/cov.zip',
        TIMESTAMPTZ '2026-09-25 07:00:00+00', repeat('c', 64), 2048);

-- Deliberately NOT contiguous: 2015q1, 2015q2, then a hole at q3, then q4.
INSERT INTO coverage_quarter (quarter, source_fetch_id, submissions_seen,
                              facts_seen, facts_loaded, refused_coreg,
                              refused_malformed, refused_unknown_filing,
                              collapsed_duplicates, quarantined, extension_facts)
SELECT q, fetch_id, 100, 1000, 880, 60, 10, 5, 15, 30, 75
FROM fetch_log, (VALUES ('2015q1'), ('2015q2'), ('2015q4')) AS t(q)
WHERE sha256 = repeat('c', 64);


-- ----------------------------------------------------------------------------
--  PART B — behavioural
-- ----------------------------------------------------------------------------
DO $$
DECLARE
    n integer;
    txt text;
BEGIN
    -- B1 — the window is stateable from the store, which is OPEN-51's point.
    SELECT earliest_quarter || '..' || latest_quarter INTO txt FROM coverage_window;
    IF txt <> '2015q1..2015q4' THEN
        RAISE EXCEPTION 'B1 FAILED: coverage_window reported %, expected '
                        '2015q1..2015q4', txt;
    END IF;

    -- B2 — the counters are an account, not a set of unrelated numbers.
    SELECT facts_loaded INTO n FROM coverage_window;
    IF n <> 2640 THEN
        RAISE EXCEPTION 'B2 FAILED: facts_loaded aggregated to %, expected 2640', n;
    END IF;

    -- ========================================================================
    -- B3 — THE CHECK THIS MIGRATION EXISTS FOR.
    --
    -- 2015q3 was never loaded. min/max says 2015q1..2015q4, which reads as a
    -- full year. A backtest over 2015q3 would return a well-formed empty
    -- answer and nothing in the window would contradict it.
    -- ========================================================================
    SELECT gaps INTO n FROM coverage_window;
    IF n <> 1 THEN
        RAISE EXCEPTION 'B3 FAILED: coverage_window reported % gaps, expected 1. '
                        'A holed window is indistinguishable from a short one, '
                        'which is the exact failure OPEN-51 names.', n;
    END IF;

    RAISE NOTICE 'PART B passed: the window is stateable and its gaps are visible.';
END $$;


-- ----------------------------------------------------------------------------
--  PART C — the refusals
-- ----------------------------------------------------------------------------
DO $$
DECLARE
    refused boolean;
BEGIN
    -- C1 — counters that do not add up are refused. A load that dropped rows
    -- silently would have to produce a set that fails this to be recorded.
    refused := FALSE;
    BEGIN
        INSERT INTO coverage_quarter (quarter, source_fetch_id, submissions_seen,
                                      facts_seen, facts_loaded, refused_coreg,
                                      refused_malformed, quarantined,
                                      extension_facts)
        SELECT '2016q1', fetch_id, 10, 1000, 900, 0, 0, 0, 0
        FROM fetch_log WHERE sha256 = repeat('c', 64);
    EXCEPTION WHEN check_violation THEN
        refused := TRUE;
    END;
    IF NOT refused THEN
        RAISE EXCEPTION 'C1 FAILED: a quarter claiming 1000 facts seen and only '
                        '900 accounted for was accepted. 100 rows would have '
                        'vanished with the store reporting no refusals.';
    END IF;

    -- C2 — an unprovenanced coverage row is not representable.
    refused := FALSE;
    BEGIN
        INSERT INTO coverage_quarter (quarter, source_fetch_id, submissions_seen,
                                      facts_seen, facts_loaded, refused_coreg,
                                      refused_malformed, quarantined,
                                      extension_facts)
        VALUES ('2016q2', NULL, 10, 100, 100, 0, 0, 0, 0);
    EXCEPTION WHEN not_null_violation THEN
        refused := TRUE;
    END;
    IF NOT refused THEN
        RAISE EXCEPTION 'C2 FAILED: coverage recorded without provenance';
    END IF;

    -- C3 — a malformed quarter identifier is refused rather than stored.
    refused := FALSE;
    BEGIN
        INSERT INTO coverage_quarter (quarter, source_fetch_id, submissions_seen,
                                      facts_seen, facts_loaded, refused_coreg,
                                      refused_malformed, quarantined,
                                      extension_facts)
        SELECT 'Q1-2016', fetch_id, 10, 100, 100, 0, 0, 0, 0
        FROM fetch_log WHERE sha256 = repeat('c', 64);
    EXCEPTION WHEN check_violation THEN
        refused := TRUE;
    END;
    IF NOT refused THEN
        RAISE EXCEPTION 'C3 FAILED: a malformed quarter identifier was stored';
    END IF;

    RAISE NOTICE 'PART C passed: unaccounted, unprovenanced and malformed '
                 'coverage rows are all refused.';
END $$;
