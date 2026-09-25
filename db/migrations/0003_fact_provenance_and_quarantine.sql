-- ============================================================================
--  MIGRATION 0003 — provenance on `fact`, and the collision quarantine
--
--  Governed by: D23 §2 (OPEN-54) and D23 §3 (OPEN-55), D-023, D16 §2.1.
--  RUN AS: a schema_admin. NO TRANSACTION CONTROL — the runner owns it.
--
--  WHY 0003 EXISTS AT ALL: 0002 MISSED THE TABLE IT WAS ORDERED FOR
--  ----------------------------------------------------------------
--  0002 added `source_fetch_id` to `filer`, `filer_ticker` and `filing`. It did
--  not add it to `fact`. D16 §2.1 ordered 0002 *before* the fact slice on the
--  reasoning that "the fact slice is where the volume arrives; in the other
--  order the largest body of data this project holds becomes the part that can
--  never be traced." 0002 as written left precisely that gap.
--
--  It survived review because the question being answered was "which tables does
--  the loader write?" — and `fact` had no loader, so it was invisible to that
--  question. The right question was "which tables hold data?"
--
--  No fact rows exist anywhere yet, so this is still the cheap-now-impossible-
--  later window 0002 itself was ordered inside.
-- ============================================================================


-- ----------------------------------------------------------------------------
--  1. Provenance on `fact`
--
--  Same shape and same reasoning as 0002's three tables: NOT NULL, because a
--  nullable column makes an unprovenanced row representable, and a row that is
--  merely *supposed* to carry provenance is the same class of thing as a guard
--  that is merely supposed to be checked.
--
--  Added NULL, checked, then set NOT NULL — so the refusal below can inspect
--  what exists rather than failing on a column definition.
-- ----------------------------------------------------------------------------
ALTER TABLE fact ADD COLUMN source_fetch_id bigint NULL REFERENCES fetch_log (fetch_id);

DO $$
DECLARE
    orphans bigint;
BEGIN
    SELECT count(*) INTO orphans FROM fact WHERE source_fetch_id IS NULL;
    IF orphans > 0 THEN
        RAISE EXCEPTION
            '0003 REFUSES TO BACKFILL: % fact row(s) exist that were loaded '
            'before provenance was recorded. A provenance row describes a fetch '
            '- its URL, its moment, and the hash of what came back - and once a '
            'fetch has happened unrecorded that record cannot be reconstructed. '
            'Re-fetching produces a NEW fetch, not evidence of the old one. '
            'Resolution: truncate fact and re-ingest with provenance, or decide '
            'deliberately that this data is unprovenanced and record THAT.',
            orphans;
    END IF;
END $$;

ALTER TABLE fact ALTER COLUMN source_fetch_id SET NOT NULL;
CREATE INDEX fact_source_fetch_idx ON fact (source_fetch_id);

COMMENT ON COLUMN fact.source_fetch_id IS
    'The fetch whose payload this row was first derived from. NOT NULL: an '
    'unprovenanced fact is not representable. Added in 0003 because 0002 - the '
    'migration ordered specifically to make the fact table traceable - omitted '
    'this table.';


-- ----------------------------------------------------------------------------
--  2. The provenance exclusion list — the inversion D23 §2 ruled
--
--  0002's verification enumerated three table names and asserted each carried
--  provenance. It was correctly written and correctly passing while every fact
--  row was unprovenanced, because `fact` was not in the list.
--
--  The ruling's general form:
--      "A guard's blind spot is not usually in what it checks but in what it
--       enumerates."
--
--  So the check is inverted. 0003's verification DERIVES the tables it checks
--  from the catalogue and asserts each carries `source_fetch_id NOT NULL`,
--  MINUS the exclusions below.
--
--  THE FAILURE DIRECTION IS THE WHOLE POINT:
--    - an INCLUSION list fails OPEN  — a table added in 0004 is silently
--      unchecked, exactly as `fact` was;
--    - an EXCLUSION list fails CLOSED — a table added in 0004 is checked unless
--      somebody deliberately exempts it, and the exemption is a visible line in
--      a file with a reason beside it.
--
--  Both are enumerations. Only one of them is wrong by default.
--
--  Each exclusion carries its reason inline, per the ruling: "a list of names
--  with no reasons becomes a place to hide a table."
-- ----------------------------------------------------------------------------
CREATE TABLE provenance_exempt (
    -- OPEN-60. Exemptions are schema-qualified. Keyed on table_name alone, a
    -- row exempting 'staging_facts' would exempt a table of that name in EVERY
    -- schema, including one created years later by someone who never saw this
    -- list. The exemption must name the object it is exempting.
    schema_name text        NOT NULL DEFAULT 'public',
    table_name  text        NOT NULL,
    reason      text        NOT NULL,
    exempted_at timestamptz NOT NULL DEFAULT now(),
    PRIMARY KEY (schema_name, table_name),
    CONSTRAINT provenance_exempt_reason_substantive CHECK (length(btrim(reason)) >= 20)
);

