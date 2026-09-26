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

**Updated 2026-09-26.** This table said *"Database: none yet"* and *"Container:
never built"* until then - written on day one and never revised, which is its
own small lesson about documents that describe a plan rather than a system.

| Component | File | Status |
|---|---|---|
| FastAPI app | `app/main.py` | `/healthz`, `/v1/meta` only. **No DB-backed endpoint exists.** |
| API-key auth (fails closed) | `app/auth.py` | built, proven (G-1..G-2) |
| DB-safety guard (positive identity) | `tests/keel_db_guard.py` | built and **proven against a real cluster** (OPEN-1 closed) |
| API contract snapshot | `tests/contract/` | built, proven (G-8) |
| Gate: test, then deploy, then verify live SHA | `.github/workflows/gate.yml` | **proven** - and was red for two days unnoticed (F-036) |
| Web container | `Dockerfile` | built and deployed |
| **Ingest container** | **`Dockerfile.ingest`** | **built and running (D-040)** |
| Migration runner | `db/migrate.py` | D-021. Proven on 16.15 and 18.3 |
| Migrations 0001-0004 | `db/migrations/` | applied and verified on r1 and r2 |
| Fact store | cluster `stockgrader-db-r2` | **150 GB, PostgreSQL 16.15, loading the 45-quarter window** |
| EDGAR client | `ingest/edgar.py` | D-023. Rate-limited, declared UA, no retry that hides a 403 |
| FSDS loader | `ingest/fsds.py`, `tools/load_quarter.py` | proven; **buffers a quarter in memory** (F-050) |
| Window fetcher + driver | `ingest/window.py`, `tools/fetch_fsds.py`, `tools/load_window.py` | built 2026-09-26 (F-046) |
| Daily price capture | `ingest/prices.py`, `tools/capture_prices.py` | **running daily** on a schedule (D-036) |
| Operational guards | `tools/apply_canary.py`, `verify_cluster.py`, `verify_writer.py`, `load_progress.py` | built 2026-09-25/26 |

## Ingestion — the shape, as built (D-040)

```
  SEC  --EdgarClient-->  stockgrader-ingest (Fly app, sjc, 8 GB)
                             |  one archive at a time, discarded after
                             |  private network, NO proxy
                             v
                         stockgrader-db-r2 : stockgrader_scratch
                             ^
                             |  pgbouncer, writer role, read-only
                         stockgradermdk (web)
```

**Two images, and the separation is the point.** `Dockerfile` has `app/` and no
loader. `Dockerfile.ingest` has `ingest/` and three tools and no `app/`. The web
process **cannot import an ingestion path** because the path is not in its image.

**Two different endpoints, deliberately.** Migrations and bulk loads use the
**direct** endpoint - the runner takes `pg_advisory_xact_lock` and owns each
migration's transaction, and those semantics are not reliable through a
transaction-mode pooler. The **app** uses **pgbouncer**. Getting this backwards
is silent.

**Run it:**

```
docker build -f Dockerfile.ingest -t sgmdk-ingest .
docker tag  sgmdk-ingest registry.fly.io/stockgrader-ingest:latest
docker push registry.fly.io/stockgrader-ingest:latest
fly machine run registry.fly.io/stockgrader-ingest:latest -a stockgrader-ingest \
    --region sjc --vm-size shared-cpu-4x --vm-memory 8192 --restart no
fly logs -a stockgrader-ingest
```

**`DATABASE_URL` goes in as a staged secret over stdin** - never `--env`, which
is refused as credential leakage and is the same exposure `fly secrets set`
carries.

**It is restartable by re-running.** The driver keeps no state; it reads
`coverage_quarter` and resumes at the first gap. A kill costs the quarter in
flight and nothing else - proven three times in one night (F-049).

## Planned shape

**Partly built as of 2026-09-26.** The first two bullets exist; the rest is
still gated on open D-entries.

- **Web process:** FastAPI, read-only against Postgres. **Built** - but no
  DB-backed endpoint exists yet, so `DATABASE_URL` is set and nothing reads it.
- **Ingestion:** a separate Fly app and image, never inside the web process.
  **Built (D-040).** Prices capture nightly on a schedule (D-036); fundamentals
  load from FSDS archives. Fund holdings are not built.
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
| `DATABASE_URL` | Fly secrets, app `stockgradermdk` | web runtime. **pgbouncer** endpoint, `stockgrader_app` at `writer`. Never in an image or a committed file |
| `DATABASE_URL` | Fly secrets, app `stockgrader-ingest` | ingest runtime. **direct** endpoint, schema-admin rights. Same name, different app, deliberately different value - the pooler is wrong for migrations and bulk loads |
| `GIT_SHA` | build arg (not a secret) | `/healthz` build verification |

## Recovery access (KEEL V11). Answer all four before any destructive op.

