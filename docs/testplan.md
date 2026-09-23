# Test plan — What would catch it if it broke?

## The gate (Day-One Step 14): PROVEN 2026-09-22

| Date | Broke what | Gate blocked? | Fixed + merged | Shipped + live SHA verified? |
|---|---|---|---|---|
| 2026-09-22 | `app/auth.py`: bypassed `compare_digest`, so any non-None key was accepted (`test_meta_with_wrong_key_is_401` red) | **Yes.** `test` failed, `deploy` was skipped (`needs: test`), and the PR reported `mergeStateStatus: BLOCKED`. Red run: [35754766404](https://github.com/mdk32366/StockGraderMDK/actions/runs/35754766404) | PR-1, second commit reverts the bypass | **Yes.** Merge run [35754987995](https://github.com/mdk32366/StockGraderMDK/actions/runs/35754987995); live `/healthz` build = `ae4e61acf61e5df41e30c44d69a49c68188bf095` on attempt 1 |

Record it here the day you watch it block AND ship with your own eyes.
Branch protection (Step 15) must require the status check named **`test`**.

## Guard proofs (KEEL Principle 6): each broken on purpose, each seen red

All trips were done 2026-09-22 in the Planner container. Every red was a
**failure** (the assertion executed), not an error.

| ID | Mutation | Went red |
|---|---|---|
| G-1 | Removed auth's "server key unset → 503" branch | `test_unconfigured_server_fails_closed[None]` and `[""]`. The `""` case is the discriminating one: client key `""` against server key `""` passes `compare_digest`, so only the fail-closed branch stands between that request and a 200. |
| G-2 | **Not a trip.** Coverage was claimed by reference to existing tests, with no mutation. Superseded by B-11, which mutated the comparison and watched it go red. | (see B-11) |
| G-3 | Session guard, end to end: `DATABASE_URL` = tunnel-style localhost URL, no confirmation | pytest exited with code **3**, `KEEL DB GUARD REFUSED`, before any test ran |
| G-4 | Confirmed, but identity unverifiable (psycopg absent) | refused, exit 3. Unverifiable is treated as unsafe. |
| G-5 | Removed factor 1 (confirmation sentence) from the guard | `test_tunnel_localhost_without_confirmation...`, `test_near_miss_confirmation...` |
| G-6 | Removed factor 2 (canary check) | `test_missing_canary_is_refused` |
| G-7 | *(Bundled: three mutations in one run. See the one-mutation-per-trip convention below.)* Put the confirmation sentence in a local `.env`; planted a password URL and a direct `psycopg.connect` in a test | `test_confirmation_variable_never_lives_in_an_env_file`, `test_no_secrets...`, `test_tests_never_open_database_connections_directly` |
| G-8 | Added an undeclared endpoint | `test_openapi_matches_committed_contract` |
| G-9 | (F-006, D-013) Ran the new `.ps1` guard against the unfixed v3 `setup.ps1`; then, on the fixed file, re-inserted an em-dash with the BOM kept (A), and stripped the BOM from an ASCII body (B) | `test_powershell_scripts_are_safe_for_windows_powershell_5`, all three times. v3 reported the BOM plus `e2 80 94` on lines 1 and 27; A reported line 27; B reported the BOM. Each half bites alone. |

## Independent guard trips by the Builder (blind, 2026-09-22)

Designed from the implementation without reading G-1..G-9. Run on the owner's
workstation (Windows, PS 5.1, Python 3.12.10). Each trip was reverted and
re-greened, and the tree was confirmed byte-identical to v4 afterwards. **Every
red was FAILED; none was ERROR.**

| ID | Guard | Mutation | Went red |
|---|---|---|---|
| B-1 | auth fails closed | unconfigured-server branch `raise` → `return` | `test_unconfigured_server_fails_closed[None]` and `[""]` |
| B-2 | DB factor 1 | exact-sentence match → any non-empty value | `test_near_miss_confirmation_is_refused` |
| B-3 | DB factor 2 | canary check → `if False` | `test_missing_canary_is_refused` |
| B-4 | row tripwire | `> MAX` → `> MAX + 1` (off by one) | `test_row_tripwire_refuses_one_over_the_ceiling` |
| B-5 | env-file ban | `.env` holding the confirmation sentence | `test_confirmation_variable_never_lives_in_an_env_file` |
| B-6 | secret scan | untracked file with a fabricated password URL | `test_no_secrets_anywhere_in_the_working_tree` |
| B-7a/b | direct-connect ban | `psycopg2.connect(`, then `create_engine(`, in uncalled helpers | `test_tests_never_open_database_connections_directly` (both) |
| B-8 | contract drift | undeclared `GET /v1/undeclared` | `test_openapi_matches_committed_contract` |
| B-9a/b | `.ps1` guard | BOM stripped (ASCII body); then BOM kept with an em-dash re-inserted | `test_powershell_scripts_are_safe_for_windows_powershell_5` (both) |
| B-10 | probe failure, end to end | `DATABASE_URL` set **and** sentence typed; psycopg absent | exit **3**, "identity cannot be verified". Confirms G-4. **The Builder's original table missed this path.** |
| B-11 | key comparison | `... or not compare_digest(...)` removed, so any non-None key is accepted | `test_meta_with_wrong_key_is_401` (200 ≠ 401). **Neither original table tripped this.** |
| B-12 | direct-connect ban | `asyncpg.connect(` | `test_tests_never_open_database_connections_directly`. **Untested by either original table.** |
| B-13 | direct-connect ban | `psycopg.connect(`, alone | same test. Isolates the branch G-7 exercised only while bundled. |
| B-14 | `-SuiteOnly` (D-012) | ran `.\setup.ps1 -SuiteOnly` with `.venv` renamed away | threw `-SuiteOnly needs an existing .venv...`; **no `.venv` was created**, so the switch cannot silently defeat D-011 |
| B-15 | warnings-as-errors (D-015) | a test raising a brand new `DeprecationWarning` | **FAILED** -- a new deprecation goes red instead of scrolling past |
| B-16 | warnings-as-errors, direction | no mutation: the two F-007 allowances left in place | 22 passed, 2 warnings. The allowances still report as warnings, so they stay visible rather than becoming errors or disappearing |

Session guard end to end (Builder Step 4): a tunnel-style `DATABASE_URL` with no
confirmation → exit **3**, `KEEL DB GUARD REFUSED`, before collection.

**Comparison with G-1..G-9 (done 2026-09-22, Builder, after its B-table was fixed):**
- **Gaps in G:**
  - No row-tripwire trip, although the Planner's own order listed it as required
    coverage. B-4 is the only trip of it.
  - No mutation of the key comparison (G-2 was by reference). Closed by B-11.
  - The `asyncpg` branch was untested. Closed by B-12.
- **Gap in B:** the probe-failure path (G-4). Closed by B-10.
- **No code change was needed.** In every case the test that should catch the
  mutation already existed and did.
- **The record is the union of G and B.** G numbers are the Planner's trips and B
  numbers are the Builder's. Rows are not duplicated across tables.

**Trip convention:** one mutation per trip. A bundled trip (G-7) cannot
distinguish "each guard fired" from "guards fired for overlapping reasons"
without reading the failure list line by line. Every direct-connect regex branch
(`psycopg`, `psycopg2`, `asyncpg`, `create_engine`) needs its own trip: an
alternation is only as good as its least-tested branch.

## How to read a red

- **A test file that fails to import aborts collection before
  `test_hygiene.py` reports.** The run is still red, so the direction is safe,
  but the red names the import, not the hygiene rule the file may also break.
  Fix the import, re-run, then read hygiene's verdict. (Builder §6.1: a first
  trip file importing an uninstalled `psycopg2` produced ERROR, which was the
  mutation failing, not the guard.)

