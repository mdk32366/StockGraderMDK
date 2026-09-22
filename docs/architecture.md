# Architecture — What am I looking at?

*StockGraderMDK · last updated 2026-09-22 · state: Keel only, no features*

## Purpose

1. **Suitability scoring.** Score stocks and mutual funds on suitability for
   buying and holding. The score is a claim about the world, so its components,
   weights, and falsification test are pre-registered before it touches real
   data (D-010).
2. **Fund overlap.** Measure how much two or more funds hold in common.
3. **API.** Serve both over a versioned HTTP API (GET and POST) to another
   application.

## What exists today

| Component | File | Status |
|---|---|---|
| FastAPI app | `app/main.py` | `/healthz`, `/v1/meta` only |
| API-key auth (fails closed) | `app/auth.py` | built, proven (testplan G-1..G-2) |
| DB-safety guard (positive identity) | `tests/keel_db_guard.py` | built, logic proven; real-DB probe **never run** (testplan OPEN-1) |
| API contract snapshot | `tests/contract/` | built, proven (G-8) |
| Gate: test then deploy then verify live SHA | `.github/workflows/gate.yml` | written; **not yet proven** (Step 14) |
| Container | `Dockerfile` | written; **never built** (testplan OPEN-2) |
| Database | — | none yet (D-009 open) |

## Planned shape

The shape is not built yet and is gated on open D-entries.

- **Web process:** FastAPI, read-only against Postgres.
- **Ingestion:** a separate Fly process group or scheduled Machine, never inside
  the web process. It refreshes prices nightly and ingests fund holdings and
  fundamentals as filings appear.
- **Overlap:** the weight-based measure is the sum over shared holdings of
  min(wA, wB), alongside count-based overlap. Every result carries its
  resolution coverage (the share of each fund's weight that resolved to a common
  identifier) and a named category for every unresolved holding (A-002).
- **Every response carries provenance:** as-of dates, sources, component
  breakdown, and coverage. No bare numbers.

## Runtime configuration: secrets by EXACT name (KEEL P4)

| Name | Lives in | Used by |
|---|---|---|
| `STOCKGRADER_API_KEY` | Fly secrets | `app/auth.py` |
| `FLY_API_TOKEN` | GitHub Actions secrets | `gate.yml` deploy job (deploy-scoped token) |
| `DATABASE_URL` | Fly secrets (future) | app runtime; never in an image, never in a committed file |
| `GIT_SHA` | build arg (not a secret) | `/healthz` build verification |

## Recovery access (KEEL V10). Answer all four before any destructive op.

| Question | Answer |
|---|---|
| 1. Exact command that lists backups for OUR cluster | **Not established, and must not be filled in yet.** No database exists, and a command recorded before it has run against the real cluster is a belief written as a fact (P8). Record the command at cluster creation, after running it against the real cluster. The command differs between Fly Postgres flavors. |
| 2. Recovery credential in password manager | **Not established.** Create it at cluster creation (Day-One Step 16). |
| 3. Re-point the app without an image rebuild | `DATABASE_URL` is a runtime secret, so no rebuild should be needed. The exact command is **ASSUMED, not tested** (A-005). |
| 4. Restore ever tested | **Never.** Test on a staging copy before the first destructive operation. |
