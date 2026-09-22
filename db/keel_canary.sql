-- ============================================================================
--  KEEL DISPOSABLE-DATABASE CANARY
--  Run this BY HAND, and ONLY against a database whose data is expendable.
--  Its presence is Factor 2 of tests/keel_db_guard.py: it tells the test
--  suite "you may truncate me."
--
--  NEVER run against production. NEVER add it to migrations. NEVER automate it.
--  Running this on production is one of the two deliberate acts required to
--  defeat the database-safety guard.
-- ============================================================================
CREATE TABLE IF NOT EXISTS keel_disposable_canary (
    marked_at  timestamptz NOT NULL DEFAULT now(),
    marked_by  text        NOT NULL,
    note       text
);