COMMENT ON TABLE provenance_exempt IS
    'Tables deliberately exempt from carrying source_fetch_id. The verification '
    'derives its check set from the catalogue MINUS this table, so an omission '
    'here fails closed. A reason is mandatory and length-checked because a bare '
    'list of names becomes a place to hide a table.';

INSERT INTO provenance_exempt (table_name, reason) VALUES
    ('schema_migration',
     'The runner''s own ledger. It records which migrations ran, not data '
     'derived from a fetch, and it exists before any fetch can have happened.'),
    ('fetch_log',
     'The provenance record itself. Pointing it at a fetch would make it '
     'self-referential, and its own rows ARE the fetch evidence.'),
    ('provenance_exempt',
     'This table. It is a policy list maintained by migrations, not data '
     'derived from a retrieval.'),
    ('fact_collision',
     'Quarantined rows that were REFUSED, not loaded. They carry the fetch '
     'they came from in source_fetch_id and are exempt from the NOT NULL '
     'assertion only because the assertion is about the loaded store.');


-- ----------------------------------------------------------------------------
--  A CONDITIONAL exemption, and the only one in this file.
--
--  `keel_disposable_canary` marks a database as safe to truncate. Its PRESENCE
--  makes scratch disposable; its ABSENCE is what refuses the test harness
--  against production (testplan R-2). So whether it exists is environment-
--  dependent BY DESIGN, and that design is a safety control.
--
--  That collides with two rules in this migration, both of which are right:
--
--    * A2 fails closed on any table without provenance, so the canary must be
--      exempted or the migration cannot run on scratch.
--    * A3 refuses an exemption naming a table that does not exist, because a
--      stale exemption pre-authorises a future table reusing the name.
--
--  A static exemption would satisfy A2 on scratch and fail A3 on production.
--  So the row is inserted ONLY where the table actually is. On production no
--  exemption exists, because no canary exists, and A3 stays satisfied.
--
--  This does NOT create the canary. `db/keel_canary.sql` says never to add it
--  to a migration and that still holds - this exempts it where a human already
--  put it, and nowhere else.
-- ----------------------------------------------------------------------------
INSERT INTO provenance_exempt (schema_name, table_name, reason)
SELECT 'public', 'keel_disposable_canary',
       'Disposability marker placed by hand via db/keel_canary.sql, not data '
       'derived from a retrieval. Exempted conditionally because its presence '
       'is environment-dependent by design: it makes scratch safe to truncate '
       'and its absence refuses the harness against production.'
WHERE to_regclass('public.keel_disposable_canary') IS NOT NULL;