- **A patch that fails to apply on Windows only is line endings first.** Check
  `.gitattributes` is present and still says `* text=auto eol=lf`, then check
  whether the working-tree file has CRLF. `core.autocrlf = true` on the
  workstation makes this the likely cause, and the git error never names it
  (F-010).

- **When doctrine and a checklist disagree, the checklist is what gets
  followed.** An amendment lands in both or it has not landed. The essay is read
  once; the checklist is read on day one, by someone deciding what to do next
  (F-013).

## Open items. Each blocks something specific.

| ID | Item | Blocks |
|---|---|---|
| ~~OPEN-1~~ | **CLOSED 2026-09-22.** `postgres_probe` ran against Fly Managed Postgres cluster `d1zj5omk443ryqkv`: **accepted** `stockgrader_scratch` (canary present, 0 rows) and **refused** `stockgrader` (no canary). Proven again end to end through `pytest_sessionstart` - see the real-cluster trips below. | - |
| ~~OPEN-2~~ | **CLOSED 2026-09-22.** Built on the first deploy: 48 MB image, pushed to `registry.fly.io/stockgradermdk`, running live. It did fail on first deploy -- on `primary_region`, not the image (F-011). | — |
| ~~OPEN-3~~ | **CLOSED 2026-09-22 by F-008.** Reproduced on the owner's machine: 22/22, egress-blocked. | — |
| ~~OPEN-4~~ | **CLOSED 2026-09-22 by F-008.** Windows PowerShell 5.1.26100.9444 parsed and ran the fixed `setup.ps1`. | — |
| OPEN-7 | **Do a full backup's children expire with it?** B-6a. Backup IDs are chains (`<FULL>_<CHILD>`) and children are not independently restorable, so the recovery horizon is bounded by the oldest surviving **full** - but expiry behaviour is unverified. `20260922-192041F` should age out ~2026-10-02. **Run `fly mpg backup list d1zj5omk443ryqkv --all` on 2026-10-03** and record whether its four children went with it. One read-only command. | Confidence in the stated recovery horizon (B-6). |
| OPEN-8 | **The PITR recovery window is unmeasured.** `--pitr-time` exists but no command reports the window it requires (`F-next/pitr-available-window-invisible`). B-9 proposes measuring it with one deliberate refusal against a throwaway cluster. **Owner's call, optional, and only after the restore drill.** Until then PITR stays unused and `--backup-id` is the only path. | Any use of PITR. |
| OPEN-9 | **The price vendor is unchosen. HALF ANSWERED 2026-09-23 - deliberately not marked closed.** **EODHD delisted coverage is documented and specific:** a `delisted=1` flag on the exchange symbol list, ~60,000 delisted US symbols as of 2026-09, with availability tiered by delisting date (pre-2018: end-of-day only). **That tiering does not bite us** - we need only prices from the vendor; fundamentals come from EDGAR under ruling 4, and EDGAR keeps a dead company's filings permanently. **The architecture makes the vendor's main limitation irrelevant, which is an argument for the architecture and not only for the vendor.** **TWO QUESTIONS REMAIN, and they are for the vendors, not for research:** **(1)** Does EODHD serve **as-traded closes** alongside adjusted? Unaddressed in their docs and it is the **disqualifying** property - a back-adjusted close times shares outstanding is a market cap nobody observed. **(2)** **Tiingo's delisted position is unestablished** - no vendor documentation either way, only forum commentary, recorded as anecdote not evidence. **Preliminary read, not a recommendation:** EODHD has answered the harder question in writing; Tiingo has not answered it at all. That is a difference in what is **established**, not necessarily in what is **true**. | Any price ingest; the universe's integrity (ruling 5); the valuation block. |
| ~~OPEN-10~~ | **CLOSED 2026-09-23 by owner ruling 11 (revised record).** Altman **Z'** - private-firm form, book value of equity. A gate built on market equity would disqualify a company on a day its fundamentals did not change; ruling 4 made market equity available, so this is a design choice made with the alternative in hand. | - |
| OPEN-11 | **Archetype classifier fallback trigger (ruling 13).** §11.2 is RULED as option (c), Lynch archetypes with per-archetype metric sets. **This item is the watch, not the question.** Fall back to **SIC-as-is** if EITHER: (a) the classifier is still unspecified when every other §13 condition has cleared, or (b) a hand-check finds it assigns archetypes the owner disagrees with more often than agrees. The classifier must be specified independently and **frozen before scoring runs** - tuning it until the rankings look right is the failure mode, and it is quiet. | Scoring build order; the credibility of every sector-relative rank. |
| ~~OPEN-12~~ | **ANSWERED 2026-09-23. N-CEN is the wrong form.** The SEC does publish N-CEN Data Sets, but N-CEN is a census of fund **operations** - service providers, auditors, custodians, board and compliance structure, ETF authorized-participant data. **Not fees, not turnover.** They live in **Financial Highlights** (485BPOS prospectus, N-CSR shareholder report) as a multi-year table - **HTML/prose, not structured** - and in **Inline XBRL** under the Tailored Shareholder Reports rule, which is the structured path and is recent. **Recent years cheap, history expensive.** Sequencing consequence in OPEN-19; date to confirm in OPEN-20. | - |
| ~~OPEN-13~~ | **CLOSED 2026-09-23.** Both load-bearing citations **verified** against primary sources. **Novy-Marx** (JFE 108(1), 1-28, 2013): GP/A, gross profit over **book value of total assets** - *not book equity*, which several later papers use and which yields a different factor. §4.2 must say total assets explicitly. **Sloan** (The Accounting Review 71(3), 289-315, 1996): the original is the **balance-sheet** formulation scaled by **average** total assets. Verification raised F-E - see OPEN-17. The remaining eight citations in lineage §11 are unverified and **not load-bearing for the source map**. | - |
| OPEN-14 | **The D-019 promotion is ruled but NOT APPLIED.** Branch protection is a repository settings change, not a commit, and the Builder's attempt was stopped at its permission boundary. Current required contexts on `main`: **`test` only.** To apply: add **`windows-setup (PS 5.1)`** - the exact reported context, **not** `windows-setup`, which the promotion ruling named and which nothing ever reports (P-8; §2 of that ruling is superseded) (`F-next/required-check-context-name`). Then confirm PR-6 still shows mergeable. | D-019 being true rather than ruled. |
| OPEN-15 | **A required check that has never refused anything is required in name.** Promotion is verified when a PR shows `windows-setup` as **Required** - that proves the setting took, **not that the block works.** The proof in the refusing direction is **a deliberate red that blocks a merge**, on a throwaway branch with an intentionally broken Windows setup step - the same both-directions discipline the deploy gate was proven under. **Not scheduled today**, and recorded so it is a thing we have not done rather than a thing we believe. | Confidence that D-019 blocks anything. |
| OPEN-16 | **A gate matrix change renames the required context, silently.** `windows-setup (PS 5.1)` is the job key plus its matrix dimensions. Change the dimensions - adding PowerShell 7, say - and the required check becomes one that **never reports**: permanently pending, blocking every merge, **with no change to the protection rule to point at.** **Guard: any change to the gate's matrix requires re-reading the reported contexts (`gh api repos/.../commits/<sha>/check-runs`) and updating branch protection in the same change.** Recorded as an action because the observation will not survive six months. | Every merge to `main`, at the moment the matrix changes. |
| OPEN-17 | **[OWNER RULING] The accruals formulation, and it is not a detail.** Sloan's original is balance-sheet differencing; the cash-flow method (earnings minus operating cash flow) is the alternative. **They disagree most for companies with acquisitions, divestitures or discontinued operations** - a balance-sheet difference reads an acquired subsidiary's working capital as if the company had generated it. **Those are exactly the companies §4.1's organic-vs-acquired proxy exists to catch**, so the gate and the growth block would measure the same fact with one doing it wrongly. **Planner recommends the cash-flow formulation, recorded as a deliberate departure from Sloan rather than an implementation shortcut.** Changes §4.3's stated basis. | §4.3's basis; the integrity gate's behaviour on acquisitive companies. |
| OPEN-18 | **Lineage edit - separate the accounting-quality argument from the return-prediction claim.** The accruals anomaly reportedly decayed after ~2002. Lineage calls Sloan *the most operationally important result in the literature*, which is a claim about **return prediction** and is now weaker than stated. **§4.3 survives on a better argument:** accruals-driven earnings reverse, and a buy-and-hold model has no business rating a company highly on earnings about to reverse - **whether or not the market still pays for the distinction.** That is accounting quality, not a factor claim. Edit lineage §5 and §9's third axiom. | Nothing operational; the honesty of the stated rationale. |
| OPEN-19 | **[OWNER SEQUENCING] The fund score's cheap work and its validating work are not the same work.** Current expense ratios are obtainable from Inline XBRL (Tailored Shareholder Reports, Item 27A of N-1A). **A ten-year series is not** - it means parsing Financial Highlights tables out of 485BPOS/N-CSR, per share class, across filers with no common layout. D-027's honest null (*does look-through add anything over expense ratio and turnover alone?*) **needs the historical series**, i.e. the expensive half; the look-through half is cheap because N-PORT is structured. **Building the cheap half first produces a fund score whose central question stays untested indefinitely.** Owner's call, not the Planner's. | D-027's pre-registered validation. |
| OPEN-20 | **Confirm the Tailored Shareholder Reports compliance date** before scoping any Inline-XBRL fee parser - it decides how many years of tagged data exist. **Unconfirmed and stated as such by the Planner.** | Scoping OPEN-19's cheap half. |
| OPEN-21 | **Which endpoint does the migration runner use, and in what pooler mode?** The attached `DATABASE_URL` points at **`pgbouncer.kzpwm0j1dm204nv3.flympg.net`**, not the `direct.` endpoint. A transaction-mode pooler interferes with **prepared statements, session-level settings and advisory locks** - all of which a D-021 migration runner typically uses. **Unestablished:** the pooler's mode, and whether `direct.` is reachable with the same credential. **Settle before migration 0001 runs against this cluster**, not during. | Migration 0001's run against `stockgrader-db-r1`. |
| OPEN-22 | **The restored cluster's disk is 15 GB; the source was 10 GB** (`F-next/restore-resizes-disk`). Decide whether that is accepted or corrected. **This has a deadline:** the 10 GB original is the only surviving record of the intended configuration and **it disappears when the old cluster is destroyed** after the ticker load. | Nothing operational; the record of what was intended, and the separately-billed cost. |
| OPEN-23 | **The old cluster is still attached to the app.** `fly mpg list` shows `stockgradermdk` in ATTACHED APPS for **both** clusters - the cutover re-pointed the secret but never ran `fly mpg detach`. **The column records history, not current state**, so it cannot answer which cluster the app uses; only the host inside `DATABASE_URL` can, and that cannot be read without exposing the credential. Resolve at destroy time - detaching now may interact with the live secret and the old cluster is deliberately retained. | Nothing operational; the ability to answer *what is this app connected to* during an incident. |
| ~~OPEN-24~~ | **ANSWERED 2026-09-23. Did the restore carry the role catalogue? YES.** Raised in delivery **D9, which never arrived** - the Builder learned of this item only from D10's ruling citing it. `fly mpg users list kzpwm0j1dm204nv3` returns `fly-user` (schema_admin), `stockgrader_app` (writer), `stockgradermdk` (schema_admin). See `F-next/restore-carries-compromised-roles`. | - |
| OPEN-25 | **[OWNER] Remove the carried compromised roles - GATED, and the gate is a deadline.** **Migration 0001 does not run against `stockgrader-db-r1` until this is done, or until the owner lifts the gate.** Its design (D8) is unaffected and proceeds. **Why now:** `stockgrader` and `stockgrader_scratch` hold no owned objects except the canary, so a role drop is near-free. **Once 0001 creates tables those tables have an owner**, and dropping an owning role fails until ownership is reassigned (`REASSIGN OWNED` / `DROP OWNED`) against the right database by an account with the right rights. **The work is small; it is only small today.** **§5.1 ESTABLISHED by the Builder (read-only):** `fly mpg users delete <CLUSTER_ID> -u <name> [-y]` exists, and `fly mpg users set-role` alongside it - **so this is CLI, not a SQL-over-proxy handover.** **Still to establish:** (5.2) whether `stockgradermdk` owns the phase-0 canary table - check before attempting, not after a failure; (5.3) drop `stockgradermdk`, which is not the app's path and should break nothing - confirm it does not; (5.4) **`fly-user` must NOT be dropped reflexively** - it is the Step 16 recovery account, and removing the recovery path to fix a credential exposure is a poor trade. Establish whether a replacement `schema_admin` can be created and `fly-user` deleted, or whether `fly-user` is MPG-provisioned and undroppable - if undroppable the answer is rotation, and D-030's exception applies. | Migration 0001's run phase; D-029's closure path, which currently does not exist. |
| ~~OPEN-26~~ | **ANSWERED 2026-09-23, read-only.** `fly mpg users create --help` exposes **only** `-h`, `-r/--role`, `-u/--username` - **no flag emits a password or connection string**, and `fly mpg users` has no `rotate`. So no CLI command hands back a credential. **But Step 16 is manual, not nominal:** per F-019 passwords are settable by a human in the Fly dashboard, so a replacement `schema_admin` **is** obtainable - create via CLI, set the password in the dashboard, store it in the password manager. **The bad trade in §5.4 is therefore avoidable.** See `F-next/no-cli-path-to-a-recovery-credential`. | - |
| OPEN-27 | **[OWNER] Stand up a clean `schema_admin`, then drop the compromised pair - IN THIS ORDER.** Migration 0001 cannot run as `stockgrader_app`: A-017 established a `writer` is refused `CREATE TABLE`, **by design** (D-021, D-031). The only two `schema_admin`s on the live cluster are `fly-user` and `stockgradermdk`, **both compromised 2026-09-22 and both carried across by the restore.** **The order is the whole control** - done backwards it removes the only account that can run 0001. **1.** Create the clean `schema_admin` on `kzpwm0j1dm204nv3`. **2.** Set its password **in the dashboard**; store it in the password manager under the project name. **3. PROVE IT** - connect over `fly mpg proxy` to `stockgrader_scratch`, `CREATE TABLE`, drop it. **Report after step 3, before step 4.** **4.** Drop `stockgradermdk`. **5.** Handle `fly-user` - replacement first, proven the same way. **Why step 3 is not ceremony:** *created-and-given-a-password* is an account that **looks** usable; *connected-and-ran-DDL* is a usable account. D-029 already states this rule for a different object - a rotation is complete when a live request proves the new credential is in use, not when the password changes. **The gap between those two claims is where Row 4 has sat all day.** **One thing in step 2 is unestablished:** F-019 records a human setting a password in the dashboard, but for an **existing** account. Whether it works for a **freshly created** MPG user has not been seen. If it does not, step 2 fails - and the ordering means it fails while both compromised accounts still exist and the recovery path is intact. | Migration 0001's run phase; OPEN-25's ordering; D-029's closure path. |
| ~~OPEN-28~~ | **CLOSED 2026-09-23. The runner is built:** `db/migrate.py`. Owns the transaction and the advisory lock; **refuses any migration or verification file containing transaction control** (the PharmFoldMDK §3.1 defect, made impossible rather than discouraged); forward-only with gap and duplicate-version refusal; **sha256 in the ledger, written by the runner in the same transaction as the DDL**; verification inside a savepoint so a failed check takes the migration down with it. `status`/`plan` read-only, `apply` explicit. **21 hermetic tests; every guard seen red against a local throwaway cluster.** See `F-next/migration-runner-proven`. | - |
| ~~OPEN-29~~ | **CLOSED 2026-09-23. The entity WAS missing from the fact key** - possibility (3). An XBRL context carries an entity as well as a period and dimensions; the key carried period and dimensions and not the entity. Two co-registrants reporting the same concept, period and unit with no dimensions would have collided, and `ON CONFLICT DO NOTHING` would have discarded the second **while calling it idempotency**. Fixed: `entity_cik bigint NOT NULL REFERENCES filer (cik)`, **in the key**. Amending 0001 rather than writing 0002 is legitimate because **0001 has never been applied to any real database**. Caught now by **A8** (structural) and by the co-registrant fixture (behavioural), independently. See `F-next/entity-missing-from-fact-key`. | - |
| OPEN-30 | **The live cluster's PostgreSQL major version is unestablished.** 0001 was proven on local **18.3**; `kzpwm0j1dm204nv3` runs an unknown major. Generated-column syntax, `jsonb` operator behaviour, exclusion-constraint support and `NULLS NOT DISTINCT` have all moved between recent majors, so hermetic-against-the-wrong-major proves the migration runs **somewhere**. **Partly established credential-free 2026-09-23:** `fly mpg databases extensions list kzpwm0j1dm204nv3 -d stockgrader` works without a connection and **confirms `btree_gist` is available**, which 0001 requires. **It does not expose the server version**, and no `fly mpg` command does. **Cheapest resolution: fold it into OPEN-27 step 3.** The owner is already connecting to prove the new `schema_admin`; `SELECT version();` in that same session costs nothing and answers this. **If the major differs from 18, re-prove 0001 on the matching major before the runner applies it** - the scratchpad cost is low enough that re-running is not an argument against it. | Migration 0001's run phase. |

