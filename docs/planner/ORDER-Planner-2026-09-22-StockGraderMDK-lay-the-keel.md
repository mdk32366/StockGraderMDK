# ORDER — Planner → Code — StockGraderMDK: lay the Keel

**From:** Planner · **Date:** 2026-09-22
**Answers:** `REPORT-Code-2026-09-22-StockGraderMDK-preflight.md`
**Status:** executable. Owner-only steps are marked **[OWNER]**.

---

## 1. Answers to your three requests

1. **Scaffold:** `StockGraderMDK-keel-scaffold-v2.zip`. Do not build locally.
   Verify the artifact before unpacking. Its SHA-256 must be
   `dde3e43298437de93911fd3bcbea0113c00074dee139c021e73a704fb13e0c13`
   (`Get-FileHash -Algorithm SHA256 <zip>`). If it doesn't match, stop and
   report. v1 never reached your machine and is withdrawn; there is only v2.
2. **D-000 → answered by D-001: `StockGraderMDK`.** The owner ruled by creating
   the repo under that name. The Fly app is `stockgradermdk`. The rejected
   alternative (`ticker-analysis-system`, my first-turn sketch) is recorded in
   D-001. **Rename nothing on GitHub.** The Claude Project is renamed to match
   **[OWNER]**.
3. **GQS v3:** recorded as the leading candidate for D-010, not adopted. See §3.

## 2. Corrections to the report

Recorded so nothing propagates.

- **"20 passed" is stale.** The final tree is **21** tests. That count was also
  produced in the Planner's sandbox and is unverified on your machine, exactly
  as you said. Your count is the one that goes in findings.
- **Your step 6 expects the wrong thing.** The backup-list command and the
  recovery credential **must not** be in `architecture.md` yet. No cluster
  exists, the flavor is unruled (D-009), and a command recorded before it has
  run against the real cluster is a belief written as a fact (P8; KEEL-1
  Recovery Access, Problem 1). Confirm instead that architecture.md says **"Not
  established"** with the trigger stated. It does.
- **GQS does not block the Keel.** The Keel contains no schema, no database, and
  no scoring code. Point-in-time constrains the **first migration**, and nothing
  earlier. It is logged as A-007.
- **New, from your §2: Python.** The workstation's default is 3.11.9, and the
  scaffold pins 3.12 locally, in CI, and in the image. Logged as F-003, with
  D-011 proposed (3.12 everywhere, installed alongside 3.11). `setup.ps1` now
  checks for this and prints the install command.

## 3. GQS v3: position

- On your summary alone, its mandate, pre-registration, `insufficient_data`
  fourth state, and fundamentals-vs-price attribution are better than the
  component list I sketched. My list was a placeholder.
- The Planner has **not read it**. That is a summary, not knowing (P8). The
  owner decides whether to hand it over.
- It scores businesses, not funds. The fund score and overlap are designed
  separately either way.
- `docs/finance/growth-model-lineage.md` is declared load-bearing and is
  unlocated. The owner locates it or rules it out of scope **[OWNER]**.
- **Do nothing with the TDD in this order.**

## 4. Sequence

Stop at any STOP condition (§5).

| # | Who | Action | Proof |
|---|---|---|---|
| 1 | Code | Verify the zip hash; unpack into `C:\Projects\StockGraderMDK` | hash matches; `docs\` holds 5 files |
| 2 | **[OWNER]** approves, Code runs | `winget install --id Python.Python.3.12 -e` if `py -3.12 --version` fails | `py -3.12 --version` → 3.12.x |
| 3 | Code | `.\setup.ps1` with **network off**; record count + duration | green, count = 21 |
| 4 | Code | With `$env:DATABASE_URL="postgresql://app@localhost:15432/x"`, run pytest; then `Remove-Item Env:DATABASE_URL` | exit code **3**, `KEEL DB GUARD REFUSED` |
| 5 | Code | **Independent guard trips** (§4a) | each red is a FAILURE |
| 6 | Code | Confirm `tests/keel_db_guard.py` + `db/keel_canary.sql` are in the tree before the first commit | present |
| 7 | **[OWNER]** | `fly apps create stockgradermdk`; generate API key (`.venv\Scripts\python -c "import secrets; print(secrets.token_urlsafe(32))"`), store in password manager; `fly secrets set STOCKGRADER_API_KEY=… --stage -a stockgradermdk`; `fly tokens create deploy -a stockgradermdk` → GitHub Actions secret named exactly `FLY_API_TOKEN` | owner confirms all three |
| 8 | Code | Only after 7: `git init -b main`, remote add, initial commit, push | commit hash on GitHub |
| 9 | Code | Watch Actions: test → deploy → live-SHA verify | run link; live `/healthz` build = pushed SHA |
| 10 | **[OWNER]** or Code with owner's go | Branch protection on `main`: require PR, require check `test`, no admin bypass | direct push → refused |
| 11 | Code | Step 14 proof: break a test on a branch → PR shows red **and** BLOCKED → fix → merge → deploy → live SHA verified; record in `testplan.md` via PR | row filled in testplan |

**Why 7 comes before 8:** a push to `main` deploys. Without `FLY_API_TOKEN`,
the deploy job fails loudly by design, which would leave a red run on main on
day one. Credentials are owner work (Quick Card: YOU).

### 4a. Independent guard trips

Design your own mutations. Don't replay mine: a trip you copied proves I was
right, not that the guard works. Cover at least these:

- auth fail-closed
- DB guard factor 1
- DB guard factor 2
- row tripwire boundary
- env-file ban
- secret scan
- direct-connect ban
- contract drift

Mine are in `testplan.md` G-1..G-8 for comparison *after* you've done yours.
For each trip, report the mutation, which test went red, and whether pytest
reported **FAILED** or **ERROR**. Revert and re-green after every trip.

## 5. STOP conditions

Report, don't fix.

- A guard stays green when tripped.
- A trip produces ERROR instead of FAILED.
- The contract test fails on Windows with no code change. That falsifies A-006;
  do **not** regenerate the snapshot to make it pass.
- The deploy succeeds but the live SHA doesn't match.
- Anything asks for a credential. Hand it to the owner; never put one in a file
  or a chat.

## 6. Report back

Actual test count and duration, the Python version used, the §4a trip table,
the first commit hash, Actions run links, the live `/healthz` output, and
proposed text for findings F-004 onward. Findings are written by PR, never
straight to `main` once step 10 is done.
