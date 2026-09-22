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

## Recovery access (KEEL V11). Answer all four before any destructive op.

| Question | Answer |
|---|---|
| 1. Exact command that lists backups for OUR cluster | **`fly mpg backup list d1zj5omk443ryqkv --all`** - run against the real cluster on 2026-09-22; returned one completed full backup, `20260922-192041F`, at 2026-09-22T19:20:41Z. **Without `--all` it lists only the last 24 hours**, which is how a populated cluster reads as having no backups. Retention is 10 days. This is the command that ran, not one that looks right (F-016). |
| 2. Recovery credential in password manager | `fly-user` (`schema_admin`) is the Step 16 recovery account. **[OWNER] to confirm it is in the password manager under the project name** - that confirmation is Step 16's actual proof and has not been given. The account was also printed in the clear at creation (F-014) and is on D-029's rotation list. Its separation from the application account was nominal until D-031 (F-017). |
| 3. Re-point the app without an image rebuild | `DATABASE_URL` is a runtime secret, so no rebuild is needed - confirmed in practice on 2026-09-22. **`fly mpg restore <CLUSTER_ID> --backup-id <ID>` restores into a NEW cluster**, so recovery is *not* finished when the data comes back. It is finished when the app points at the new cluster: **`fly mpg attach` AND THEN `fly secrets deploy`.** The deploy half is the step that silently does not happen - see F-015, where an attach left `DATABASE_URL` Staged while the running machine held nothing. |
| 4. Restore ever tested | **Never.** Still never, and now with a specific reason to test it on a quiet day: the restore path ends in the same attach-and-deploy sequence that F-015 caught mid-failure. A restore that stops at "the data came back" leaves the app talking to the old cluster, or to nothing. Test on a scratch copy before the first destructive operation. |