## D-019 counter - RETIRED 2026-09-23. `windows-setup` is a required check.

**RETIRED.** The threshold was met and D-019 was ruled: `windows-setup` is
promoted to a required check. The table below is kept as the evidence the ruling
was made on, not as a live count.

*Original terms: promotion was an owner ruling at 10, reset to zero on any red,
and the count was structurally one behind - a count committed to the repo cannot
include the run that validates the commit recording it. That tolerated lag is
what let a real two-run drift hide; see `F-next/tolerated-error-hides-real-error`.*

**Final count: 10 of 10** - threshold met 2026-09-23, **RULED, counter closed.**

**Caught up by 3, and two of them had been missed.** Runs 7 and 8 are PR-5's,
from 2026-09-22T20:59-21:00Z - they completed green and were never recorded,
because PR-5 merged after the count line was last written. **The counter had
silently fallen two behind**, which is the same shape as F-018: the work
outran its record, and nothing in the document revealed it. Recovered from
`gh run list`, not from memory.

**RULED 2026-09-23:** promoted. Ten consecutive green runs, no reds, across five
branches and four merges to `main`. **A red on Windows now blocks merge.**
The caveat is recorded with the ruling in D-019: ten runs of a repo with 22 tests
and almost no application code, never stressed by dependency churn - and ingest
is exactly what stresses a Windows setup path. **That is the argument for
promoting now rather than after.**
**Implementation is not done** - see OPEN-14 and OPEN-15.