-- ----------------------------------------------------------------------------
--  3. fact_collision — OPEN-55's quarantine
--
--  FSDS violates its own documented unique key. Measured on 2026q2: 3,608,711
--  rows across 3,608,679 distinct key tuples — 32 collisions, and 31 of them
--  carry DIFFERENT VALUES.
--
--  So `ON CONFLICT DO NOTHING` on `fact_one_per_filing` would keep one value and
--  discard a genuinely different one, with no record, in the schema built to
--  make exactly that impossible.
--
--  D23 §3 ruled the response, and it is one step past "fail loudly" because at
--  31 rows a quarter across 45 quarters, aborting the load is not a policy
--  anyone would keep:
--
--    §3.1  rows agreeing on EVERY field including value -> keep one.
--          Genuine deduplication; ON CONFLICT DO NOTHING is correct for it.
--    §3.2  rows DISAGREEING on value -> BOTH quarantined, counted, reported.
--          Neither is loaded.
--    §3.3  the key is NOT weakened. Adding a source ordinal would let two rows
--          exist for one fact, which is what fact_one_per_filing forbids by
--          design and what A4 protects. The guarantee is worth more than 31
--          facts per quarter out of 3.4 million — and the alternative is not
--          keeping them, it is keeping ONE of them chosen arbitrarily with no
--          record, which is the silent loss.
--
--  This is the second instance of a standard this project already set with
--  `coreg`: a CHOSEN REFUSAL WE CAN COUNT AND INSPECT is a different object from
--  a silence. It is the general response to source data that violates its own
--  contract.
--
--  NO UNIQUE CONSTRAINT ON THE COLLIDING KEY HERE, deliberately. The whole point
--  is that these rows collide; a uniqueness constraint would refuse the second
--  one and reproduce the loss inside the quarantine.
-- ----------------------------------------------------------------------------
CREATE TABLE fact_collision (
    collision_id    bigint      GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    -- The colliding key, stored as the loader saw it.
    accession       text        NOT NULL REFERENCES filing (accession),
    entity_cik      bigint      NOT NULL REFERENCES filer (cik),
    concept         text        NOT NULL,
    taxonomy        text        NOT NULL,
    unit            text        NOT NULL,
    period_type     text        NOT NULL,
    period_start    date        NOT NULL,
    period_end      date        NOT NULL,
    dimensions      jsonb       NOT NULL,
    -- The disagreeing value. One row per competing assertion, so both survive.
    value           numeric     NOT NULL,
    -- Which source row it came from, for tracing back into the archive.
    -- OPEN-59: NOT NULL because it is part of this row's identity. Nullable, it
    -- could not distinguish two genuinely separate assertions of the same value
    -- from one row seen twice, and NULLs do not compare equal in a unique index.
    source_ordinal  integer     NOT NULL,
    source_fetch_id bigint      NOT NULL REFERENCES fetch_log (fetch_id),
    detected_at     timestamptz NOT NULL DEFAULT now(),

    CONSTRAINT fact_collision_period_type_valid CHECK (period_type IN ('instant','duration')),
    CONSTRAINT fact_collision_period_ordered    CHECK (period_start <= period_end),

    -- ------------------------------------------------------------------------
    -- OPEN-59 — re-ingesting an archive must leave this table UNCHANGED.
    --
    -- Every other table's idempotency is the schema's property: each insert
    -- lands on ON CONFLICT DO NOTHING against a real constraint. This table had
    -- no constraint at all, so a second ingest of the same quarter inserted the
    -- same quarantined rows again. A load that is idempotent everywhere except
    -- in the table recording its refusals is not idempotent.
    --
    -- The obvious fix -- uniqueness on the colliding key -- is the WRONG one,
    -- and A5 exists to forbid it: it would refuse the second competing value
    -- and reproduce, inside the quarantine, the exact loss the quarantine was
    -- built to prevent.
    --
    -- So identity is the colliding key PLUS the value PLUS the source ordinal:
    --
    --   * including `value` means two rows that disagree BOTH insert. That is
    --     the property A5 protects, and it is preserved by construction.
    --   * including `source_ordinal` means three rows that collide where two
    --     agree on value still yield three rows. Keyed on value alone they
    --     would collapse to two, silently discarding the evidence that the
    --     archive asserted that value twice.
    --   * both are properties of the ARCHIVE, not of the fetch, so they are
    --     stable across re-ingestion. source_fetch_id deliberately is NOT in
    --     the key: a re-ingest is a new fetch with a new fetch_id, so including
    --     it would make every row unique again and restore the defect.
    --
    -- Consequence, stated because it is the cost: the retained row keeps the
    -- FIRST fetch that produced it. That is honest -- the row's content is
    -- immutable, so first sighting is complete provenance, not the stale
    -- pointer OPEN-45 warns about for mutable `current_*` columns.
    -- ------------------------------------------------------------------------
    CONSTRAINT fact_collision_one_per_source_row UNIQUE (
        accession, entity_cik, concept, taxonomy, unit, period_type,
        period_start, period_end, dimensions, value, source_ordinal
    )
);

CREATE INDEX fact_collision_key_idx ON fact_collision
    (accession, entity_cik, concept, period_end);
CREATE INDEX fact_collision_fetch_idx ON fact_collision (source_fetch_id);

COMMENT ON TABLE fact_collision IS
    'Rows refused because they collide on fact_one_per_filing with a DIFFERENT '
    'value. Both competing assertions are kept here and neither is loaded. The '
    'key is not weakened to admit them: a chosen refusal we can count is a '
    'different object from a silence.';


-- ----------------------------------------------------------------------------
--  4. fact_collision_rate — the signal, per D23 §3.5
--
--  "Report the collision count on every load. The number is the signal. A jump
--   in the rate means something changed at the source, and that is the finding a
--   constant trickle would otherwise hide."
--
--  A view rather than a stored counter, for the reason 0002 used: the number is
--  derived, and a stored copy can diverge from what it counts.
-- ----------------------------------------------------------------------------
CREATE VIEW fact_collision_rate AS
SELECT
    x.url,
    x.retrieved_at,
    count(*)                              AS quarantined_rows,
    count(DISTINCT (c.accession, c.entity_cik, c.concept,
                    c.period_start, c.period_end, c.dimensions))
                                          AS distinct_collisions
FROM fact_collision c
JOIN fetch_log x ON x.fetch_id = c.source_fetch_id
GROUP BY x.url, x.retrieved_at
ORDER BY x.retrieved_at DESC;

COMMENT ON VIEW fact_collision_rate IS
    'Quarantined rows per fetch. The rate is the signal: a jump means something '
    'changed at the source, which a constant trickle would hide.';