| Question | Answer |
|---|---|
| 1. Exact command that lists backups for OUR cluster | **`fly mpg backup list d1zj5omk443ryqkv --all`** - re-run 2026-09-23. **Without `--all` it lists only the last 24 hours**, which is how a populated cluster reads as having no backups. Retention is 10 days, but **bounded by the oldest surviving *full*** - IDs are chains (`<FULL>_<CHILD>`) and children are not independently restorable (B-6; expiry behaviour unverified, testplan OPEN-7). **The listing now returns 21 backups, not one:** daily fulls (`20260922-192041F`, `20260923-000148F`), 6-hourly differentials, hourly incrementals through 2026-09-23T14:04:22Z. The rolling schedule is observably running on *this* cluster (F-next/backup-cadence-observable). Backup IDs are chains - `<FULL>_<CHILD>` - so a child is not independently restorable. This is the command that ran, not one that looks right (F-016). |
| 2. Recovery credential in password manager | `fly-user` (`schema_admin`) is the Step 16 recovery account. **[OWNER] to confirm it is in the password manager under the project name** - that confirmation is Step 16's actual proof and has not been given. The account was also printed in the clear at creation (F-014) and is on D-029's rotation list. Its separation from the application account was nominal until D-031 (F-017). |
| 3. Re-point the app without an image rebuild | `DATABASE_URL` is a runtime secret, so no rebuild is needed - confirmed in practice on 2026-09-22. **`fly mpg restore <CLUSTER_ID>` restores into a NEW cluster**, from either `--backup-id <ID>` or `--pitr-time <RFC3339>` (mutually exclusive; PITR confirmed present in flyctl v0.4.102, though **no command reports the PITR recovery window** - F-next/pitr-available-window-invisible, so `--backup-id` against a listed `completed` backup is the verifiable path). `-n/--name` names the restored cluster; unnamed, it is generated. Recovery is *not* finished when the data comes back. It is finished when the app points at the new cluster: **`fly mpg attach` AND THEN `fly secrets deploy`.** The deploy half is the step that silently does not happen - see F-015. |
| 4. Restore ever tested | **YES - 2026-09-23, end to end including cutover.** `fly mpg restore d1zj5omk443ryqkv --backup-id 20260923-155431F -n stockgrader-db-r1` produced `kzpwm0j1dm204nv3`, which is **now the live cluster**: both databases came across, a `writer` account (`stockgrader_app`) was created and attached with `-u`/`-d` - **but see the correction below: the restore also carried the old role catalogue**, `DATABASE_URL` reproduced F-015 as **Staged**, `fly secrets deploy` cleared it across both machines, and the new cluster was given its own chain root. **Three defects the drill found, none of which a green restore would have shown:** attach **refuses** to overwrite an existing `DATABASE_URL` so the written step 7 could not run (`F-next/attach-refuses-to-overwrite`); the restore **silently resized 10 GB to 15 GB** (`F-next/restore-resizes-disk`); the app connects via **pgbouncer**, not the direct endpoint (`F-next/app-connects-via-pgbouncer`). **The data half is NOT yet proven.** `/healthz` returned 200 on build `f9298de` but **opens no database connection** - it would answer identically against a dead cluster. Per B-5 and D-029 the recovery is finished when a live request answers **from the database**, and that endpoint does not exist yet. **Re-run after the ticker load**, when row counts make the data half meaningful (B-4). **CORRECTION, same day:** an earlier version of this row implied the cutover produced a clean cluster. **It did not. A restore is a copy, and it copied the role catalogue** - `stockgradermdk` and `fly-user`, both compromised on 2026-09-22, are live on `kzpwm0j1dm204nv3` with their original passwords (`F-next/restore-carries-compromised-roles`). **D-031 stands** - the app connects as `stockgrader_app` at `writer` - but **F-017's over-privilege was not escaped**, because the over-privileged account came across too. |


## The old cluster's configuration, captured before its destroy

**Why this is here.** `fly mpg restore` gave the live cluster **15 GB** when the
source had **10 GB** - unasked, with no size flag passed and none documented
(`F-next/restore-resizes-disk`). **The old cluster is the only surviving evidence
that 15 GB was not chosen**, and that evidence disappears when it is destroyed.
Whether to resize is a separate and unhurried question. **Whether anyone can
still tell it was unintended expires with the old cluster**, so the capture
happens now rather than at destroy time.

Captured 2026-09-23, verbatim, `fly mpg status d1zj5omk443ryqkv`:

```
Cluster Status
 ID                  │ d1zj5omk443ryqkv
 Name                │ stockgrader-db
 Organization        │ matt-kelly-802
 Region              │ sjc
 Status              │ ready
 Allocated Disk (GB) │ 10
 Replicas            │ 1
 Direct IP           │ direct.d1zj5omk443ryqkv.flympg.net
```

**The live cluster `kzpwm0j1dm204nv3` differs in exactly one respect: 15 GB.**
Region, plan, replica count and organisation all carried across faithfully. The
storage did not, and nothing announced it.
