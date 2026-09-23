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
| 1. Exact command that lists backups for OUR cluster | **`fly mpg backup list d1zj5omk443ryqkv --all`** - re-run 2026-09-23. **Without `--all` it lists only the last 24 hours**, which is how a populated cluster reads as having no backups. Retention is 10 days, but **bounded by the oldest surviving *full*** - IDs are chains (`<FULL>_<CHILD>`) and children are not independently restorable (B-6; expiry behaviour unverified, testplan OPEN-7). **The listing now returns 21 backups, not one:** daily fulls (`20260922-192041F`, `20260923-000148F`), 6-hourly differentials, hourly incrementals through 2026-09-23T14:04:22Z. The rolling schedule is observably running on *this* cluster (F-next/backup-cadence-observable). Backup IDs are chains - `<FULL>_<CHILD>` - so a child is not independently restorable. This is the command that ran, not one that looks right (F-016). |
| 2. Recovery credential in password manager | `fly-user` (`schema_admin`) is the Step 16 recovery account. **[OWNER] to confirm it is in the password manager under the project name** - that confirmation is Step 16's actual proof and has not been given. The account was also printed in the clear at creation (F-014) and is on D-029's rotation list. Its separation from the application account was nominal until D-031 (F-017). |
| 3. Re-point the app without an image rebuild | `DATABASE_URL` is a runtime secret, so no rebuild is needed - confirmed in practice on 2026-09-22. **`fly mpg restore <CLUSTER_ID>` restores into a NEW cluster**, from either `--backup-id <ID>` or `--pitr-time <RFC3339>` (mutually exclusive; PITR confirmed present in flyctl v0.4.102, though **no command reports the PITR recovery window** - F-next/pitr-available-window-invisible, so `--backup-id` against a listed `completed` backup is the verifiable path). `-n/--name` names the restored cluster; unnamed, it is generated. Recovery is *not* finished when the data comes back. It is finished when the app points at the new cluster: **`fly mpg attach` AND THEN `fly secrets deploy`.** The deploy half is the step that silently does not happen - see F-015. |
| 4. Restore ever tested | **YES - 2026-09-23, end to end including cutover.** `fly mpg restore d1zj5omk443ryqkv --backup-id 20260923-155431F -n stockgrader-db-r1` produced `kzpwm0j1dm204nv3`, which is **now the live cluster**: both databases came across, a `writer` account (`stockgrader_app`) was created and attached with `-u`/`-d` - **but see the correction below: the restore also carried the old role catalogue**, `DATABASE_URL` reproduced F-015 as **Staged**, `fly secrets deploy` cleared it across both machines, and the new cluster was given its own chain root. **Three defects the drill found, none of which a green restore would have shown:** attach **refuses** to overwrite an existing `DATABASE_URL` so the written step 7 could not run (`F-next/attach-refuses-to-overwrite`); the restore **silently resized 10 GB to 15 GB** (`F-next/restore-resizes-disk`); the app connects via **pgbouncer**, not the direct endpoint (`F-next/app-connects-via-pgbouncer`). **The data half is NOT yet proven.** `/healthz` returned 200 on build `f9298de` but **opens no database connection** - it would answer identically against a dead cluster. Per B-5 and D-029 the recovery is finished when a live request answers **from the database**, and that endpoint does not exist yet. **Re-run after the ticker load**, when row counts make the data half meaningful (B-4). **CORRECTION, same day:** an earlier version of this row implied the cutover produced a clean cluster. **It did not. A restore is a copy, and it copied the role catalogue** - `stockgradermdk` and `fly-user`, both compromised on 2026-09-22, are live on `kzpwm0j1dm204nv3` with their original passwords (`F-next/restore-carries-compromised-roles`). **D-031 stands** - the app connects as `stockgrader_app` at `writer` - but **F-017's over-privilege was not escaped**, because the over-privileged account came across too. |
