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

## Open items. Each blocks something specific.

| ID | Item | Blocks |
|---|---|---|
| OPEN-1 | `postgres_probe` (the real-DB half of the guard) has **never run against a real Postgres**. Its logic is proven only through fakes. | The first DB-backed test. No test may use `db_url` until the probe has refused a non-canary DB and accepted a canary DB, both on a real server. |
| ~~OPEN-2~~ | **CLOSED 2026-09-22.** Built on the first deploy: 48 MB image, pushed to `registry.fly.io/stockgradermdk`, running live. It did fail on first deploy -- on `primary_region`, not the image (F-011). | — |
| ~~OPEN-3~~ | **CLOSED 2026-09-22 by F-008.** Reproduced on the owner's machine: 22/22, egress-blocked. | — |
| ~~OPEN-4~~ | **CLOSED 2026-09-22 by F-008.** Windows PowerShell 5.1.26100.9444 parsed and ran the fixed `setup.ps1`. | — |

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
