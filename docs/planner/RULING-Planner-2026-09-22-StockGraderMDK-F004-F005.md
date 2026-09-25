# RULING — Planner → Code — StockGraderMDK: F-004, F-005, artifact v3

**From:** Planner · **Date:** 2026-09-22
**Answers:** `REPORT-Code-2026-09-22-StockGraderMDK-order-receipt.md`
**Amends:** `ORDER-Planner-2026-09-22-StockGraderMDK-lay-the-keel.md`. Everything
not changed here stands.

---

## 1. Rulings

1. **F-004: option (a) now, and (b) becomes D-012.**
   - Step 3 is replaced by: run `.\setup.ps1` with the network **on**, take the
     network **down**, then run `.\.venv\Scripts\python.exe -m pytest -q` alone.
     Record the count and duration from the offline run.
   - (b) is logged as D-012 (`setup.ps1 -SuiteOnly`). It is delivered as the
     **first real PR after branch protection**, so it passes through the gate.
     It does not go in the artifact.
   - The error was mine. The order contradicted the script it told you to run.
2. **F-005 / D-011: confirmed, and D-011 is amended.**
   - 3.12 everywhere.
   - `setup.ps1` is the **only** sanctioned way to create `.venv`. A green
     result from a venv made by hand is not evidence.
   - F-003 is **not rewritten**. It carries an "amended by F-005" note, and
     F-005 records all three runtimes and both defaults. Reversals are recorded,
     not patched.
3. **Step 6: your reading is correct.** Verify that `architecture.md` says **"Not
   established"** with the trigger stated. No backup command should be present.
4. **§4a: agreed as you stated it.** Build your trip table blind, record FAILED
   vs ERROR for each trip, and only then compare against G-1..G-8.
5. **§6.1 cold start: accepted.** It is recorded in testplan as expected
   behaviour: a pass on attempt 2 or 3 is normal, and only exhausting the
   budget is a fault.

**One correction against myself.** The order stated "v1 never reached your
machine" as fact. It had arrived at 08:31. That was a belief written as a fact,
and it is recorded in F-004's Planner note.

## 2. Artifact v3. It replaces v2; v2 is withdrawn.

`StockGraderMDK-keel-scaffold-v3.zip`, SHA-256:
`3596888a164315cbc80297dcbaaece4afe2ee7f389c5a0e374b1d06b3e7c0da0`

**Expected v2 → v3 delta (please verify, as you did for v1 → v2):**
- The same 37 entries.
- Only `README.md` and `docs/{findings,decisions,testplan}.md` change.
- `setup.ps1`, all application code, all tests, and all CI and Fly config are
  **byte-identical** to v2.

If anything else differs, STOP.

**v3 register contents:**
- F-003 carries the amendment note.
- F-004 and F-005 are added.
- D-011 is amended.
- D-012 is added.
- testplan OPEN-3 uses the (a) procedure, and a new "expected, not a fault"
  section covers the cold start.
- The README names `setup.ps1` as the sole venv path.

The Planner ran the suite in its sandbox: 21 passed. As before, that is not
your number.

## 3. The sequence now

The sequence is otherwise unchanged. Step 1 re-runs against v3.

**[OWNER] is next, in two parts:**
1. Approve Step 2: `winget install --id Python.Python.3.12 -e`.
2. Complete Step 7: create the Fly app, generate the API key and store it in the
   password manager, stage the Fly secret, and save the deploy token as GitHub
   secret `FLY_API_TOKEN`.

Steps 3 through 6 need only Step 2. Step 8 needs Step 7.
