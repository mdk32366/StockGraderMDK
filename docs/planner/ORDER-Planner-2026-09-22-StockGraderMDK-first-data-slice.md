# ORDER — Planner → Code — StockGraderMDK: the first data slice

**From:** Planner · **Date:** 2026-09-22
**Scope:** database cluster through verified fund overlap. Scoring is **not** in
this order; it waits on D-010.
**Standing rules unchanged:** report don't fix, one mutation per trip, every
guard tripped, credentials are [OWNER], the repo stays public (D-020).

---

## 1. Rulings recorded with this order

**D-009 — Fly Managed Postgres, one cluster, region `sjc`. RULED.**
Rejected: unmanaged Fly Postgres (the recovery maze that cost two hours was on
that path, and the backup-list command is the thing we could not run);
DuckDB (better columnar analytics, but single-writer and wrong for a hosted API
with a live consumer); SQLite (PharmFoldMDK proved a hermetic SQLite test can
pass while the real schema behaviour differs); a warehouse (cost and latency for
no benefit at this size). `sjc` follows D-017: app and cluster in one region.

**D-008 — Universe: US-listed common stocks, US mutual funds, and US ETFs.
PROPOSED, owner to ratify.**
ETFs are included because they file N-PORT, so overlap extends to them at almost
no cost, and a fund-vs-ETF overlap is the comparison most people actually want.
Rejected: mutual funds only (leaves the obvious question unanswerable);
non-US (identifier coverage collapses, A-002 gets worse, no demand yet).

**D-021 — Forward-only numbered SQL migrations, applied by our own runner.**
Each migration runs in its own transaction, under a session advisory lock, and
is followed by a **verification query** that asserts the objects it claims to
create actually exist and are of the right shape. "The migration reported
success" and "the schema changed" are different claims.
Rejected: Alembic with SQLAlchemy 2.0 as delivered — PharmFoldMDK §3.1 records a
migration chain that silently rolled itself back because a `SET` ran before the
transaction the tool owned. We can adopt it later deliberately; we are not
inheriting that failure on day one.

**D-022 — Ingestion runs as a separate Fly process group, never in the web
process.** A slow or rate-limited fetch must not touch API latency, and a
crashed ingest must not take the API down.

**D-023 — EDGAR client rules.** A declared User-Agent with contact details, a
hard client-side rate limit, retry with backoff on 429/503, and **no retry that
hides a 403**. Every fetch records the source URL, retrieval timestamp, and a
hash of the payload. Raw filings are **not** stored: EDGAR is the authoritative,
permanent copy, and the hash plus accession makes any row re-derivable.

## 2. Schema conventions — binding on every table in this slice

1. **Absence is a named category, never a blank or a zero** (Part C, Step C1).
   Every nullable result column has a companion reason column with an enumerated
   value. `NULL` with no reason is a defect.
2. **Coverage travels with every aggregate.** Anything computed over a set of
   holdings carries the fraction of weight that resolved, and the fraction that
   did not, by reason.
3. **Point-in-time ready.** Every fact is keyed to the filing that stated it
   (accession number and filed timestamp). A restatement is a new row, never an
   update. This costs little now and is unaffordable to retrofit if D-010 adopts
   GQS.
4. **Provenance on every row:** source, retrieved-at, and the ingest run id.
5. **Idempotent by accession.** Re-ingesting a filing changes nothing.

## 3. Phases

Each phase ends with its proof. Do not start the next until the proof is met.
Each new guard gets its own trip, recorded as usual.

### Phase 0 — cluster, recovery, and OPEN-1 ([OWNER] + Code)

1. **[OWNER]** Create the Managed Postgres cluster in `sjc`.
2. **[OWNER]** Day-One **Step 16** at cluster creation: a dedicated recovery
   account with a known password, stored in the password manager under the
   project name, never in an env file, never handed to an AI.
3. **Run the actual backup-list command against the actual cluster**, then
   record the exact command in `architecture.md` recovery row 1. Not a command
   that looks right — the one that ran.
4. `DATABASE_URL` becomes a Fly **runtime** secret. It is never baked into the
   image (Recovery Problem 3), and it never enters the repo (D-020: public).
5. Create a **separate scratch database** for the non-hermetic track and run
   `db/keel_canary.sql` against it **only**.
6. **Close OPEN-1.** Run `postgres_probe` against both:
   - the scratch database → canary present, small → accepted;
   - the **production** database → no canary → **refused**. This is read-only
     and safe, and it is the first time the guard has been tested against a
     database that actually matters.

**PROOF:** the recovery credential is findable in the password manager without
searching; `architecture.md` names a command that has been executed; the probe
accepted scratch and refused production, both recorded as findings.

### Phase 1 — migration runner and the identifier spine

Tables: `securities`, `security_identifiers` (type, value, source, as-of),
`funds` (series), `fund_classes` (class tickers), `source_files`, `ingest_runs`.

