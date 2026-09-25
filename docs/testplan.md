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
| OPEN-9 | **The price vendor is unchosen. HALF ANSWERED 2026-09-23 - deliberately not marked closed.** **EODHD delisted coverage is documented and specific:** a `delisted=1` flag on the exchange symbol list, ~60,000 delisted US symbols as of 2026-09, with availability tiered by delisting date (pre-2018: end-of-day only). **That tiering does not bite us** - we need only prices from the vendor; fundamentals come from EDGAR under ruling 4, and EDGAR keeps a dead company's filings permanently. **The architecture makes the vendor's main limitation irrelevant, which is an argument for the architecture and not only for the vendor.** **TWO QUESTIONS REMAIN, and they are for the vendors, not for research:** **(1)** Does EODHD serve **as-traded closes** alongside adjusted? Unaddressed in their docs and it is the **disqualifying** property - a back-adjusted close times shares outstanding is a market cap nobody observed. **(2)** **Tiingo's delisted position is unestablished** - no vendor documentation either way, only forum commentary, recorded as anecdote not evidence. **(3) ADDED 2026-09-24: a DELISTING DATE per symbol.** The owner's delisting-eligibility ruling needs listing status **as of D**, and a vendor retaining delisted symbols typically publishes the delisting date alongside them - **exactly what as-of eligibility needs, from a source already required for other reasons.** All three are disqualifying, not preferences. **Preliminary read, not a recommendation:** EODHD has answered the harder question in writing; Tiingo has not answered it at all. That is a difference in what is **established**, not necessarily in what is **true**. | Any price ingest; the universe's integrity (ruling 5); the valuation block. |
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
| OPEN-27 | **STEPS 1-3 COMPLETE 2026-09-25. Steps 4-5 remain and are NOT started.** `stockgrader_schema_admin` created by CLI, password set **in the dashboard**, stored in the password manager, and **PROVEN** - connected over `fly mpg proxy` to `stockgrader_scratch`, ran `CREATE TABLE` / `INSERT` / `SELECT` / `DROP TABLE`, plus `SELECT version();` closing OPEN-30. **No credential entered the transcript.** **The unestablished step is now established (F-028):** F-019 recorded a dashboard password set for an *existing* account; this confirms it for a **freshly created** MPG user, so the platform's recovery path is proven end to end rather than argued. **Migrations 0001-0004 are applied to `stockgrader_scratch`** - the largest unvalidated assumption in the project, settled. **STILL OPEN: step 4** (drop `stockgradermdk`) and **step 5** (`fly-user`, replacement first, proven the same way). Both compromised accounts remain live and the recovery path is intact. | OPEN-25's ordering; D-029's closure path; any migration against `stockgrader` proper. |
| ~~OPEN-28~~ | **CLOSED 2026-09-23. The runner is built:** `db/migrate.py`. Owns the transaction and the advisory lock; **refuses any migration or verification file containing transaction control** (the PharmFoldMDK §3.1 defect, made impossible rather than discouraged); forward-only with gap and duplicate-version refusal; **sha256 in the ledger, written by the runner in the same transaction as the DDL**; verification inside a savepoint so a failed check takes the migration down with it. `status`/`plan` read-only, `apply` explicit. **21 hermetic tests; every guard seen red against a local throwaway cluster.** See `F-next/migration-runner-proven`. | - |
| ~~OPEN-29~~ | **CLOSED 2026-09-23. The entity WAS missing from the fact key** - possibility (3). An XBRL context carries an entity as well as a period and dimensions; the key carried period and dimensions and not the entity. Two co-registrants reporting the same concept, period and unit with no dimensions would have collided, and `ON CONFLICT DO NOTHING` would have discarded the second **while calling it idempotency**. Fixed: `entity_cik bigint NOT NULL REFERENCES filer (cik)`, **in the key**. Amending 0001 rather than writing 0002 is legitimate because **0001 has never been applied to any real database**. Caught now by **A8** (structural) and by the co-registrant fixture (behavioural), independently. See `F-next/entity-missing-from-fact-key`. | - |
| ~~OPEN-30~~ | **CLOSED 2026-09-25. The live cluster runs PostgreSQL 16.15** (`16.15-1.pgdg13+2`), **not 18** - two majors from where 0001-0004, the runner and every verification were proven. Answered by `SELECT version();` folded into OPEN-27 step 3, exactly as proposed, at zero cost. **All four migrations then applied and verified against 16.15 unchanged** - but that is the outcome, not the justification: it was found by applying to a **disposable canary database**, and the ordering is what made a bad outcome survivable rather than what made this one fine. Open since 2026-09-23. See **F-027**. | - |
| ~~OPEN-31~~ | **RULED 2026-09-23 (D15).** `filer` + `filing` from **`submissions.zip`** (all filers, full history); `filer_ticker` from `company_tickers*.json` as the **current-day crosswalk only**. §3's intent unchanged, its inputs replaced. Planner error recorded as **P-10**. | - |
| ~~OPEN-32~~ | **ANSWERED 2026-09-23. `sic_at_filing` has NO source in slice 1 and stays NULL.** The submissions document carries SIC **at entity level only** (`sic`, `sicDescription` - the filer's *current* classification). Its 16 per-filing columns carry **none**. Entity SIC maps to `filer.current_sic`, where it is honest. **Filling `sic_at_filing` from it would put today's classification in a column whose name asserts it is not today's, invisibly and permanently.** Still unestablished and not needed by slice 1: whether per-filing SIC exists in the filing header or the Financial Statement Data Sets. See `F-next/sic-at-filing-has-no-source-in-slice-1`. | - |
| OPEN-33 | **[RUN PHASE] Acceptance test for `submissions.zip`, stated as pass/fail rather than as a claim.** The archive is correct for our purpose if **CIK 806085 (Lehman Brothers Holdings) is present with filings ending in 2008.** That is the property ruling 5 needs, testable, rather than trusting what *"all filers"* means. | Whether the ruled source actually delivers the historical universe. |
| ~~OPEN-34~~ | **CLOSED 2026-09-24 by migration 0002.** `fetch_log` keyed on **(url, retrieved_at)** - a retrieval is an event, not a property of a URL. `source_fetch_id` **NOT NULL** on `filer`, `filer_ticker` and `filing`, so an unprovenanced row is **not representable**. The loader records the fetch first, in the same transaction as the rows it produces. **0002 refuses to backfill** rather than invent provenance, and that refusal is executable. `fetch_content_change` surfaces a changed payload - the case that **retroactively falsifies D-023's re-derivability claim** for rows loaded from the superseded payload. D-023 is now implemented rather than asserted. | - |
| ~~OPEN-36~~ | **RULED 2026-09-24 (D17 §2): the Financial Statement Data Sets.** Decided on **60.7%** - companyfacts would discard the majority of facts filers publish, invisibly. **Ruling 5 one level down:** the ticker files were rejected as structurally incapable of representing a dead company; companyfacts is structurally incapable of representing a dimension or a second entity. The ~50-day lag bites only at a live edge **that does not exist**, and **adding recency later is additive while adding completeness later is a re-ingest**. companyfacts **deferred, not rejected**, gated on OPEN-38. See `D-next/fact-sources`. | - |
| OPEN-37 | **Is `sub.txt.sic` the SIC *as filed* or the filer's SIC *as of extract*?** FSDS `sub.txt` carries per-submission SIC on 97.5% of rows, which answers OPEN-32's open half - `sic_at_filing` **has** a source. But **which of those two things the field means is the entire reason the column exists**, and a 97.5% population rate does not say. **Establish before populating it**; until then the column stays honestly NULL. | `filing.sic_at_filing` ever being filled. |
| OPEN-38 | **Does companyfacts attribute co-registrant facts to the requested CIK?** 61,122 facts per quarter belong to a co-registrant rather than the filer. If companyfacts **excludes** them it merely omits data; if it **returns them under the requested CIK** it records the wrong entity, which is worse than omission and invisible. Unestablished, and it bears on OPEN-36. | Whether companyfacts is safe as a supplementary source. |
| ~~OPEN-39~~ | **ANSWERED 2026-09-24: possibility (3).** `coreg` is free text - **0 of 990 values numeric**, **93.8%** of submissions carrying coreg facts have **no `aciks` at all** to resolve against, and **34.5% of rows** use opaque within-filing codes (`EBP001`) with no external referent. Documentation says *coregistrant of the parent company registrant*, no CIK. **Possibility (2) fails on availability, not matching - the mapping has no domain.** **Consequences:** co-registrant facts are **REFUSED** per the scheme rule (~1.69% of facts), a chosen refusal rather than an emergent rejection rate; **OPEN-36 rests on dimensions alone** and the record now says so; and `entity_cik` will be trivially the filer's CIK - **but as a visible, countable refusal, not an invisible misattribution.** | - |
| ~~OPEN-40~~ | **ANSWERED 2026-09-24 from documentation.** `prevrpt` = *TRUE indicates that the submission information was subsequently amended*. **It marks the ORIGINAL that was later amended** - exactly the value that was knowable at the time. Filtering on it deletes the original and keeps the restatement. **Store the flag; never exclude on it.** | - |
| ~~OPEN-41~~ | **ANSWERED 2026-09-24 from documentation.** `ddate` = period end date; `qtrs` = duration in quarters. **`period_end` = `ddate`; `period_type` = instant when `qtrs=0` else duration; `period_start` = `ddate` for instants (0001's convention) else `ddate` minus `qtrs` quarters.** Corroborated by distribution - `qtrs=0` is **54.9%** of 3.6M rows, which is what a balance-sheet-heavy set should look like and what an inverted reading would have got badly wrong. | - |
| ~~OPEN-42~~ | **ANSWERED 2026-09-24.** FSDS begins **2009q1** (2008q4 and earlier are 404) - but 2009q1 is **13,540 bytes**, effectively empty, and coverage ramps to steady state around **2011q4** (64 MB) as the XBRL mandate phased in. **The nominal start overstates the backtest's reach by nearly three years.** | - |
| OPEN-40 | **`prevrpt` is metadata to record, never a filter to apply.** FSDS flags superseded submissions. **The superseded row IS the value that was knowable then** - exactly what a point-in-time store exists to hold. **Filtering on `prevrpt` would implement the latest-value trap with the platform's assistance.** Store the flag; never exclude on it. Establish its exact semantics before the loader is written. | The point-in-time property, at ingest. |
| OPEN-41 | **The `ddate`/`qtrs` period derivation must be established against documentation, not inferred from samples.** `ddate` is an end date, `qtrs` encodes duration; `period_start`, `period_end` and `period_type` all derive from those two, with instants landing on 0001's `period_start = period_end` convention. **An off-by-one-quarter error here is silent and poisons every growth metric in §4.1** - and a sample-inferred encoding would look right on the samples it was inferred from. | Every §4.1 metric. |
| OPEN-42 | **What is the earliest quarter FSDS publishes?** The TDD requires ≥3 years of filing history for eligibility and the backtest wants considerably more, so **the archive's start date is a hard bound on what can ever be validated.** Establish it before the handover. | The backtest's maximum reach. |
| OPEN-43 | **[BLOCKS AS-OF ELIGIBILITY] There is no delisting date anywhere in the store.** The owner ruled delisted companies out of scope for output and in scope for validation - and **validation needs listing status as of D, which we cannot answer at all.** `filer_ticker.valid_from` is an observation date (OPEN-35), not a listing start. **Until this exists, any backtest must state in its own output which eligibility rule produced it** - a validation result that does not say is not interpretable, and saying it in a document beside the result is not the same thing. See `F-next/bias-can-re-enter-at-the-last-gate`. | Any as-of-date validation. |
| ~~OPEN-44~~ | **ANSWERED 2026-09-24, and it reframes the question.** `submissions.zip` grew **1,565,081,455 -> 1,565,294,470 bytes in 24 hours**. Its contents change nightly because it is a **daily snapshot of a growing dataset** - so whether rebuild nondeterminism exists is **unobservable, because the contents are never unchanged**. A response-level hash of it is therefore a **build identifier, not a change detector**, and `fetch_content_change` would fire on the primary source every night, correctly. **The member is the right unit** - a per-filer JSON stays byte-identical when that filer does not file, and it is what a `filing` row actually derives from. **Not to be fixed by quieting the view.** Cheap facts for the design: response carries an `ETag` (no download needed) and `Accept-Ranges: bytes`. See `F-next/archive-hash-is-a-build-id-not-a-change-detector`. | - |
| OPEN-45 | **ANSWERED as to fact, OPEN as to design.** Slice 1's loader is `ON CONFLICT (cik) DO NOTHING`, so it **never updates** `current_*` - the misattribution dilemma does not arise and `source_fetch_id` is internally consistent. **But that is the other defect the ruling named**: a `current_` column that never updates. **`metadata_as_of` is the sharp case** - its job is to bound the currency claim, so frozen it does not go stale, it **asserts a false bound**, permanently claiming the date of first sight. Fold into OPEN-46. | - |
| OPEN-46 | **[PLANNER] Decide the `current_*` upsert and its provenance TOGETHER.** If the loader starts updating `current_name`/`current_sic`/`metadata_as_of`, **OPEN-45's dilemma arrives immediately**: does `source_fetch_id` follow the update (losing which fetch created the row) or stay at creation (pointing at a fetch that did not produce the values beside it - **provenance present, non-null and wrong**)? Both are defensible; the second's failure mode is the one this project keeps finding. **Deciding the upsert without deciding the provenance is how the wrong one gets chosen by default.** | `filer.current_*` ever being refreshed. |
| ~~OPEN-44~~ | **ANSWERED PER SOURCE 2026-09-24.** **FSDS quarterly archives are byte-stable** - `2026q2.zip` fetched twice returned identical bytes and sha256, refuting the rebuild-nondeterminism hypothesis for the **primary fact source**. So `fetch_content_change` is **correct** there: a changed hash would mean the SEC republished that quarter, which is exactly what it should report. **`submissions.zip` changes nightly** (+213,015 bytes in 24h) because it is a growing snapshot, so its response hash is a **build identifier** and the member-level question applies **only to it**. Proves response determinism, **not** that an archive will never be republished - and only the first was in doubt. | - |
| OPEN-51 | **RULED 2026-09-24 (owner): the 45 most recent FSDS quarters, MEASUREMENT FIRST.** One quarter into a local cluster, sizes taken, × 45, **reported before loading 45**. **Condition: coverage recorded as data** - loaded quarters as rows with per-quarter fact counts, and **every validation states its window in its own output**. Without it a 2013 backtest against a 2015 store returns a well-formed nearly-empty answer that looks like a result. **Does not weaken *store, don't filter*** - the boundary is a load decision recorded as data, not a filter on data we hold. See `D-next/coverage-window`. | The fact slice's load step. |
| OPEN-52 | **[PLANNER] D21 is lost - the fact-slice handover itself, plus OPEN-47 through OPEN-50.** D22's check: expected 48 distinct, **46 on disk**, shortfall exactly D21's two documents. Known only by citation: OPEN-48 `version`/filer extension tags, OPEN-49 `segments` truncation, OPEN-50 `adsh` formatting; §4.3 *store, don't filter*; §5's preference order. **Their precise terms, falsification conditions and whatever nothing cited are unknown** - `citations-are-lossy-recovery`, which has now cost a missed condition twice (D9 §3, D17's two-pillar clause). **OPEN-48/49/50 not started.** OPEN-44 proceeded because D20 specified it fully and is in hand. | The fact-slice build. |
| OPEN-53 | **RULED 2026-09-24 (owner): narrow by concept, tier 1, defer the tier question. MEASURED: tier 1 does not fit either.** Tier 1 retains **91.5%** -> **~114 GB against 15 GB**. And **no concept allowlist reaches 15 GB**: fitting requires <=12.1% of rows, and the **top 5 tags alone are 16.7% (~20.7 GB)**. Every lever now priced - window (5 quarters, useless), dimensions (refused, and ~49 GB anyway), indexes (15% max), concepts (~3 tags), **disk (the only 8x)**. **Report and stop per D24 §3.** Cost context, **corrected 2026-09-25 (P-11)**: 150 GB Basic is **$38/month more** than today, and **`stockgrader-db` alone - ours, empty, ~$41/month - more than covers it.** The earlier *~$120/month across three clusters* is **struck**: only one is established as idle, and the other two are attached to live projects with unknown status. **Do not destroy them.** | The fact slice's load step; the owner's ruling. |
| ~~OPEN-48~~ | **ANSWERED 2026-09-24, both quarters.** `version = adsh` marks a filer extension - documented in `readme.htm`, no heuristic needed. **Standard share 92.7% (2015q2) / 91.5% (2026q2)** - stable, and **moving opposite to the hypothesis** that early quarters carry more extensions. Extensions are **counted and reported, never silently dropped**. | - |
| ~~OPEN-49~~ | **ANSWERED 2026-09-24: `segments` is NOT truncated.** Max length **440** (2026q2) with **1 row at it**, **448** in 2015q2 - a fixed cap cannot produce two different maxima - and the tail decays smoothly against a mean of 6,100 rows per distinct length. **No truncated-string-parsed-to-valid-jsonb population exists.** The refuse-don't-default-to-`'{}'` rule stands for malformed input regardless. | - |
| ~~OPEN-50~~ | **ANSWERED 2026-09-24: formats match exactly.** **0 failures** against slice 1's accession pattern across **8,212** (2015q2) and **7,714** (2026q2) submissions. No FK formatting disagreement. | - |
| ~~OPEN-54~~ | **CLOSED 2026-09-25 by migration 0003.** `fact.source_fetch_id NOT NULL`, and **A5's enumeration inverted**: A2 derives its check set from the catalogue minus a declared `provenance_exempt` table, each exemption carrying a **length-checked mandatory reason**. Proven side by side - a new `price_daily` table fires A2 while 0002's enumerated A5 **passes, blind to it and to `fact`**. Plus **A3**, which refuses a stale exemption naming a non-existent table, because that **pre-authorises a future table reusing the name**. | - |
| ~~OPEN-55~~ | **CLOSED 2026-09-25 by migration 0003.** `fact_collision` keeps **both** competing assertions, neither loaded, both traced to their fetch; `fact_collision_rate` reports per fetch. **`fact_one_per_filing` is untouched** (A6) and the quarantine deliberately has **no uniqueness on the colliding key** (A5) - the rows collide by definition and a constraint there would reproduce the loss inside the table built to prevent it. | - |
| ~~OPEN-56~~ | **ANSWERED 2026-09-25, and the answer inverts D25 §5.1's framing.** `fly mpg create` takes **`--volume-size` (default 10)** and **no subcommand resizes it after** - the full list is attach/backup/connect/create/databases/destroy/detach/list/proxy/restore/status/users. Docs say *"Storage growth is monitored and managed automatically"* and bill **per provisioned GB** ($0.28/30-day month), but **do not state that provisioned storage can be raised post-creation.** **So "managed automatically" is the load-bearing claim and it is untestable without filling a disk.** On CLI evidence **under-provisioning is the EXPENSIVE mistake** - recovery means a new cluster plus a data migration, since `restore` picks its own size (OPEN-22). **Provision for measured need plus headroom; treat auto-growth as unverified, not as a safety net.** Also established: plan RAM = Basic 1 GB, Starter 2, Launch 8, Scale 32, Performance 64. | - |
| OPEN-57 | **RE-MEASURED 2026-09-25 under a REAL 1 GB cgroup - build settled, steady state still open.** Docker `--memory=1g`; cgroup v2 charges page cache, so the cache was genuinely bounded: `memory.current` pinned at **990-1,022 MB of a 1,024 MB cap**, **969 MB of it file cache**, **95,784 reclaim events, 0 OOM kills**. **Index build: 15.4 s for 1,075 MB** - faster than the unconstrained host run - so **the external sort comes off the risk list properly.** **Steady state: 627/659/882 ms, but hit=16,113 read=123,325 - 88% from disk at only a ~2:1 data-to-cache ratio.** At 114 GB the ratio is ~114:1 and I/O dominates. **REMAINING CONFOUND: Docker's VM has 15.4 GB of unbounded page cache beneath the container**, sitting exactly in the I/O path that would dominate. **Closing it needs a 1 GB-total host or a real Basic cluster - both cost something.** | OPEN-53's plan tier. |
| OPEN-58 | **B-4's re-run of the restore drill now costs a second ~114 GB cluster** - plan fee plus storage, for as long as it exists. **B-9's same-sitting destroy condition applies with more force**, and the drill should be scheduled when someone can see it through to the destroy. | The post-ticker-load drill re-run. |
| ~~OPEN-59~~ | **CLOSED 2026-09-25.** The quarantine broke double-ingest idempotency: `fact_collision` had **no constraint at all**, so re-ingesting a quarter re-inserted every quarantined row. Identity is now the colliding key + **`value`** + **`source_ordinal`**, with `source_ordinal` made `NOT NULL`. `value` keeps two disagreeing rows both inserting (A5's property, by construction); `source_ordinal` keeps **three rows where two agree on value** from collapsing to two - **the shape the Planner named in advance, and the harness confirms the wrong fix produces exactly 2**; and `source_fetch_id` is **deliberately excluded**, because a re-ingest is a new fetch with a new id and including it would pass a naive test while fixing nothing. **A5 had to be refined first** - it forbade any uniqueness covering `concept`, which was a *proxy* for *would refuse a competing value*, and would have rejected the correct fix. See **F-022**, **F-023**. Proven on PostgreSQL 18.3: **6/6 red-test cases**, control green. | - |
| ~~OPEN-60~~ | **CLOSED 2026-09-25.** A2 scoped its catalogue derivation to `nspname = 'public'`, so it **enumerated a schema instead of a table list** - a table in any other schema escaped exactly as `fact` escaped 0002's A5, one level up. Now scoped by **exclusion of system schemas** (`pg_catalog`, `information_schema`, `pg_*`), so a new schema is in scope by default. **`provenance_exempt` became schema-qualified in the same change** - unqualified, a row exempting `bulk_facts` would have exempted that name in *every* schema, **moving the hole rather than closing it**. Proven side by side, the way A2 was proven against A5: the public-only scope blind, the schema-wide scope firing, same database and moment. **B7 asserts the old scope returns 0**, so the comparison cannot quietly stop measuring. See **F-024**. | - |
| OPEN-65 | **[OWNER] The Basic write path costs ~45 min per quarter with all seven indexes live - decide the tier or the load strategy before the 45-quarter run.** Measured 2026-09-25 on the live cluster: **3,368,813 facts loaded**, counts identical to the local 18.3 run, but the fact insert maintained **seven index structures per row** (`pg_locks`, F-032) on **1 GB of shared CPU**. Locally the same phase costs ~50 s because the indexes sit in RAM. **~45 min x 45 quarters = ~34 hours**, against ~2 h at local speed. **This is OPEN-57's question on the WRITE path** - both earlier attempts measured reads and neither touched ingest. **Two levers, not mutually exclusive:** (a) `--defer-indexes`, already built and proven to reproduce all five index definitions exactly, on OPEN-57's own evidence that a build is cheap (1,075 MB in 15.4 s under a 1 GB cgroup) while maintenance during insert is not; (b) a larger tier, which the owner has ruled is not cost-blocked. **Not a correctness issue** - the load completed and balanced. **Measure (a) on one quarter before committing to either.** See **F-031**, **F-032**. | The 45-quarter load; OPEN-53's tier choice. |
| OPEN-64 | **[PLANNER/OWNER] 4.9% of FSDS rows carry NO VALUE - decide whether refusing them is right.** Measured on 2026q2: **179,806 rows** have an empty `value` with tag, taxonomy, period and unit all present and well-formed (**178,555** counted as `refused_malformed`; the other 1,251 also carry a `coreg` and count there). Only 1,404 carry a footnote, so footnotes do not explain them. **They are not obscure tags** - `NetIncomeLoss` (11,538), `CommitmentsAndContingencies` (9,585), `ProfitLoss` (5,143), `StockholdersEquity` (4,561) - and the first and fourth are **core GQS inputs**. **Current behaviour: refuse and count**, which is visible rather than silent, and `fact.value` is NOT NULL because a fact without a value is not a fact. **But the behaviour arrived as a default, not a decision**, and *store, don't filter* cuts the other way: what the source asserted is **an element tagged with no number**, and a line item deliberately left blank is not the same as one never tagged. **Decide explicitly.** If they are to be kept, it needs a representation that does not weaken `fact.value`'s guarantee for the 93.4% that do have one. See **F-030**. | What the fact store contains; every GQS metric whose input is among these tags. |
| OPEN-63 | **[OWNER] Rotate `stockgrader_app`'s password — DEFERRED by the owner 2026-09-25, recorded so the deferral has an end.** The credential reached the session transcript, the owner's shell environment and PowerShell history on disk (**F-021**). It is the credential the **deployed application** uses, so rotation is two actions and both are the owner's: **1.** set a new password for `stockgrader_app` in the dashboard; **2.** `fly secrets set` the app's `DATABASE_URL`. Then clear it locally — `Remove-Item Env:DATABASE_URL`, and the line from `(Get-PSReadlineOption).HistorySavePath`. **Why it is an open item rather than a note:** the owner ruled *"we'll change it later"*, which is correct prioritisation and is also exactly P-13's shape — §11.1 was deferred to *"its own session"* on day one and no session was ever scheduled. **A deferral without an end is a deferral without a date.** **Note the ordering interaction:** this rotation is independent of OPEN-25's drops and of OPEN-27's clean `schema_admin`, and is **not** gated behind them — `stockgrader_app` is a `writer` and owns no objects, so rotating it is a password change rather than an ownership migration. **It gets more expensive only if the app is redeployed against the old secret in the meantime.** | D-030's claim that credentials never appear in transcripts; D-029's rotation-is-complete-when-proven rule. |
| OPEN-55 | **FSDS violates its own documented unique key, and 31 of 32 collisions disagree on value.** 3,608,711 rows / 3,608,679 distinct key tuples in 2026q2. **`ON CONFLICT DO NOTHING` would be silent data loss.** The loader must detect collisions, **assert colliding rows agree on value, and fail loudly when they do not** - 31 rows per quarter is small enough to report individually and far too important to drop. OPEN-49's terms may bear on the cause; not assumed. | The fact loader's conflict policy. |
| OPEN-35 | **Ticker validity ranges before first observation are unavailable.** `filer_ticker.valid_from` is the date the pairing was **observed**, not the date it began - `company_tickers.json` carries no start date (`F-next/ticker-crosswalk-has-no-start-dates`). Historical ticker resolution therefore returns nothing before first observation. **Not on the load-bearing path** - ruling 5 keys the universe on CIK - and not pretended. Recovering true ranges needs a source we do not have. | Any historical ticker-based lookup. |

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
- *(future)* **Ingest slice 1 loading into Postgres.** Parsing, the rate limit,
  403 handling and the scheme refusal are hermetic and in the gate (21 tests).
  **Loading and double-ingest idempotency are not** - they were proven against a
  local PostgreSQL 18.3 cluster, which is neither the platform's major version
  (OPEN-30) nor behind a pooler (OPEN-21). A hermetic green is not evidence that
  ingest loads.
