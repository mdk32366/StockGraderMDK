-- ============================================================================
--  VERIFICATION FOR MIGRATION 0002 — D-021's required half
--
--  Every check RAISES on failure. No transaction control — the runner wraps
--  this in a savepoint and rolls back to it, so fixtures leave no trace and a
--  failed check takes the migration down with it.
-- ============================================================================

-- ----------------------------------------------------------------------------
--  PART A — structural
-- ----------------------------------------------------------------------------
DO $$
BEGIN
    -- A1: the fetch table and the change view exist.
    IF to_regclass('public.fetch_log') IS NULL THEN
        RAISE EXCEPTION 'A1 FAILED: fetch table absent';
    END IF;
    IF to_regclass('public.fetch_content_change') IS NULL THEN
        RAISE EXCEPTION 'A1 FAILED: fetch_content_change view absent';
    END IF;

    -- A2: the key is (url, retrieved_at). This is the structural expression of
    -- "a fetch is an event, not a property of a URL".
    IF NOT EXISTS (
        SELECT 1 FROM pg_constraint
        WHERE conname = 'fetch_log_one_per_moment'
          AND conrelid = 'public.fetch_log'::regclass AND contype = 'u'
    ) THEN
        RAISE EXCEPTION 'A2 FAILED: fetch_log_one_per_moment unique constraint absent';
    END IF;

    -- A3: and it MUST include retrieved_at. Without it the constraint collapses
    -- to (url) and a re-fetch can only be stored by overwriting — destroying
    -- the only evidence of when a payload changed.
    IF NOT EXISTS (
        SELECT 1 FROM pg_constraint c
        JOIN LATERAL unnest(c.conkey) AS k(attnum) ON TRUE
        JOIN pg_attribute a ON a.attrelid = c.conrelid AND a.attnum = k.attnum
        WHERE c.conname = 'fetch_log_one_per_moment'
          AND c.conrelid = 'public.fetch_log'::regclass
          AND a.attname = 'retrieved_at'
    ) THEN
        RAISE EXCEPTION 'A3 FAILED: fetch uniqueness does not include '
                        'retrieved_at - re-fetches would overwrite';
    END IF;

    -- A4: no uniqueness on url alone, and none on (url, sha256). The first
    -- destroys retrieval history; the second silently discards the evidence
    -- that a resource was still unchanged later. Stated as a check so a future
    -- migration adding the "obvious" key goes red.
    IF EXISTS (
        SELECT 1 FROM pg_constraint c
        WHERE c.conrelid = 'public.fetch_log'::regclass
          AND c.contype IN ('u','p')
          AND EXISTS (SELECT 1 FROM unnest(c.conkey) k(attnum)
                      JOIN pg_attribute a ON a.attrelid = c.conrelid AND a.attnum = k.attnum
                      WHERE a.attname = 'url')
          AND NOT EXISTS (SELECT 1 FROM unnest(c.conkey) k(attnum)
                      JOIN pg_attribute a ON a.attrelid = c.conrelid AND a.attnum = k.attnum
                      WHERE a.attname = 'retrieved_at')
    ) THEN
        RAISE EXCEPTION 'A4 FAILED: a uniqueness constraint covers url without '
                        'retrieved_at - repeated fetches cannot both be stored';
    END IF;

    -- A5: every stored table carries provenance, NOT NULL, with an FK.
    -- Nullable would make an unprovenanced row representable.
    IF EXISTS (
        SELECT 1 FROM unnest(ARRAY['filer','filer_ticker','filing']) AS t
        WHERE NOT EXISTS (
            SELECT 1 FROM pg_attribute
            WHERE attrelid = ('public.' || t)::regclass
              AND attname = 'source_fetch_id' AND attnotnull
        )
    ) THEN
        RAISE EXCEPTION 'A5 FAILED: source_fetch_id is missing or nullable on at '
                        'least one table - an unprovenanced row is representable';
    END IF;

    IF (SELECT count(*) FROM pg_constraint
        WHERE contype = 'f' AND confrelid = 'public.fetch_log'::regclass) < 3 THEN
        RAISE EXCEPTION 'A6 FAILED: fewer than three foreign keys reference fetch';
    END IF;

    RAISE NOTICE 'PART A passed: fetch is keyed on the event, and provenance is mandatory.';
END $$;


-- ----------------------------------------------------------------------------
--  Fixtures. One URL fetched three times: twice identical, once changed.
-- ----------------------------------------------------------------------------
INSERT INTO fetch_log (url, retrieved_at, sha256, content_bytes) VALUES
    ('https://data.sec.gov/submissions/CIK0000320193.json',
     TIMESTAMPTZ '2026-09-23 10:00:00+00', repeat('a', 64), 164033),
    -- Same URL, SAME payload, later. Not a duplicate: evidence the resource was
    -- still unchanged at 11:00.
    ('https://data.sec.gov/submissions/CIK0000320193.json',
     TIMESTAMPTZ '2026-09-23 11:00:00+00', repeat('a', 64), 164033),
    -- Same URL, DIFFERENT payload. THE FINDING.
    ('https://data.sec.gov/submissions/CIK0000320193.json',
     TIMESTAMPTZ '2026-09-24 06:00:00+00', repeat('b', 64), 164999),
    -- An unrelated URL, fetched once, to prove the view does not flag it.
    ('https://www.sec.gov/files/company_tickers.json',
     TIMESTAMPTZ '2026-09-23 10:00:00+00', repeat('c', 64), 800821);

