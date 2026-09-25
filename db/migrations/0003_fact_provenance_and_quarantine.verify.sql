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
    SELECT string_agg(n.nspname || '.' || c.relname, ', '
                      ORDER BY n.nspname, c.relname) INTO missing
    FROM pg_class c
    JOIN pg_namespace n ON n.oid = c.relnamespace
    WHERE n.nspname NOT IN ('pg_catalog', 'information_schema')
      AND n.nspname NOT LIKE 'pg\_%'
      AND c.relkind = 'r'
      AND NOT EXISTS (
          SELECT 1 FROM provenance_exempt e
          WHERE e.schema_name = n.nspname AND e.table_name = c.relname
      )
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

    -- A5: fact_collision must NOT carry a unique constraint that would refuse
    -- a second, DISAGREEING assertion. The point of the table is that these
    -- rows collide; such a constraint would reproduce the loss inside the
    -- quarantine built to prevent it.
    --
    -- REFINED for OPEN-59. This check previously failed on any uniqueness
    -- touching `concept`. That was a PROXY for the property, and the proxy and
    -- the property diverge at exactly one point: a constraint that INCLUDES
    -- `value` cannot refuse a differing value, because differing values differ
    -- in the key. The old wording would have rejected the correct fix to
    -- OPEN-59 while permitting nothing safer.
    --
    -- So the test is now the property itself: uniqueness over the colliding key
    -- is forbidden UNLESS `value` is part of it.
    IF EXISTS (
        SELECT 1 FROM pg_constraint c
        WHERE c.conrelid = 'public.fact_collision'::regclass
          AND c.contype IN ('u','p')
          AND EXISTS (SELECT 1 FROM unnest(c.conkey) k(attnum)
                      JOIN pg_attribute a ON a.attrelid=c.conrelid AND a.attnum=k.attnum
                      WHERE a.attname = 'concept')
          AND NOT EXISTS (SELECT 1 FROM unnest(c.conkey) k(attnum)
                      JOIN pg_attribute a ON a.attrelid=c.conrelid AND a.attnum=k.attnum
                      WHERE a.attname = 'value')
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
--  PART B (continued) — OPEN-59 and OPEN-60, proven rather than asserted
-- ----------------------------------------------------------------------------
DO $$
DECLARE
    before_n integer;
    after_n  integer;
    old_scope integer;
    new_scope integer;
    n        integer;
BEGIN
    -- ========================================================================
    -- B5 — OPEN-59. Re-ingesting the same archive leaves the table UNCHANGED.
    --
    -- The re-ingest is given a DIFFERENT fetch, because that is what a second
    -- ingest actually is: fetch_log is keyed on (url, retrieved_at), so the
    -- same archive fetched again is a new row with a new fetch_id. A constraint
    -- that included source_fetch_id would make every re-ingested row unique
    -- again and would pass this test while fixing nothing.
    -- ========================================================================
    INSERT INTO fetch_log (url, retrieved_at, sha256, content_bytes)
    VALUES ('https://example.invalid/fsds/2026q1.zip',
            TIMESTAMPTZ '2026-09-26 06:00:00+00', repeat('e', 64), 1024);

    SELECT count(*) INTO before_n FROM fact_collision;

    INSERT INTO fact_collision (accession, entity_cik, concept, taxonomy, unit,
                                period_type, period_start, period_end, dimensions,
                                value, source_ordinal, source_fetch_id)
    SELECT '9990000001-26-000001', 999000001, 'DerivativeAssetFairValueGrossLiability',
           'us-gaap/2025', 'USD', 'instant', DATE '2026-03-31', DATE '2026-03-31',
           '{}'::jsonb, v, o, fetch_id
    FROM fetch_log, (VALUES (-3123000, 1), (706000, 2)) AS t(v, o)
    WHERE retrieved_at = TIMESTAMPTZ '2026-09-26 06:00:00+00'
    ON CONFLICT ON CONSTRAINT fact_collision_one_per_source_row DO NOTHING;

    SELECT count(*) INTO after_n FROM fact_collision;

    IF after_n <> before_n THEN
        RAISE EXCEPTION 'B5 FAILED: re-ingesting the same archive changed '
                        'fact_collision from % to % rows. A load that is '
                        'idempotent everywhere except in the table recording '
                        'its refusals is not idempotent.', before_n, after_n;
    END IF;

    -- B5b — and the surviving rows still hold BOTH competing values. An
    -- idempotency fix that achieved stability by discarding one of them would
    -- pass B5 and destroy the table's entire purpose.
    IF NOT EXISTS (SELECT 1 FROM fact_collision WHERE value = -3123000)
       OR NOT EXISTS (SELECT 1 FROM fact_collision WHERE value = 706000) THEN
        RAISE EXCEPTION 'B5b FAILED: idempotency was achieved by losing a '
                        'competing value';
    END IF;

    -- ========================================================================
    -- B6 — the shape the Planner named as the one that would break it:
    -- three rows collide and TWO OF THEM AGREE on value.
    --
    -- Keyed on the colliding key plus value alone, the two agreeing rows
    -- collapse to one and the archive's second assertion of 7000 is silently
    -- discarded. source_ordinal is in the key precisely to prevent that.
    -- ========================================================================
    INSERT INTO fact_collision (accession, entity_cik, concept, taxonomy, unit,
                                period_type, period_start, period_end, dimensions,
                                value, source_ordinal, source_fetch_id)
    SELECT '9990000001-26-000001', 999000001, 'ThreeWayCollisionProbe',
           'us-gaap/2025', 'USD', 'instant', DATE '2026-03-31', DATE '2026-03-31',
           '{}'::jsonb, v, o, fetch_id
    FROM fetch_log, (VALUES (5000, 10), (7000, 11), (7000, 12)) AS t(v, o)
    WHERE retrieved_at = TIMESTAMPTZ '2026-09-25 06:00:00+00'
    ON CONFLICT ON CONSTRAINT fact_collision_one_per_source_row DO NOTHING;

    SELECT count(*) INTO n FROM fact_collision
    WHERE concept = 'ThreeWayCollisionProbe';
    IF n <> 3 THEN
        RAISE EXCEPTION 'B6 FAILED: three colliding rows with two agreeing on '
                        'value produced % rows, expected 3. A value of 2 means '
                        'the duplicate assertion was collapsed away.', n;
    END IF;

    -- B6b — and re-ingesting that shape is still stable.
    INSERT INTO fact_collision (accession, entity_cik, concept, taxonomy, unit,
                                period_type, period_start, period_end, dimensions,
                                value, source_ordinal, source_fetch_id)
    SELECT '9990000001-26-000001', 999000001, 'ThreeWayCollisionProbe',
           'us-gaap/2025', 'USD', 'instant', DATE '2026-03-31', DATE '2026-03-31',
           '{}'::jsonb, v, o, fetch_id
    FROM fetch_log, (VALUES (5000, 10), (7000, 11), (7000, 12)) AS t(v, o)
    WHERE retrieved_at = TIMESTAMPTZ '2026-09-26 06:00:00+00'
    ON CONFLICT ON CONSTRAINT fact_collision_one_per_source_row DO NOTHING;

    SELECT count(*) INTO n FROM fact_collision
    WHERE concept = 'ThreeWayCollisionProbe';
    IF n <> 3 THEN
        RAISE EXCEPTION 'B6b FAILED: re-ingesting the three-way collision gave '
                        '% rows, expected 3', n;
    END IF;

    -- ========================================================================
    -- B7 — OPEN-60, PROVEN SIDE BY SIDE, the way A2 was proven against A5.
    --
    -- A table outside `public` with no provenance. The old public-only scope
    -- passes blind to it; the schema-wide scope fires. Same database, same
    -- moment, two queries -- a measurement rather than an argument.
    -- ========================================================================
    CREATE SCHEMA verify_open60;
    CREATE TABLE verify_open60.staging_facts (id bigint, value numeric);

    -- The OLD scope: public only.
    SELECT count(*) INTO old_scope
    FROM pg_class c JOIN pg_namespace n ON n.oid = c.relnamespace
    WHERE n.nspname = 'public'
      AND c.relkind = 'r'
      AND c.relname = 'staging_facts'
      AND NOT EXISTS (
          SELECT 1 FROM pg_attribute a
          WHERE a.attrelid = c.oid AND a.attname = 'source_fetch_id'
            AND a.attnotnull AND NOT a.attisdropped);

    -- The NEW scope: every non-system schema.
    SELECT count(*) INTO new_scope
    FROM pg_class c JOIN pg_namespace n ON n.oid = c.relnamespace
    WHERE n.nspname NOT IN ('pg_catalog', 'information_schema')
      AND n.nspname NOT LIKE 'pg\_%'
      AND c.relkind = 'r'
      AND c.relname = 'staging_facts'
      AND NOT EXISTS (
          SELECT 1 FROM provenance_exempt e
          WHERE e.schema_name = n.nspname AND e.table_name = c.relname)
      AND NOT EXISTS (
          SELECT 1 FROM pg_attribute a
          WHERE a.attrelid = c.oid AND a.attname = 'source_fetch_id'
            AND a.attnotnull AND NOT a.attisdropped);

    IF old_scope <> 0 THEN
        RAISE EXCEPTION 'B7 FAILED: the public-only scope was expected to be '
                        'blind to a table in another schema, but saw % - the '
                        'probe is not measuring what it claims', old_scope;
    END IF;
    IF new_scope <> 1 THEN
        RAISE EXCEPTION 'B7 FAILED: the schema-wide scope did not catch an '
                        'unprovenanced table outside public (found %). A2 '
                        'still enumerates a schema rather than checking the '
                        'database.', new_scope;
    END IF;

    -- B7b — the exemption is schema-qualified: exempting public.staging_facts
    -- must NOT exempt verify_open60.staging_facts.
    INSERT INTO provenance_exempt (schema_name, table_name, reason)
    VALUES ('public', 'staging_facts',
            'Probe row for B7b. Exempts the public table only, and must not '
            'reach the identically named table in another schema.');

    SELECT count(*) INTO new_scope
    FROM pg_class c JOIN pg_namespace n ON n.oid = c.relnamespace
    WHERE n.nspname NOT IN ('pg_catalog', 'information_schema')
      AND n.nspname NOT LIKE 'pg\_%'
      AND c.relkind = 'r'
      AND c.relname = 'staging_facts'
      AND NOT EXISTS (
          SELECT 1 FROM provenance_exempt e
          WHERE e.schema_name = n.nspname AND e.table_name = c.relname)
      AND NOT EXISTS (
          SELECT 1 FROM pg_attribute a
          WHERE a.attrelid = c.oid AND a.attname = 'source_fetch_id'
            AND a.attnotnull AND NOT a.attisdropped);

    IF new_scope <> 1 THEN
        RAISE EXCEPTION 'B7b FAILED: an exemption naming public.staging_facts '
                        'silenced the check for a DIFFERENT table of the same '
                        'name in another schema. That is the hole OPEN-60 '
                        'described, moved rather than closed.';
    END IF;

    DROP TABLE verify_open60.staging_facts;
    DROP SCHEMA verify_open60;
    DELETE FROM provenance_exempt WHERE table_name = 'staging_facts';

    RAISE NOTICE 'PART B (continued) passed: re-ingest is stable, the '
                 'three-way collision survives, and the provenance check '
                 'reaches outside public.';
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
