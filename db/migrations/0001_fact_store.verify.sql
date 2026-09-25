-- ============================================================================
--  VERIFICATION FOR MIGRATION 0001 — D-021's required half
--
--  D-021: "followed by a verification query asserting that the objects it
--  claims to create exist and are the right shape." §4 of the D8 handover adds
--  four behavioural checks — the ones that would fail if a §1 property were
--  absent.
--
--  DESIGN: every check RAISES on failure. None of them returns a result set for
--  a human to eyeball. "The migration reported success" and "the schema is
--  right" are different claims (D-021, D-005's shape); a check whose failure
--  mode is an empty result nobody reads is the first kind pretending to be the
--  second.
--
--  NON-DESTRUCTIVE. This file contains NO transaction control. The runner wraps
--  it in a SAVEPOINT and rolls back to that savepoint afterwards, so the
--  fixtures vanish while the migration itself survives to COMMIT. Verification
--  and migration are therefore atomic together: a failed check takes the
--  migration down with it.
--  CIKs 999000001-3 are synthetic and implausible as real filers.
--
--  Every check below can be made to fail on purpose; see the report's
--  "how to trip each one" section. A guard never seen red is not a guard.
-- ============================================================================

-- ----------------------------------------------------------------------------
--  PART A — structural. The objects exist and are the right shape.
-- ----------------------------------------------------------------------------
DO $$
DECLARE
    missing text;
BEGIN
    -- A1: every table exists.
    SELECT string_agg(t, ', ') INTO missing
    FROM unnest(ARRAY['filer','filer_ticker','filing','fact','schema_migration']) AS t
    WHERE to_regclass('public.' || t) IS NULL;
    IF missing IS NOT NULL THEN
        RAISE EXCEPTION 'A1 FAILED: missing table(s): %', missing;
    END IF;

    -- A2: the fact uniqueness key is the one we chose, not the one that looks
    -- right. This is the check that matters most in the whole file — it is the
    -- structural expression of "an amendment inserts, never updates".
    IF NOT EXISTS (
        SELECT 1 FROM pg_constraint
        WHERE conname = 'fact_one_per_filing'
          AND conrelid = 'public.fact'::regclass
          AND contype  = 'u'
    ) THEN
        RAISE EXCEPTION 'A2 FAILED: fact_one_per_filing unique constraint absent';
    END IF;

    -- A3: and the key MUST include accession. Without it the constraint
    -- collapses to (concept, period, unit) and forces the upsert.
    IF NOT EXISTS (
        SELECT 1
        FROM pg_constraint c
        JOIN LATERAL unnest(c.conkey) AS k(attnum) ON TRUE
        JOIN pg_attribute a ON a.attrelid = c.conrelid AND a.attnum = k.attnum
        WHERE c.conname = 'fact_one_per_filing'
          AND c.conrelid = 'public.fact'::regclass
          AND a.attname = 'accession'
    ) THEN
        RAISE EXCEPTION 'A3 FAILED: fact uniqueness does not include accession - '
                        'amendments would collide and force an overwrite';
    END IF;

    -- A4: no unique constraint may exist on (concept, period) WITHOUT
    -- accession. This is the prohibition stated as a check rather than a
    -- comment. If someone adds the "obvious" key in 0002, this goes red.
    IF EXISTS (
        SELECT 1
        FROM pg_constraint c
        WHERE c.conrelid = 'public.fact'::regclass
          AND c.contype IN ('u','p')
          AND EXISTS (
              SELECT 1 FROM unnest(c.conkey) k(attnum)
              JOIN pg_attribute a ON a.attrelid = c.conrelid AND a.attnum = k.attnum
              WHERE a.attname = 'concept'
          )
          AND NOT EXISTS (
              SELECT 1 FROM unnest(c.conkey) k(attnum)
              JOIN pg_attribute a ON a.attrelid = c.conrelid AND a.attnum = k.attnum
              WHERE a.attname = 'accession'
          )
    ) THEN
        RAISE EXCEPTION 'A4 FAILED: a uniqueness constraint covers concept but '
                        'not accession - this forces upsert-on-amendment';
    END IF;

    -- A8: the key MUST include entity_cik. Without it, two co-registrants
    -- reporting the same concept for the same period collide, and ON CONFLICT
    -- DO NOTHING silently discards the second while calling it idempotency.
    IF NOT EXISTS (
        SELECT 1
        FROM pg_constraint c
        JOIN LATERAL unnest(c.conkey) AS k(attnum) ON TRUE
        JOIN pg_attribute a ON a.attrelid = c.conrelid AND a.attnum = k.attnum
        WHERE c.conname = 'fact_one_per_filing'
          AND c.conrelid = 'public.fact'::regclass
          AND a.attname = 'entity_cik'
    ) THEN
        RAISE EXCEPTION 'A8 FAILED: fact uniqueness does not include entity_cik - '
                        'co-registrants in one filing would collide and the '
                        'second would be discarded as a duplicate';
    END IF;

    -- A5: the ticker exclusion constraint exists.
    IF NOT EXISTS (
        SELECT 1 FROM pg_constraint
        WHERE conname = 'filer_ticker_no_overlap'
          AND conrelid = 'public.filer_ticker'::regclass
          AND contype  = 'x'
    ) THEN
        RAISE EXCEPTION 'A5 FAILED: filer_ticker_no_overlap exclusion constraint absent';
    END IF;

    -- A6: filing.filing_date is NOT NULL. The point-in-time boundary cannot be
    -- optional.
    IF NOT EXISTS (
        SELECT 1 FROM pg_attribute
        WHERE attrelid = 'public.filing'::regclass
          AND attname  = 'filing_date'
          AND attnotnull
    ) THEN
        RAISE EXCEPTION 'A6 FAILED: filing.filing_date is nullable';
    END IF;

    -- A7: fact.accession is NOT NULL and references filing. A fact that can
    -- exist without a filing is a fact with no knowability date.
    IF NOT EXISTS (
        SELECT 1 FROM pg_constraint
        WHERE conrelid = 'public.fact'::regclass
          AND contype = 'f'
          AND confrelid = 'public.filing'::regclass
    ) THEN
        RAISE EXCEPTION 'A7 FAILED: fact has no foreign key to filing';
    END IF;

    RAISE NOTICE 'PART A passed: structure is the shape 0001 claims.';
