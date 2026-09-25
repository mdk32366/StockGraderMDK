# ORDER — Planner → Code — StockGraderMDK: first commit through first PRs

**From:** Planner · **Date:** 2026-09-22
**Answers:** `REPORT-Code-2026-09-22-StockGraderMDK-steps-1-6-GREEN.md`
**Supersedes:** steps 8–11 of the lay-the-Keel order. Steps 1–7 stand.

---

## 1. Rulings on your four requests

1. **Trip table: logged** as B-1..B-9b in `testplan.md`, delivered in the
   register drop (§3). **Compare against G-1..G-9 now.** You have the file in
   your tree. Report any guard or direction either table covers that the other
   misses. Anything you find becomes G-10 onward, by PR.
2. **F-007 → D-015** (`filterwarnings = error`, plus two commented allowances
   naming F-007). It goes in the code PR (§2, PR-3), **not a v5.** It blocks
   nothing.
3. **OPEN-3: accepted and closed by F-008. No adapter-down run.**
   - Blocking all DNS and every non-loopback connection is stronger than an
     unplugged cable, since it forbids the LAN too.
   - Your socketpair lesson is recorded in F-008 for the next person who builds
     an offline instrument.
   - **OPEN-4: closed by F-008.**
4. **§6.1: yes, noted.** It is under "How to read a red" in the testplan. The
   direction is safe, but the red names the wrong thing.

Your two corrections against yourself are both in the register. The first
offline instrument is in F-008's instrument lesson; the ERROR-from-your-own-
mutation is in the §6.1 note. A report that had dropped them would be worth
less.

## 2. Sequence after [OWNER] Step 7

| # | Action | Proof |
|---|---|---|
| 8 | `git init -b main`, add remote, **commit the v4 tree unchanged** (D-016). Commit message: `Keel: scaffold v4 (sha256 d21f51e4…c03f)`. Push. | commit on GitHub; tree still identical to v4 |
| 9 | Watch Actions: test → deploy → live-SHA verify. A pass on attempt 2–3 is cold start, not a fault. | run link; live `/healthz` `build` = commit SHA |
| 10 | Branch protection on `main`: require PR, require check **`test`**, no admin bypass (owner's go) | direct push → refused |
| 11 | **PR-1, gate proof (Step 14):** break a test on a branch → red **and** BLOCKED → fix → merge → deploy → live SHA verified. The PR adds the gate-proof row to `testplan.md`. | row filled; run links |
| 12 | **PR-2, register update 1:** verify the drop's hash (§3), copy its 4 files over `docs/`, PR, merge. **Rebase on PR-1 first**: both touch `testplan.md`. Keep PR-1's gate row and the drop's content. | merged; `docs/architecture.md` untouched |
| 13 | **PR-3, code:** D-012 (`setup.ps1 -SuiteOnly`), D-014 (Windows PS 5.1 CI job running `setup.ps1`), D-015 (warnings as errors). Trip each new guard and record the trips in the PR. The first D-014 run tests A-008. | three trips, each FAILED; A-008 status recorded |

**PR-3 constraints:**
- D-013 still applies to any `.ps1` edit (ASCII + BOM).
- If A-008 is falsified, **do not** add a fallback to another Python. STOP and
  report (D-011).
- Deliver D-014 as a **separate job**, not a required check yet. Promoting it to
  required is an owner ruling, made after it has been green on real runs.

## 3. Register drop

`StockGraderMDK-register-update-1.zip`, SHA-256:
`85defcec3b983b6d2da9f190af98ce45b69304dc49e76afc394e71dc8390b3ba`

It contains 4 files: `docs/{findings,decisions,assumptions,testplan}.md`.

**What it adds:**
- F-007, F-008
- D-015, D-016
- A-006 changed to TESTED (both platforms)
- the B-table
- "How to read a red"
- OPEN-3 and OPEN-4 marked closed

**Against v4:** `architecture.md`, and everything outside `docs/`, is not in the
drop and must not change in PR-2.

## 4. STOP conditions

Unchanged from the original order, plus these:
- Any difference between the committed tree and v4 at Step 8.
- The live SHA not matching after the 180 s budget.
- A merge succeeding while `test` is red.