Load SEC's ticker-to-CIK map for companies and the fund class/series map. These
are small, have no filing lag, and are the denominators everything else reports
coverage against.

**PROOF:** the row count loaded reconciles two ways — against the source file's
entry count and against distinct identifiers stored — and the difference is
explained by named categories, not waved at (Step C3). The verification query
for each migration is in the repo and has been seen to fail against a schema
missing its object.

### Phase 2 — one fund, end to end

Tables: `filings` (accession, form, filed_at, period), `fund_holdings` (filing,
fund, raw identifier type/value, resolved security nullable,
`unresolved_reason`, weight, as-of).

Parse one fund's most recent N-PORT. Resolve identifiers against the spine.
Every unresolved holding keeps its raw identifier and gets a reason
(`NO_IDENTIFIER`, `UNMATCHED_CUSIP`, `NON_EQUITY`, `DERIVATIVE`, `CASH_OR_EQUIV`,
and so on — the list is yours to complete from what the data actually contains).

**PROOF:**
- The top ten holdings by weight match the fund's own published holdings page,
  checked by eye. Name the fund and the page in the finding.
- Weights reconcile to the filing's stated total within a tolerance you state.
- Resolution coverage is reported as a number, not asserted as fine.
- **A-001 and A-002 are updated to TESTED or REFUTED with real figures.** If
  coverage is poor, that is the finding, and it changes the design before we
  load anything else.

### Phase 3 — overlap, and the first real endpoints

**Definition, pre-registered before any code:** weight overlap between funds A
and B is the sum over shared securities of `min(weight_A, weight_B)`. Also
report count-based overlap. Both are reported against the resolved portion, with
coverage stated.

**Fixture requirement (Principle 6, V10 clause c):** the hand-computed fixture
must be one where a correct implementation and a plausible wrong one **differ** —
shared names with asymmetric weights, so that "count of shared names over total
names" and the min-weight sum cannot both be right. A fixture both would pass
proves nothing.

Endpoints:
- `GET /v1/funds/{ticker}/holdings`
- `POST /v1/funds/overlap` — body `{"tickers": [...]}`, pairwise results
- `GET /v1/freshness` — per dataset: as-of date, last successful ingest, and
  age. Derived at request time, never written down (PharmFoldMDK Recommendation
  B).

**`insufficient_data` is a first-class state, not an error and not a zero.**
Below a coverage floor you name, the response returns that state with its
reason. An overlap of 0.0 and "we could not resolve enough of this fund" are
different answers and must never render the same.

Regenerate the contract snapshot deliberately, and log the D-entry. Adding
endpoints is backward compatible for the consumer.

**PROOF:** the hand-computed pair matches to the stated tolerance; the coverage
floor has been tripped deliberately and returns `insufficient_data`; the
contract test is green against the regenerated snapshot.

### Phase 4 — widen

Backfill worker: resume-safe, idempotent by accession, rate-limited per D-023,
writing an `ingest_runs` row per attempt with counts and named miss reasons
(Step C2: know your miss counts).

**PROOF:** you can state, for the loaded universe, how many filings were
attempted, how many succeeded, and the miss counts by reason — and say which of
those numbers you have measured rather than inferred.

## 4. Guards this slice must add, each tripped

| Guard | What it must do when its input is wrong |
|---|---|
| Migration verification | Fail the migration, not log a warning |
| Weight reconciliation | Flag the filing, never silently normalise weights to 100% |
| Coverage floor | Return `insufficient_data`, never a number |
| Zero vs unknown | Distinguish them in the response schema, not in prose |
| Ingest failure (403/429/parse) | Mark the run FAILED and show data age; never leave a stale dataset looking fresh |
| Real-DB probe (OPEN-1) | Refuse production; accept scratch |

Each goes in `testplan.md` with its trip. A guard that documents a blind spot
rather than closing it is an open defect (Principle 6, V10 corollary).

## 5. New assumptions to register as you learn them

- **A-010** — N-PORT weight semantics: which field is percent-of-net-assets, and
  whether it is signed for shorts.
- **A-011** — a CUSIP identifies one security for our purposes (share classes,
  ADRs and dual listings are the falsifier).
- **A-012** — the SEC ticker maps are refreshed on a cadence we can state.
- **A-013** — the recorded backup-list command survives platform updates.

## 6. What this order deliberately does not do

- No prices (D-007 unruled).
- No scores (D-010 unruled; GQS v3 and `growth-model-lineage.md` still not in
  the Planner's hands).
- No bulk load before Phase 2's proof. Loading forty million holdings and then
  discovering A-002 is the expensive order of operations.

## 7. [OWNER] items

1. Ratify **D-008** (universe).
2. Phase 0 steps 1 and 2: cluster and recovery credential.
3. Move the API key out of Downloads into the password manager, if not yet done.
4. **D-010 / GQS v3**, and locate or descope `growth-model-lineage.md`.
5. **D-020**: name the observable that means development is complete, and log it
   as a decision (KEEL-2 V11, Step 17).
