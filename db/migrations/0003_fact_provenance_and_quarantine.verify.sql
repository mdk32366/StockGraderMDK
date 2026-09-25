-- ============================================================================
--  VERIFICATION FOR MIGRATION 0003
--
--  Every check RAISES on failure. No transaction control — the runner wraps this
--  in a savepoint and rolls back to it.
--
--  THE CENTRAL CHECK IS A5-INVERTED (§A2 below). 0002's A5 enumerated three
--  table names and passed while every fact row was unprovenanced. This one
--  derives its check set from the catalogue and subtracts a declared exclusion
--  list, so a table added in a later migration is checked unless somebody
--  deliberately exempts it.
-- ============================================================================

-- ----------------------------------------------------------------------------
--  PART A — structural
-- ----------------------------------------------------------------------------
DO $$
DECLARE
    missing text;
    extra   text;
BEGIN
    -- A1: the new objects exist.
    IF to_regclass('public.fact_collision') IS NULL THEN
        RAISE EXCEPTION 'A1 FAILED: fact_collision table absent';
    END IF;
    IF to_regclass('public.provenance_exempt') IS NULL THEN
        RAISE EXCEPTION 'A1 FAILED: provenance_exempt table absent';
    END IF;
    IF to_regclass('public.fact_collision_rate') IS NULL THEN
        RAISE EXCEPTION 'A1 FAILED: fact_collision_rate view absent';
    END IF;

    -- ========================================================================
    -- A2 — THE INVERTED CHECK. Derived from the catalogue, not enumerated.
    --
    -- Every ordinary table in public must carry source_fetch_id NOT NULL,
    -- EXCEPT those declared in provenance_exempt.
    --
    -- 0002's A5 listed {filer, filer_ticker, filing} and therefore could not
    -- see `fact`. This cannot have that blind spot: a table added later is in
    -- the check set by default, and the only way out is a visible row with a
    -- reason attached.
    -- ========================================================================
    SELECT string_agg(c.relname, ', ' ORDER BY c.relname) INTO missing
    FROM pg_class c
    JOIN pg_namespace n ON n.oid = c.relnamespace
    WHERE n.nspname = 'public'
      AND c.relkind = 'r'
      AND c.relname NOT IN (SELECT table_name FROM provenance_exempt)
      AND NOT EXISTS (
          SELECT 1 FROM pg_attribute a
          WHERE a.attrelid = c.oid
            AND a.attname = 'source_fetch_id'
            AND a.attnotnull
            AND NOT a.attisdropped
      );

    IF missing IS NOT NULL THEN
        RAISE EXCEPTION
            'A2 FAILED: table(s) carry no source_fetch_id NOT NULL and are not '
            'declared in provenance_exempt: %. Either give the table provenance '
            'or exempt it with a reason. This check is derived from the '
            'catalogue precisely so that a new table cannot be silently '
            'unchecked, which is how 0002 missed `fact`.', missing;
    END IF;

    -- A3: the exclusion list must not name tables that do not exist. A stale
    -- exemption is a hole that opens if the name is ever reused.
    SELECT string_agg(table_name, ', ' ORDER BY table_name) INTO extra
    FROM provenance_exempt
    WHERE to_regclass('public.' || table_name) IS NULL;
    IF extra IS NOT NULL THEN
        RAISE EXCEPTION 'A3 FAILED: provenance_exempt names non-existent '
                        'table(s): %. A stale exemption pre-authorises a future '
                        'table that happens to reuse the name.', extra;
    END IF;

    -- A4: `fact` specifically. Named as well as derived, because it is the
    -- table 0002 missed and the regression worth naming out loud.
    IF NOT EXISTS (
        SELECT 1 FROM pg_attribute
        WHERE attrelid = 'public.fact'::regclass
          AND attname = 'source_fetch_id' AND attnotnull
    ) THEN
        RAISE EXCEPTION 'A4 FAILED: fact.source_fetch_id is missing or nullable '
                        '- this is the exact defect 0003 exists to fix';
    END IF;

    -- A5: fact_collision must NOT carry a unique constraint on the colliding
    -- key. The point of the table is that these rows collide; uniqueness here
    -- would refuse the second one and reproduce the loss inside the quarantine.
    IF EXISTS (
        SELECT 1 FROM pg_constraint c
        WHERE c.conrelid = 'public.fact_collision'::regclass
          AND c.contype IN ('u','p')
          AND EXISTS (SELECT 1 FROM unnest(c.conkey) k(attnum)
                      JOIN pg_attribute a ON a.attrelid=c.conrelid AND a.attnum=k.attnum
                      WHERE a.attname = 'concept')
    ) THEN
        RAISE EXCEPTION 'A5 FAILED: fact_collision has a uniqueness constraint '
                        'covering concept - quarantined rows collide by '
                        'definition and would be refused';
    END IF;

    -- A6: fact_one_per_filing is untouched. D23 §3.3 - the key is not weakened
    -- to accommodate collisions.
    IF NOT EXISTS (
        SELECT 1 FROM pg_constraint
        WHERE conname = 'fact_one_per_filing'
          AND conrelid = 'public.fact'::regclass AND contype = 'u'
    ) THEN
        RAISE EXCEPTION 'A6 FAILED: fact_one_per_filing is absent - 0003 must '
                        'not weaken the key to admit colliding rows';
    END IF;

    RAISE NOTICE 'PART A passed: provenance is derived-and-excluded, not enumerated.';
END $$;


-- ----------------------------------------------------------------------------
--  Fixtures
-- ----------------------------------------------------------------------------
INSERT INTO fetch_log (url, retrieved_at, sha256, content_bytes) VALUES
    ('https://www.sec.gov/files/dera/data/financial-statement-data-sets/2026q2.zip',
     TIMESTAMPTZ '2026-09-25 06:00:00+00', repeat('e', 64), 60419016);