| # | Run | Branch |
|---|---|---|
| 1 | [35755627563](https://github.com/mdk32366/StockGraderMDK/actions/runs/35755627563) | pr3-code-d012-d014-d015 |
| 2 | [35755827105](https://github.com/mdk32366/StockGraderMDK/actions/runs/35755827105) | pr3-code-d012-d014-d015 |
| 3 | [35755972455](https://github.com/mdk32366/StockGraderMDK/actions/runs/35755972455) | main (PR-3 merge) |
| 4 | [35761835450](https://github.com/mdk32366/StockGraderMDK/actions/runs/35761835450) | pr4-d020-visibility |
| 5 | [35765068869](https://github.com/mdk32366/StockGraderMDK/actions/runs/35765068869) | pr4-d020-visibility |
| 6 | [35765196736](https://github.com/mdk32366/StockGraderMDK/actions/runs/35765196736) | main (PR-4 merge) |
| 7 | [35783781284](https://github.com/mdk32366/StockGraderMDK/actions/runs/35783781284) | pr5-register-catchup *(unrecorded until 2026-09-23)* |
| 8 | [35783912646](https://github.com/mdk32366/StockGraderMDK/actions/runs/35783912646) | main (PR-5 merge) *(unrecorded until 2026-09-23)* |
| 9 | [35877548924](https://github.com/mdk32366/StockGraderMDK/actions/runs/35877548924) | pr6-backup-strategy |
| 10 | [35877772087](https://github.com/mdk32366/StockGraderMDK/actions/runs/35877772087) | pr6-backup-strategy |

## Real-cluster proofs (OPEN-1), 2026-09-22

Cluster `d1zj5omk443ryqkv`. **`stockgrader` and `stockgrader_scratch` sit on the
same cluster, same host, same port, and were probed by the same user.** Nothing
but the canary table distinguishes them. That is what makes this proof of
**positive identity** rather than proof of a working query: a guard that read
the hostname would have accepted both.

| ID | Condition | Expected | Observed |
|---|---|---|---|
| R-1 | `postgres_probe` against `stockgrader_scratch` | accept | `canary_present=True`, `max_table_rows=0` -> **ACCEPTED, `DISPOSABLE_VERIFIED`** |
| R-2 | `postgres_probe` against `stockgrader` (production) | refuse | `canary_present=False` -> **REFUSED**, "Canary table keel_disposable_canary not found" |
| R-3 | Full suite, `DATABASE_URL`=scratch, sentence typed | suite runs | **22 passed, exit 0** - the first green this suite has produced with a real database armed |
| R-4 | Full suite, `DATABASE_URL`=production, sentence typed | refuse, exit 3 | **exit 3**, `KEEL DB GUARD REFUSED: Canary table ... not found` |
| R-5 | Full suite, `DATABASE_URL`=production, **no** sentence | refuse at factor 1 | **exit 3**, `...KEEL_TEST_DB_DISPOSABLE does not equal the confirmation sentence` |

**R-4 and R-5 are the pair worth keeping.** They are two *different* refusals of
the same production database, from two independent barriers. R-5 never contacts
it at all - factor 1 is checked before the probe is called, so a shell pointed at
production without the sentence cannot even cause a connection. R-4 connects,
finds no canary, and refuses on identity.

**Probe read-only confirmation:** before pointing it at production, the probe was
confirmed to issue only an `information_schema.tables` existence check, a
`pg_stat_user_tables` listing, and bounded `SELECT count(*)` queries. No DDL, no
writes.

## Open items added 2026-09-22

| ID | Item | Blocks |
|---|---|---|
| OPEN-5 | **Make the gate notice a staged secret.** *(Rewritten 2026-09-23: the item said "the gate cannot see a staged secret." The CLI **does** warn - `There is 1 secret not deployed` - so this was never silent at the human layer. It is silent at the **gate** layer, which never runs `secrets list` and whose live-SHA check reads a build arg baked into the image. "Make the gate notice them" is a different and far more buildable thing than "notice them".)* **Original text:** The gate cannot see a staged secret.** F-015 passed every check we have, including the live-SHA verification, because the SHA is baked into the image and has nothing to do with secrets. A DB-backed endpoint plus a check that it actually answers *from the database* would close this. | Not buildable until such an endpoint exists, so this is an open item, not a guard. It is also what D-029 means by "a rotation is complete when a request to the live service proves the new credential is in use". |
| OPEN-6 | **`pharmfoldmdk` is attached to two MPG clusters**, seen in `fly mpg list`. Out of scope for this project, and flagged because it is PharmFoldMDK's own section 3.1 shape - a write that appears to succeed against a connection nobody proved. | Nothing here. Owner's call, another day. |

## Expected behaviour that is not a fault

- **Live-SHA check passing on attempt 2 or 3.** `fly.toml` scales to zero, so the
  first `/healthz` poll after a deploy can pay a cold start. The budget is 18 ×
  10 s. A late pass is normal. Only exhausting the budget is a fault. (Builder
  report §6.1.)

## Chosen NOT to test, with reasons

- **Fly deploy mechanics inside the hermetic suite.** A hermetic suite can't
  observe a real deploy. It is covered instead by the Step 14 watch and by the
  deploy job's live-SHA check (D-005).
- **Timing-attack resistance of the key comparison.** It uses
  `secrets.compare_digest`; a timing test would be slow and flaky and would
  prove the stdlib, not our code.

## Non-hermetic track (PharmFoldMDK Recommendation A): named, empty

Runs against real services and never in the gate. A hermetic green is never
evidence for anything listed here.

- *(future)* `postgres_probe` against real disposable and non-disposable Postgres
  (closes OPEN-1).
- *(future)* Live SEC EDGAR fetch with the declared User-Agent (A-004).
- *(future)* Live price-vendor fetch (A-003 / D-007).

## GQS §13 completeness gate - current state, 2026-09-23

Recorded from `RULING-RECORD-2026-09-23-...-owner-rulings.md` §4. **This is the
gate that decides whether a scoring build order may issue.** D-010's binding
condition points here.

| §13 condition | State |
|---|---|
| Any §11 question unratified | **OPEN** - 11.1 deferred (ruling 12). **11.2, 11.3, 11.4 ruled.** |
| §5.4 R&D treatment unresolved | **OPEN** - the same question as 11.1 |
| Eligibility table contains an unlisted class | Believed clear; **confirm in v4** |
| Any block contains a placeholder metric | **Confirm in v4** |
| Point-in-time property weakened in build order | Not yet applicable |

**No scoring build order can issue.** **§11.1 is now the only open §11 question**
- 11.2, 11.3 and 11.4 are ruled - and §5.4 is the same question. Two conditions
remain unconfirmed pending v4.

**Ingest is unaffected and proceeds.** The universe, the point-in-time fact
store, and the filing-date/accession discipline are the same work whichever way
the §11 questions land - which is why ruling 5 constrains the first migration
now rather than waiting on the gate.

- *(future)* **Migration runner against a real Postgres** (`F-next/migration-runner-proven`).
  Apply/verify/savepoint-rollback, advisory-lock contention between two
  concurrent runners, and behaviour **through pgbouncer** (OPEN-21) are all
  non-hermetic. They were proven against a local PostgreSQL 18.3 cluster, which
  is **not** the platform's version and **not** through a pooler. A hermetic
  green in the gate is not evidence that a migration applies.
