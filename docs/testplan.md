# Test plan — What would catch it if it broke?

## The gate (Day-One Step 14): PROVEN 2026-09-22

| Date | Broke what | Gate blocked? | Fixed + merged | Shipped + live SHA verified? |
|---|---|---|---|---|
| 2026-09-22 | `app/auth.py`: bypassed `compare_digest`, so any non-None key was accepted (`test_meta_with_wrong_key_is_401` red) | **Yes.** `test` failed, `deploy` was skipped (`needs: test`), and the PR reported `mergeStateStatus: BLOCKED`. Red run: [35754766404](https://github.com/mdk32366/StockGraderMDK/actions/runs/35754766404) | PR-1, second commit reverts the bypass | see the merge run recorded in PR-2 |

Record it here the day you watch it block AND ship with your own eyes.
Branch protection (Step 15) must require the status check named **`test`**.

## Guard proofs (KEEL Principle 6): each broken on purpose, each seen red

All trips were done 2026-09-22 in the Planner container. Every red was a
**failure** (the assertion executed), not an error.

| ID | Mutation | Went red |
|---|---|---|
| G-1 | Removed auth's "server key unset → 503" branch | `test_unconfigured_server_fails_closed[None]` and `[""]`. The `""` case is the discriminating one: client key `""` against server key `""` passes `compare_digest`, so only the fail-closed branch stands between that request and a 200. |
| G-2 | (covered by G-1 plus 401 tests) wrong or missing client key | `test_meta_without_key_is_401`, `test_meta_with_wrong_key_is_401` |
| G-3 | Session guard, end to end: `DATABASE_URL` = tunnel-style localhost URL, no confirmation | pytest exited with code **3**, `KEEL DB GUARD REFUSED`, before any test ran |
| G-4 | Confirmed, but identity unverifiable (psycopg absent) | refused, exit 3. Unverifiable is treated as unsafe. |
| G-5 | Removed factor 1 (confirmation sentence) from the guard | `test_tunnel_localhost_without_confirmation...`, `test_near_miss_confirmation...` |
| G-6 | Removed factor 2 (canary check) | `test_missing_canary_is_refused` |
| G-7 | Put the confirmation sentence in a local `.env`; planted a password URL and a direct `psycopg.connect` in a test | `test_confirmation_variable_never_lives_in_an_env_file`, `test_no_secrets...`, `test_tests_never_open_database_connections_directly` |
| G-8 | Added an undeclared endpoint | `test_openapi_matches_committed_contract` |
| G-9 | (F-006, D-013) Ran the new `.ps1` guard against the unfixed v3 `setup.ps1`; then, on the fixed file, re-inserted an em-dash with the BOM kept (A), and stripped the BOM from an ASCII body (B) | `test_powershell_scripts_are_safe_for_windows_powershell_5`, all three times. v3 reported the BOM plus `e2 80 94` on lines 1 and 27; A reported line 27; B reported the BOM. Each half bites alone. |

## Open items. Each blocks something specific.

| ID | Item | Blocks |
|---|---|---|
| OPEN-1 | `postgres_probe` (the real-DB half of the guard) has **never run against a real Postgres**. Its logic is proven only through fakes. | The first DB-backed test. No test may use `db_url` until the probe has refused a non-canary DB and accepted a canary DB, both on a real server. |
| OPEN-2 | The `Dockerfile` has **never been built** (no Docker in the Planner environment). | Nothing yet. Its first build is the Step 14 deploy, which is exactly where it should fail if it's going to. |
| OPEN-3 | F-002 has not been reproduced on the owner's machine. | Step 12 proof. Install Python 3.12 if absent (D-011). Run `.\setup.ps1` with the network **on** (it installs from PyPI; see F-004). Then take the network **down** and run `.\.venv\Scripts\python.exe -m pytest -q` alone. That proves the suite, not the installer, is hermetic., then run the suite once with `$env:DATABASE_URL="postgresql://app@localhost:15432/x"` and watch it refuse (exit 3). |
| OPEN-4 | The fixed `setup.ps1` has **never been parsed by Windows PowerShell 5.1**. G-9 proves the bytes, not the parse. CI still never runs `.ps1` (D-014). | Step 3. The Builder's first clean run of `.\setup.ps1` closes it. |

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