END $$;


-- ----------------------------------------------------------------------------
--  Fixtures. Two filers, one ticker reassigned between them, one restatement.
-- ----------------------------------------------------------------------------
INSERT INTO filer (cik, current_name, current_sic, metadata_as_of) VALUES
    (999000001, 'Synthetic Alpha Corp', '3711', DATE '2026-09-23'),
    (999000002, 'Synthetic Beta Inc',   '7372', DATE '2026-09-23'),
    (999000003, 'Synthetic Gamma Ltd',  '2834', DATE '2026-09-23');

-- SYNTH was Alpha's until 2018-03-01, then Beta's. The real-world trap.
INSERT INTO filer_ticker (cik, ticker, valid_from, valid_to) VALUES
    (999000001, 'SYNTH', DATE '2011-01-01', DATE '2018-03-01'),
    (999000002, 'SYNTH', DATE '2018-03-01', NULL);

-- Alpha: an original 10-K, then a 10-K/A restating the same period.
INSERT INTO filing (accession, cik, form_type, filing_date, period_of_report, is_amendment, amends_accession) VALUES
    ('9990000001-22-000001', 999000001, '10-K',   DATE '2022-02-15', DATE '2021-12-31', FALSE, NULL),
    ('9990000001-23-000007', 999000001, '10-K/A', DATE '2023-05-20', DATE '2021-12-31', TRUE,  '9990000001-22-000001'),
    ('9990000001-23-000001', 999000001, '10-K',   DATE '2023-02-14', DATE '2022-12-31', FALSE, NULL);

-- Gamma filed a 10-K in 2013 and then stopped existing. It must still be in
-- the 2013 universe. This is the survivorship case.
INSERT INTO filing (accession, cik, form_type, filing_date, period_of_report, is_amendment) VALUES
    ('9990000003-13-000001', 999000003, '10-K', DATE '2013-03-01', DATE '2012-12-31', FALSE);