INSERT INTO filer (cik, current_name, metadata_as_of, source_fetch_id)
SELECT 999000001, 'Synthetic Alpha Corp', DATE '2026-09-25', fetch_id
FROM fetch_log WHERE sha256 = repeat('e', 64);

INSERT INTO filing (accession, cik, form_type, filing_date, is_amendment, source_fetch_id)
SELECT '9990000001-26-000001', 999000001, '10-Q', DATE '2026-05-01', FALSE, fetch_id
FROM fetch_log WHERE sha256 = repeat('e', 64);

-- Two competing assertions of ONE fact. This is the 31-of-32 case.
INSERT INTO fact_collision (accession, entity_cik, concept, taxonomy, unit,
                            period_type, period_start, period_end, dimensions,
                            value, source_ordinal, source_fetch_id)
SELECT '9990000001-26-000001', 999000001, 'DerivativeAssetFairValueGrossLiability',
       'us-gaap/2025', 'USD', 'instant', DATE '2026-03-31', DATE '2026-03-31',
       '{}'::jsonb, v, o, fetch_id
FROM fetch_log, (VALUES (-3123000, 1), (706000, 2)) AS t(v, o)
WHERE sha256 = repeat('e', 64);


-- ----------------------------------------------------------------------------
--  PART B — behavioural
-- ----------------------------------------------------------------------------
DO $$
DECLARE
    n integer;
BEGIN
    -- B1 — BOTH competing values survive. If this returns 1, the quarantine has
    -- reproduced the very loss it exists to prevent.
    SELECT count(*) INTO n FROM fact_collision
    WHERE accession = '9990000001-26-000001'
      AND concept = 'DerivativeAssetFairValueGrossLiability';
    IF n <> 2 THEN
        RAISE EXCEPTION 'B1 FAILED: expected 2 competing assertions in '
                        'quarantine, found %. A value of 1 means one was '
                        'discarded - the silent loss this table prevents.', n;
    END IF;

    -- B2 — and they are distinguishable by value, not merely counted.
    IF NOT EXISTS (SELECT 1 FROM fact_collision WHERE value = -3123000)
       OR NOT EXISTS (SELECT 1 FROM fact_collision WHERE value = 706000) THEN
        RAISE EXCEPTION 'B2 FAILED: the two disagreeing values are not both '
                        'retrievable';
    END IF;

    -- B3 — the rate view surfaces them against the fetch, so a jump is visible.
    SELECT quarantined_rows INTO n FROM fact_collision_rate
    WHERE retrieved_at = TIMESTAMPTZ '2026-09-25 06:00:00+00';
    IF n <> 2 THEN
        RAISE EXCEPTION 'B3 FAILED: fact_collision_rate reports % quarantined '
                        'rows for that fetch, expected 2', n;
    END IF;

    -- B4 — quarantined rows trace to the fetch that produced them, like
    -- everything else in the store.
    SELECT count(*) INTO n
    FROM fact_collision c JOIN fetch_log x ON x.fetch_id = c.source_fetch_id
    WHERE x.sha256 = repeat('e', 64);
    IF n <> 2 THEN
        RAISE EXCEPTION 'B4 FAILED: quarantined rows do not trace to their fetch';
    END IF;

    RAISE NOTICE 'PART B passed: both competing assertions survive and are traceable.';
END $$;


-- ----------------------------------------------------------------------------
--  PART C — the refusals
-- ----------------------------------------------------------------------------
DO $$
DECLARE
    refused boolean;
BEGIN
    -- C1: an unprovenanced FACT must be refused. The defect 0003 fixes.
    refused := FALSE;
    BEGIN
        INSERT INTO fact (accession, entity_cik, concept, unit, period_type,
                          period_start, period_end, value)
        VALUES ('9990000001-26-000001', 999000001, 'Revenues', 'USD', 'duration',
                DATE '2026-01-01', DATE '2026-03-31', 1);
    EXCEPTION WHEN not_null_violation THEN
        refused := TRUE;
    END;
    IF NOT refused THEN
        RAISE EXCEPTION 'C1 FAILED: an unprovenanced fact was ACCEPTED';
    END IF;

    -- C2: an exemption with no substantive reason must be refused. A bare name
    -- is what turns the exclusion list into a place to hide a table.
    refused := FALSE;
    BEGIN
        INSERT INTO provenance_exempt (table_name, reason) VALUES ('fact', 'x');
    EXCEPTION WHEN check_violation THEN
        refused := TRUE;
    END;
    IF NOT refused THEN
        RAISE EXCEPTION 'C2 FAILED: an exemption with a trivial reason was ACCEPTED';
    END IF;

    -- C3: a quarantined row with no provenance must be refused too. The
    -- quarantine is not a place where the rules relax.
    refused := FALSE;
    BEGIN
        INSERT INTO fact_collision (accession, entity_cik, concept, taxonomy, unit,
                                    period_type, period_start, period_end,
                                    dimensions, value)
        VALUES ('9990000001-26-000001', 999000001, 'Revenues', 'us-gaap/2025',
                'USD', 'instant', DATE '2026-03-31', DATE '2026-03-31',
                '{}'::jsonb, 1);
    EXCEPTION WHEN not_null_violation THEN
        refused := TRUE;
    END;
    IF NOT refused THEN
        RAISE EXCEPTION 'C3 FAILED: an unprovenanced quarantine row was ACCEPTED';
    END IF;

    RAISE NOTICE 'PART C passed: every guard refused what it should refuse.';
END $$;
