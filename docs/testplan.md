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
| OPEN-9 | **The price vendor is unchosen, and the deciding question is delisted coverage.** Owner ruling 4 settled *sourcing policy* (SEC is one source among several), **not vendor selection**. A vendor that drops dead names **reintroduces survivorship bias through the door ruling 5 just closed.** Put delisted coverage to **Tiingo** and **EODHD** directly - the question is whether a delisted ticker's history remains retrievable after delisting, not whether the vendor says it has "full history." | Any price ingest; the universe's integrity (ruling 5). |
| OPEN-10 | **Altman variant unresolved (ruling 11).** Z' (private-firm, book equity) was recommended; *"take Z"* was returned and reads as public-firm Z (market equity). Not assumed either way. | The disqualifier block. |
| OPEN-11 | **Sector granularity unresolved (ruling 13).** No recommendation existed to accept. Live options: SIC as-is, hand-maintained mapping, per-archetype metric sets. | Per-sector metric selection. |

## D-019 counter - `windows-setup` consecutive green runs

Promotion to a **required** check is an owner ruling at **10**. Reset to zero on
any red. **The counter is structurally one behind:** a count committed to the
repo cannot include the run that validates the commit recording it.

**Count: 6 of 10** (as of 2026-09-22)

| # | Run | Branch |
|---|---|---|
| 1 | [35755627563](https://github.com/mdk32366/StockGraderMDK/actions/runs/35755627563) | pr3-code-d012-d014-d015 |
| 2 | [35755827105](https://github.com/mdk32366/StockGraderMDK/actions/runs/35755827105) | pr3-code-d012-d014-d015 |
| 3 | [35755972455](https://github.com/mdk32366/StockGraderMDK/actions/runs/35755972455) | main (PR-3 merge) |
| 4 | [35761835450](https://github.com/mdk32366/StockGraderMDK/actions/runs/35761835450) | pr4-d020-visibility |
| 5 | [35765068869](https://github.com/mdk32366/StockGraderMDK/actions/runs/35765068869) | pr4-d020-visibility |
| 6 | [35765196736](https://github.com/mdk32366/StockGraderMDK/actions/runs/35765196736) | main (PR-4 merge) |

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
| OPEN-5 | **The gate cannot see a staged secret.** F-015 passed every check we have, including the live-SHA verification, because the SHA is baked into the image and has nothing to do with secrets. A DB-backed endpoint plus a check that it actually answers *from the database* would close this. | Not buildable until such an endpoint exists, so this is an open item, not a guard. It is also what D-029 means by "a rotation is complete when a request to the live service proves the new credential is in use". |
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
| Any §11 question unratified | **OPEN** - 11.1 deferred (ruling 12), 11.2 unresolved (ruling 13) |
| §5.4 R&D treatment unresolved | **OPEN** - the same question as 11.1 |
| Eligibility table contains an unlisted class | Believed clear; **confirm in v4** |
| Any block contains a placeholder metric | **Confirm in v4** |
| Point-in-time property weakened in build order | Not yet applicable |

**No scoring build order can issue.** Two conditions are open and two are
unconfirmed.

**Ingest is unaffected and proceeds.** The universe, the point-in-time fact
store, and the filing-date/accession discipline are the same work whichever way
the §11 questions land - which is why ruling 5 constrains the first migration
now rather than waiting on the gate.