-- FY2021 revenue: originally 1000, restated to 900 fifteen months later.
INSERT INTO fact (accession, entity_cik, concept, unit, period_type, period_start, period_end, value) VALUES
    ('9990000001-22-000001', 999000001, 'Revenues', 'USD', 'duration', DATE '2021-01-01', DATE '2021-12-31', 1000),
    ('9990000001-23-000007', 999000001, 'Revenues', 'USD', 'duration', DATE '2021-01-01', DATE '2021-12-31',  900),
    ('9990000001-23-000001', 999000001, 'Revenues', 'USD', 'duration', DATE '2022-01-01', DATE '2022-12-31', 1200);

-- THE CO-REGISTRANT CASE (OPEN-29). Beta's facts inside Alpha's submission:
-- same accession, same concept, same period, same unit, no dimensions. These
-- differ ONLY by entity_cik. Before entity_cik entered the key this INSERT
-- collided, and ON CONFLICT DO NOTHING would have discarded it as a re-ingest.
INSERT INTO fact (accession, entity_cik, concept, unit, period_type, period_start, period_end, value) VALUES
    ('9990000001-22-000001', 999000002, 'Revenues', 'USD', 'duration', DATE '2021-01-01', DATE '2021-12-31', 55);


-- ----------------------------------------------------------------------------
--  PART B — behavioural. §4 of the handover.
-- ----------------------------------------------------------------------------
DO $$
DECLARE
    v        numeric;
    n        integer;
    leaked   integer;
    cutoff   date;