INSERT INTO filer (cik, current_name, current_sic, metadata_as_of, source_fetch_id)
SELECT 999000001, 'Synthetic Alpha Corp', '3711', DATE '2026-09-23', fetch_id
FROM fetch_log WHERE retrieved_at = TIMESTAMPTZ '2026-09-23 10:00:00+00'
  AND url LIKE '%CIK0000320193%';


-- ----------------------------------------------------------------------------
--  PART B — behavioural. The two cases D16 §2.5 asks about.
-- ----------------------------------------------------------------------------
DO $$
DECLARE
    n integer;
    payloads integer;
BEGIN
    -- B1 — SAME URL, SAME CONTENT, TWICE: two rows, and NOT a finding.
    -- A second identical fetch is a second observation. Collapsing it would
    -- discard the fact that the resource was still unchanged an hour later.
    SELECT count(*) INTO n FROM fetch_log
    WHERE url LIKE '%CIK0000320193%' AND sha256 = repeat('a', 64);
    IF n <> 2 THEN
        RAISE EXCEPTION 'B1 FAILED: two identical fetches stored as % row(s), '
                        'expected 2. Collapsing them discards the evidence that '
                        'the payload was unchanged at the later moment.', n;
    END IF;

    -- B2 — SAME URL, DIFFERENT CONTENT: this IS the finding, and it must be
    -- visible without anybody going looking for it.
    SELECT count(*) INTO n FROM fetch_content_change
    WHERE url LIKE '%CIK0000320193%';
    IF n <> 1 THEN
        RAISE EXCEPTION 'B2 FAILED: a URL with two distinct payloads is not '
                        'surfaced by fetch_content_change (% rows)', n;
    END IF;

    SELECT distinct_payloads INTO payloads FROM fetch_content_change
    WHERE url LIKE '%CIK0000320193%';
    IF payloads <> 2 THEN
        RAISE EXCEPTION 'B2 FAILED: expected 2 distinct payloads, found %', payloads;
    END IF;

    -- B3 — and a URL fetched once, or fetched repeatedly WITHOUT changing, must
    -- NOT appear. A change detector that flags everything detects nothing.
    IF EXISTS (SELECT 1 FROM fetch_content_change WHERE url LIKE '%company_tickers%') THEN
        RAISE EXCEPTION 'B3 FAILED: an unchanged URL was reported as changed';
    END IF;

    -- B4 — a stored row resolves to the fetch it came from, and to that fetch's
    -- hash. This is the traceability D16 §2.5 asks for, exercised rather than
    -- asserted by the NOT NULL.
    SELECT count(*) INTO n
    FROM filer f JOIN fetch_log x ON x.fetch_id = f.source_fetch_id
    WHERE f.cik = 999000001
      AND x.sha256 = repeat('a', 64)
      AND x.retrieved_at = TIMESTAMPTZ '2026-09-23 10:00:00+00';
    IF n <> 1 THEN
        RAISE EXCEPTION 'B4 FAILED: the filer row does not trace to the fetch '
                        'that produced it';
    END IF;

    RAISE NOTICE 'PART B passed: identical re-fetch is not a finding, a changed payload is.';
END $$;


-- ----------------------------------------------------------------------------
--  PART C — the refusals.
-- ----------------------------------------------------------------------------
DO $$
DECLARE
    refused boolean;
BEGIN
    -- C1: a row with no provenance must be REFUSED. This is the property the
    -- whole migration exists to establish.
    refused := FALSE;
    BEGIN
        INSERT INTO filer (cik, current_name, metadata_as_of, source_fetch_id)
        VALUES (999000002, 'No Provenance Inc', DATE '2026-09-23', NULL);
    EXCEPTION WHEN not_null_violation THEN
        refused := TRUE;
    END;
    IF NOT refused THEN
        RAISE EXCEPTION 'C1 FAILED: a row with no provenance was ACCEPTED';
    END IF;

    -- C2: a row pointing at a fetch that does not exist must be REFUSED.
    -- Provenance that references nothing is worse than none, because it looks
    -- like provenance.
    refused := FALSE;
    BEGIN
        INSERT INTO filer (cik, current_name, metadata_as_of, source_fetch_id)
        VALUES (999000003, 'Dangling Ref Ltd', DATE '2026-09-23', 987654321);
    EXCEPTION WHEN foreign_key_violation THEN
        refused := TRUE;
    END;
    IF NOT refused THEN
        RAISE EXCEPTION 'C2 FAILED: a row referencing a non-existent fetch was ACCEPTED';
    END IF;

    -- C3: the same URL cannot be recorded twice at the same instant. Two
    -- fetches at the identical microsecond is a double-write, not an event.
    refused := FALSE;
    BEGIN
        INSERT INTO fetch_log (url, retrieved_at, sha256)
        VALUES ('https://data.sec.gov/submissions/CIK0000320193.json',
                TIMESTAMPTZ '2026-09-23 10:00:00+00', repeat('d', 64));
    EXCEPTION WHEN unique_violation THEN
        refused := TRUE;
    END;
    IF NOT refused THEN
        RAISE EXCEPTION 'C3 FAILED: the same URL was recorded twice at one instant';
    END IF;

    -- C4: a malformed hash must be REFUSED. A truncated or non-hex digest
    -- compares unequal to everything and would read as a permanent change.
    refused := FALSE;
    BEGIN
        INSERT INTO fetch_log (url, retrieved_at, sha256)
        VALUES ('https://example.invalid/x', now(), 'not-a-sha256');
    EXCEPTION WHEN check_violation THEN
        refused := TRUE;
    END;
    IF NOT refused THEN
        RAISE EXCEPTION 'C4 FAILED: a malformed sha256 was ACCEPTED';
    END IF;

    RAISE NOTICE 'PART C passed: every guard refused what it should refuse.';
END $$;
