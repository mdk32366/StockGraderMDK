# CLOSEOUT AND PREWORK — Builder's half — StockGraderMDK — 2026-09-25

**From:** Code (Builder) · **For:** the next Builder context, and the Planner
**Branch:** `pr6-backup-strategy`, HEAD `9de8150`, pushed, working tree clean
**Suite:** 96/96 · **Register:** 105 findings, 46 decisions, 36 open, 31 closed
**Cluster:** `stockgrader_scratch` holds 0001–0004 and **3,368,813 real facts**

---

# PART 1 — What is not in the register

**This is the part only this context can write.** Everything in Parts 2–5 is
recoverable by reading the repository. This is not.

## 1.1 The interpreter is not the one your shell gives you

**`python` in this shell resolves to `C:\Projects\Project-PharmFoldMDK\.venv\`** —
a *different project's* virtualenv, activated by the user's profile. It carries
FastAPI 0.121.2 and pydantic 2.13.4 against this project's pins of 0.141.1 and
2.13.5.

**Always invoke `.venv\Scripts\python.exe` explicitly.** Never bare `python`.

Under the wrong interpreter the suite reports **63 passed, 1 failed** — and the
one failure is the OpenAPI contract test, which is **the only test in the suite
that can tell the difference.** The other 95 pass under both. Without that guard,
green from a foreign interpreter is indistinguishable from green from the right
one (**F-021** area, and the reason A-006 pinned the versions).

## 1.2 You will not be given a credential, and must not ask for one

**Standing constraint: no credential reaches the Builder.** Not in a DSN, not in
a variable, not "just for one command."

Consequences you will hit immediately:

- **Anything touching the live cluster is owner-at-the-keyboard.** One command at
  a time, wait for output, confirm, hand over the next. Any unexpected output
  stops the sequence.
- **Never ask the owner to paste a line containing a password.** That is how
  **F-021** happened: the handoff said *substitute the real password into this
  `DATABASE_URL=` line and paste the result back*, which puts the secret inside
  the region being returned. Use `Read-Host -AsSecureString` into `PGPASSWORD`,
  and a DSN in `host=… port=… user=… dbname=…` keyword form that carries no
  secret. Then `plan`/`apply` output is safe to paste in full.
- **`fly mpg create` and `fly mpg attach` print live credentials on success**
  (F-014). Never run them. Neither is yours.

## 1.3 Bash heredocs will fight you

Writing files through `bash <<'EOF'` **fails repeatedly** on apostrophes, `$`,
backticks and `$$` (PL/pgSQL). It has cost this project several wasted cycles
and once silently mangled a commit message.

**Use the `Write` tool for any file with prose in it.** For edits, write a small
Python script and run it with the repo venv. `git commit -F <file>`, never
`-m "…"` for anything multi-line.

## 1.4 Quote `PGBIN`

`C:\Program Files\PostgreSQL\18\bin` **contains a space.** An unquoted expansion
once produced a harness that reported **five guards green while running
nothing**. Quote it every time, and make any harness print evidence that it
actually ran.

## 1.5 The local Postgres is 18.3; the cluster is 16.15

Two majors apart (**F-027**). Everything proved identical across them, but that
is a result, not a guarantee for future work. There is a local server on 5432
whose password nobody has — **spin up a throwaway cluster with `initdb -A trust`
on a high port instead.** Every tool in `tools/` does exactly that.

## 1.6 Fly MPG specifics that cost time to learn

- **`fly mpg list` requires `--org personal`** when non-interactive.
- **`fly mpg proxy <cluster>`** listens on `127.0.0.1:16380` and routes to the
  **direct** endpoint. That is what the runner needs.
- **`pgbouncer.<id>.flympg.net` is a transaction-mode pooler.** The runner takes
  `pg_advisory_xact_lock` and owns each migration's transaction; those semantics
  are not reliable through it. **The app uses pgbouncer; migrations must not.**
- **`schema_admin` cannot see other sessions in `pg_stat_activity`** — you get
  `<insufficient privilege>`. **Use `pg_locks`**, which is readable and shows
  which relations a transaction has touched. That is how the stalled load was
  diagnosed.
- **`pg_stat_database` counters do not flush mid-transaction.** `tup_inserted`
  reading 0 during a long load means nothing. I drew a conclusion from it and was
  wrong (**F-032**).

## 1.7 Both FSDS archives are already on disk

```
C:\Users\mdk32\AppData\Local\Temp\claude\C--Windows-system32\5c1bb862-f852-4bd5-a528-60961a83dd7c\scratchpad\2026q2.zip   60,419,016 bytes  sha256 d7c815395cd420cf…
C:\Users\mdk32\AppData\Local\Temp\claude\C--Windows-system32\5c1bb862-f852-4bd5-a528-60961a83dd7c\scratchpad\2015q2.zip   78,908,272 bytes  sha256 d3cac325930af6ef…
```

**139 MB, already fetched through the rate-limited client.** (At closeout: 2026q2: present, 2015q2: present. **This is a session-scoped temp directory - if it has been cleared, refetch through `ingest.edgar.EdgarClient`, never with a bare HTTP call.**) Do not refetch to
experiment. `tools/check_segments_grammar.py` caches to the same place.

## 1.8 The document relay is asymmetric, and the asymmetry is the point

| Direction | Mechanism | Lossy? |
|---|---|---|
| **Planner → Code** | committed to `docs/planner/` on receipt | **No, after receipt** |
| **Code → Planner** | written to the owner's Downloads, hand-carried | **Yes** |

- **The Planner-side manifest chain is RETIRED.** The Code-side chain is
  **RETAINED** and is not covered by that retirement.
- **Regenerate the indexes in the same commit** that adds documents:
  `tools/planner_index.py` and `tools/reports_index.py`, both with `--check`.
  A stale index is indistinguishable from a complete one, and these are the only
  doors — GitHub disallows automated reads of `/tree/` views.
- **Select Planner documents by EXCLUDING Code-authored ones**, never by an
  include-pattern. `*-Planner-*` silently missed 11 documents including all seven
  `RULING-RECORD-*` files, which carry the owner's own rulings, and would have
  missed `RECOVERY-Planner-*`, a prefix that did not exist when it was written.

## 1.9 The failure shapes this project keeps producing

Six months of findings reduce to four sentences. **Every one of them cost real
time, and three recurred on the final day.**

1. **A check that cannot run reports the same thing as a system with no
   defects.** Make every harness prove it executed — print the intermediate
   count, assert a specific expectation, not merely an absence of error.
2. **A guard is only as wide as what it enumerates.** A2 enumerated a schema and
   called it catalogue derivation. A5 tested a proxy and called it the property.
   Prefer excluding what is known-safe over including what is known-relevant.
3. **An improvement that works in one direction is not symmetric**, and the
   direction it does not cover keeps the old failure mode.
4. **A rule is indexed by the situation that produced it**, and the next
   situation arrives without consulting it. I recorded
   *a-measurement-that-decides-nothing* on one day and proposed exactly such a
   measurement the next.

## 1.10 The thing to hold on to

> **The store holds 3.37 million real facts and nothing reads them.**

Every remaining infrastructure task is genuinely unblocked and none of it moves
the product. **The application's critical path is §11.1 and §5.4** — deferred to
"its own session" on day one, **never scheduled** (P-13). Building more store
while that sits is the bog this project already measured once.

---

# PART 2 — State

## 2.1 Repository

**HEAD `9de8150`, 55 commits ahead of `main`, pushed, clean. 96/96.**
PR-6: https://github.com/mdk32366/StockGraderMDK/pull/6

## 2.2 The cluster — and what is deliberately NOT done

`kzpwm0j1dm204nv3` / `stockgrader-db-r1`, **PostgreSQL 16.15**, Basic, 15 GB.

| | |
|---|---|
| `stockgrader_scratch` | 0001–0004 applied · **3,368,813 facts** · 195 quarantined · 7,714 filings · 6,179 filers · 1 coverage row |
| `stockgrader` | **untouched** |
| Roles | `fly-user` (compromised), `stockgradermdk` (compromised), `stockgrader_app` (writer), **`stockgrader_schema_admin`** (clean, proven) |

**Standing constraints, unchanged:**

- **No cluster is destroyed.** Building is unrestricted; anything built is named
  and recorded with a stated end condition.
- **OPEN-27 steps 4 and 5 are NOT started.** Both compromised roles are live.
- **OPEN-25's cheap window is now CLOSING** — `stockgrader_scratch` holds
  objects, and a role that owns objects is a different problem from one that does
  not.

## 2.3 What is built

| | Status |
|---|---|
| `db/migrate.py` | D-021 runner. Owns the transaction, refuses transaction control, advisory lock, sha256 ledger, forward-only. **Proven on 16.15.** |
| `0001` fact store | Applied. The uniqueness key makes overwrite-on-amendment *unavailable*. |
| `0002` fetch provenance | Applied. `source_fetch_id NOT NULL`; refusal-to-backfill is executable. |
| `0003` provenance + quarantine | Applied. A2 derived from the catalogue across all non-system schemas; `fact_collision` keeps both sides. |
| `0004` coverage window | Applied. Coverage as **data**; the accounting CHECK; gaps reported. |
| `ingest/edgar.py` | Rate-limited client, declared User-Agent, no retry that hides a 403. |
| `ingest/slice1.py` | Filers/tickers/filings parsing and loading. **Never run against the cluster.** |
| `ingest/fsds.py` | The fact loader. COPY into staging + server-side insert. |
| `tools/load_quarter.py` | One quarter, one transaction. `--submissions`, `--defer-indexes`, `--dry-run`. |
| `tools/redtest_0003.py` | 8 red-test cases for 0003's guards. |
| `tools/e2e_fsds.py` | End-to-end loader proof on a throwaway cluster. |
| `tools/confirm_restartable.py` | The three restart properties. |
| `tools/check_segments_grammar.py` | Grammar measurement against real archives. |
| `tools/planner_index.py` / `reports_index.py` | Index generation, `--check` for staleness. |
| `app/` | **`/healthz` and `/v1/meta` only. No DB-backed endpoint exists.** |

**Not built:** the GQS normalization layer (the TDD's largest single piece), the
archetype classifier, any scoring, any UI.

---

# PART 3 — What actually gates what

**36 open items. Most are notes.** These are the ones that gate something.

## 3.1 With the owner

| | |
|---|---|
| **OPEN-64** | **Precondition ANSWERED by this context.** 179,806 valueless rows, **all published empty, zero parse failures** — so by the Planner's ruling they are **nil assertions, data**. Store distinguishably from zero ⇒ **0005**, because `fact.value` is NOT NULL and data now exists. **Needs the go-ahead.** |
| **OPEN-25** | Drop `stockgradermdk`, replace `fly-user`. **The cheap window is closing.** |
| **OPEN-63** | Rotate `stockgrader_app` — deferred by the owner, recorded so the deferral has an end. |
| **OPEN-17 / 19 / 9 / 46** | Accruals formulation; fund sequencing; the price vendor's three disqualifying properties; the `current_*` upsert and its provenance together. |
| **§11.1 / §5.4** | **The application's critical path.** P-13. |

## 3.2 Sweep candidates

The register has **duplicate rows** for OPEN-40, OPEN-41 and OPEN-44 — an
answered entry and an open one for the same number. **OPEN-41 is retired on
evidence** (1,908,661 instants all collapsed to a point, 1,460,152 durations
none, on 3.37M real rows) but still shows as open.

**A fresh context inheriting 36 open items inherits the bog with them.** The
sweep is the Planner's to propose and the Builder's to apply.

---

# PART 4 — The prework: what to do first

**In order. The first is small and the second is the one that matters.**

### 1. Sweep the register (Planner proposes, Builder applies)

Collapse the duplicates, close OPEN-41, and demote every item that has gated
nothing in 48 hours to a note.

### 2. Schedule §11.1 and §5.4

**This is the whole of P-13 and it is the only thing on the product's critical
path.** It is not database work and it has never been scheduled. Everything in
Part 3.1 can be true and the product still does not exist.

### 3. Then, and only as far as it helps §2

- **0005** — nil assertions, once OPEN-64 is signed off.
- **The first DB-backed endpoint.** Real data is behind it now. Closes D-029's
  application half and moves recovery row 4 off `Never`.
- **OPEN-33's acceptance test** — CIK 806085 (Lehman) present with filings ending
  2008. Requires `submissions.zip`, which FSDS does **not** substitute for.
- **The 45-quarter load.** ~34 h, unattended, **restart is free and confirmed**
  (F-034). No optimisation needed; `--defer-indexes` is built and deliberately
  unused.

---

# PART 5 — What this sitting established

Recorded so the next context does not re-derive it.

- **The largest unvalidated assumption is retired.** Four migrations, a runner
  and a loader that had only ever met deleted local clusters now hold 3.37M real
  facts, with **every counter identical across PostgreSQL 16.15 and 18.3**.
- **OPEN-30 closed** — the live major was unestablished for two days.
- **OPEN-41 retired on real data** — the silent off-by-one-quarter risk is gone.
- **OPEN-59, OPEN-60, OPEN-65 closed.** OPEN-65 closed **without** the
  measurement I proposed, because no decision turned on it.
- **The quarantine caught the case the register predicted** —
  `DerivativeAssetFairValueGrossLiability`, −3,123,000 and 706,000, both stored.
- **The `segments` grammar is undocumented** and the data carries a broken HTML
  entity; fixed structurally, 100% acceptance across two quarters eleven years
  apart.
- **A2 fired on first contact with a real database**, on a safety marker whose
  existence is environment-dependent by design. Two correct guards in conflict,
  resolved conditionally. **Undiscoverable hermetically.**

**And the honest column.** In this sitting I: put a credential-shaped instruction
in front of the owner (F-021); misread `pg_stat_database` and drew a conclusion
from it; left `executemany` in one insert path after converting the others;
printed `DEFINITIONS IDENTICAL` from a check whose rebuild had crashed; and
proposed a measurement with no decision behind it one day after recording that
exact finding.

**Five of the six were caught by something that forced the question** — a
constraint refusing a row, a lock table, a ruling. **That is the argument for the
guards, and it is the only argument that matters.**