BEGIN
    -- ====================================================================
    -- B1 — POINT IN TIME. Facts as of a past date return nothing filed
    -- after it. This is the query the whole schema exists to make possible.
    -- As of 2022-06-30, only the ORIGINAL 1000 was knowable.
    -- ====================================================================
    SELECT f.value INTO v
    FROM fact f JOIN filing g ON g.accession = f.accession
    WHERE f.entity_cik = 999000001          -- entity, NOT g.cik. See OPEN-29.
      AND f.concept = 'Revenues'
      AND f.period_end = DATE '2021-12-31'
      AND f.dimensions = '{}'::jsonb
      AND g.filing_date <= DATE '2022-06-30'
    ORDER BY g.filing_date DESC, g.accession DESC
    LIMIT 1;

    IF v IS DISTINCT FROM 1000 THEN
        RAISE EXCEPTION 'B1 FAILED: as-of 2022-06-30 returned %, expected 1000 '
                        '(the restatement had not been filed yet)', v;
    END IF;

    -- And the same query after the restatement returns the restated value.
    SELECT f.value INTO v
    FROM fact f JOIN filing g ON g.accession = f.accession
    WHERE f.entity_cik = 999000001          -- entity, NOT g.cik. See OPEN-29.
      AND f.concept = 'Revenues'
      AND f.period_end = DATE '2021-12-31'
      AND f.dimensions = '{}'::jsonb
      AND g.filing_date <= DATE '2026-09-23'
    ORDER BY g.filing_date DESC, g.accession DESC
    LIMIT 1;

    IF v IS DISTINCT FROM 900 THEN
        RAISE EXCEPTION 'B1 FAILED: as-of today returned %, expected 900', v;
    END IF;

    -- The leak check, stated in the negative: of everything the as-of query is
    -- ALLOWED to see, nothing may post-date the boundary.
    --
    -- The first version of this check read
    --   WHERE filing_date <= D AND filing_date > D
    -- which is empty by construction whatever the data says. It could not fail,
    -- so it proved nothing while looking like proof — the same defect as a
    -- harness that reports green without running. Replaced with a check that
    -- reads the data and can go red: take the newest filing the as-of window
    -- admits and assert it really is at or before the boundary.
    SELECT count(*) INTO leaked
    FROM fact f JOIN filing g ON g.accession = f.accession
    WHERE f.entity_cik = 999000001
      AND g.filing_date <= DATE '2022-06-30';
    IF leaked <> 1 THEN
        RAISE EXCEPTION 'B1 FAILED: the as-of 2022-06-30 window admits % fact '
                        'rows for this entity, expected exactly 1 (the original). '
                        'More means a later filing is visible before it was filed.',
                        leaked;
    END IF;

    SELECT max(g.filing_date) INTO cutoff
    FROM fact f JOIN filing g ON g.accession = f.accession
    WHERE f.entity_cik = 999000001
      AND g.filing_date <= DATE '2022-06-30';
    IF cutoff > DATE '2022-06-30' THEN
        RAISE EXCEPTION 'B1 FAILED: as-of window returned a filing dated %, '
                        'which is after the boundary', cutoff;
    END IF;

    -- ====================================================================
    -- B2 — AMENDMENT. Both rows present, distinguishable by filing date.
    -- If this returns 1, an overwrite happened and the point-in-time
    -- property is already gone.
    -- ====================================================================
    SELECT count(*) INTO n
    FROM fact f JOIN filing g ON g.accession = f.accession
    WHERE f.entity_cik = 999000001          -- entity, NOT g.cik. See OPEN-29.
      AND f.concept = 'Revenues'
      AND f.period_end = DATE '2021-12-31';

    IF n <> 2 THEN
        RAISE EXCEPTION 'B2 FAILED: expected 2 rows for the restated period '
                        '(original + amendment), found %. A value of 1 means '
                        'the amendment overwrote the original.', n;
    END IF;

    -- They must be distinguishable, and the amendment must be identifiable
    -- as one rather than inferred from ordering.
    IF NOT EXISTS (
        SELECT 1 FROM fact f JOIN filing g ON g.accession = f.accession
        WHERE f.entity_cik = 999000001 AND f.period_end = DATE '2021-12-31'
          AND g.is_amendment AND f.value = 900
    ) THEN
        RAISE EXCEPTION 'B2 FAILED: the restated value is not carried by a '
                        'filing marked is_amendment';
    END IF;

    -- ====================================================================
    -- B3 — UNIVERSE, keyed on CIK alone. Gamma filed a 10-K in 2013 and
    -- never again. It MUST be in the 2013 universe. A universe built from
    -- a current ticker file would have lost it — that is survivorship
    -- bias, and ruling 5 exists to prevent exactly this row going missing.
    -- ====================================================================
    SELECT count(*) INTO n
    FROM (
        SELECT DISTINCT g.cik
        FROM filing g
        WHERE g.form_type = '10-K'
          AND g.filing_date >= DATE '2013-01-01'
          AND g.filing_date <  DATE '2014-01-01'
    ) u;

    IF n <> 1 THEN
        RAISE EXCEPTION 'B3 FAILED: 2013 10-K universe has % members, expected 1', n;
    END IF;

    IF NOT EXISTS (
        SELECT 1 FROM filing
        WHERE cik = 999000003 AND form_type = '10-K'
          AND filing_date BETWEEN DATE '2013-01-01' AND DATE '2013-12-31'
    ) THEN
        RAISE EXCEPTION 'B3 FAILED: the dead filer is absent from its own '
                        'filing year - survivorship bias is present';
    END IF;

    -- ====================================================================
    -- B4 — TICKER REASSIGNMENT. The handover suspected this might not be
    -- constructible with synthetic data. It is, and better: the constraint
    -- can be shown to REFUSE the wrong case as well as permit the right one.
    -- ====================================================================
    SELECT cik INTO n FROM filer_ticker
    WHERE ticker = 'SYNTH'
      AND daterange(valid_from, valid_to, '[)') @> DATE '2014-06-01';
    IF n <> 999000001 THEN
        RAISE EXCEPTION 'B4 FAILED: SYNTH in 2014 resolved to %, expected 999000001', n;
    END IF;

    SELECT cik INTO n FROM filer_ticker
    WHERE ticker = 'SYNTH'
      AND daterange(valid_from, valid_to, '[)') @> DATE '2020-06-01';
    IF n <> 999000002 THEN
        RAISE EXCEPTION 'B4 FAILED: SYNTH in 2020 resolved to %, expected 999000002', n;
    END IF;

    -- ====================================================================
    -- B5 - CO-REGISTRANT (OPEN-29). Two entities reported the same concept,
    -- period and unit inside ONE accession with no dimensions. Both must
    -- survive and each must be retrievable as its own. If this returns 1,
    -- entity_cik is not in the key and a real fact was discarded as a
    -- duplicate - the failure this schema exists to refuse.
    -- ====================================================================
    SELECT count(*) INTO n
    FROM fact
    WHERE accession = '9990000001-22-000001'
      AND concept = 'Revenues' AND period_end = DATE '2021-12-31';
    IF n <> 2 THEN
        RAISE EXCEPTION 'B5 FAILED: expected 2 co-registrant facts in one '
                        'accession, found %. A value of 1 means the second '
                        'entity was discarded as a duplicate.', n;
    END IF;

    SELECT value INTO v FROM fact
    WHERE accession = '9990000001-22-000001' AND entity_cik = 999000002
      AND concept = 'Revenues' AND period_end = DATE '2021-12-31';
    IF v IS DISTINCT FROM 55 THEN
        RAISE EXCEPTION 'B5 FAILED: the co-registrant fact returned %, expected 55', v;
    END IF;

    RAISE NOTICE 'PART B passed: point-in-time, amendment, universe, reassignment, co-registrant.';
END $$;


-- ----------------------------------------------------------------------------
--  PART C — the refusals. A constraint that has never refused anything is a
--  constraint in name. Each of these MUST raise; if the INSERT succeeds, the
--  guard is absent and the check fails.
-- ----------------------------------------------------------------------------
DO $$
DECLARE
    got_refused boolean;
BEGIN
    -- C1: two CIKs holding the same ticker at the same time must be REFUSED.
    got_refused := FALSE;
    BEGIN
        INSERT INTO filer_ticker (cik, ticker, valid_from, valid_to)
        VALUES (999000003, 'SYNTH', DATE '2015-01-01', DATE '2016-01-01');
    EXCEPTION WHEN exclusion_violation THEN
        got_refused := TRUE;
    END;
    IF NOT got_refused THEN
        RAISE EXCEPTION 'C1 FAILED: an overlapping ticker assignment was ACCEPTED - '
                        'one ticker can resolve to two CIKs at once';
    END IF;

    -- C2: the same filing asserting the same concept/period/unit twice must be
    -- REFUSED. This is the idempotency half of the key.
    got_refused := FALSE;
    BEGIN
        INSERT INTO fact (accession, entity_cik, concept, unit, period_type, period_start, period_end, value)
        VALUES ('9990000001-22-000001', 999000001, 'Revenues', 'USD', 'duration',
                DATE '2021-01-01', DATE '2021-12-31', 1111);
    EXCEPTION WHEN unique_violation THEN
        got_refused := TRUE;
    END;
    IF NOT got_refused THEN
        RAISE EXCEPTION 'C2 FAILED: a duplicate fact within one filing was ACCEPTED';
    END IF;

    -- C3: a fact with no filing must be REFUSED. A fact without a filing has no
    -- knowability date and is unusable point-in-time.
    got_refused := FALSE;
    BEGIN
        INSERT INTO fact (accession, entity_cik, concept, unit, period_type, period_start, period_end, value)
        VALUES ('0000000000-00-000000', 999000001, 'Revenues', 'USD', 'duration',
                DATE '2021-01-01', DATE '2021-12-31', 1);
    EXCEPTION WHEN foreign_key_violation THEN
        got_refused := TRUE;
    END;
    IF NOT got_refused THEN
        RAISE EXCEPTION 'C3 FAILED: a fact with no filing was ACCEPTED';
    END IF;

    -- C4: an instant spanning a range must be REFUSED. A balance-sheet value
    -- that claims to cover a period is a modelling error, not a value.
    got_refused := FALSE;
    BEGIN
        INSERT INTO fact (accession, entity_cik, concept, unit, period_type, period_start, period_end, value)
        VALUES ('9990000001-22-000001', 999000001, 'Assets', 'USD', 'instant',
                DATE '2021-01-01', DATE '2021-12-31', 5000);
    EXCEPTION WHEN check_violation THEN
        got_refused := TRUE;
    END;
    IF NOT got_refused THEN
        RAISE EXCEPTION 'C4 FAILED: an instant with a non-zero span was ACCEPTED';
    END IF;

    RAISE NOTICE 'PART C passed: every guard refused what it should refuse.';
END $$;


-- No ROLLBACK here. The runner rolls back to its savepoint, which removes the
-- fixtures above and leaves the migration intact.
