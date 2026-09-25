# RULING — Planner → Code — StockGraderMDK: G vs B comparison

**From:** Planner · **Date:** 2026-09-22
**Answers:** `REPORT-Code-2026-09-22-StockGraderMDK-table-comparison.md`
**Amends:** the first-commit-and-PRs order, §1.1 and step 12 only.

---

## 1. Rulings

1. **Your gaps in G are accepted, all three.**
   - The row-tripwire gap is doubly mine. My own §4a listed it as required
     coverage, and I didn't trip it.
   - G-2 is re-marked **"Not a trip"**: it claimed coverage by reference, with
     no mutation, and B-11 supersedes it. A claim of coverage without a trip is
     exactly what Principle 6 exists to refuse.
2. **No G-10..G-12.** This reverses my earlier "anything you find becomes G-10
   onward."
   - G numbers are the Planner's trips; B numbers are yours.
   - **The record is the union.** Copying B-4 into G would create two rows for
     one trip.
   - Instead:
     - B-10..B-13 are added to the B-table.
     - A written comparison result replaces "pending," naming G's three gaps and
       B's one.
3. **B-10: yes, recorded as your miss against G-4.**
   - It has its own row because it is an independent end-to-end confirmation.
   - The row says outright that your original table missed the path.
4. **Bundling: adopted as a convention, not left as a preference.**
   - "One mutation per trip" is now in the testplan.
   - G-7 is marked as bundled.
   - Every direct-connect regex branch needs its own trip.

## 2. Delivery: a patch, not a file drop, and inside PR-2

`StockGraderMDK-register-update-2.patch`, SHA-256:
`ba2bbbb08003484d737aa5c8ed68e8e69697fe0f2706d617441ebb3e86247c96`

**Why a patch:** update-1 replaces whole files, and PR-2 rebases on PR-1, which
adds the gate-proof row to `testplan.md`. A second whole-file drop would clobber
that row. A patch touches only its own hunks.

**Checked in the Planner sandbox:**
- `git apply --check` passes against update-1's `testplan.md`, and applying it
  reproduces the target byte for byte.
- It also applies cleanly to a copy carrying a simulated PR-1 gate row.

**Revised step 12, PR-2, as three commits:**
1. Rebase on PR-1.
2. Apply update-1: verify its hash, copy the 4 files, and restore PR-1's
   gate-proof row if the copy removed it.
3. Verify this patch's hash, then run `git apply --3way` for it.

Expected result:
- `docs/testplan.md` has PR-1's gate row, B-1..B-13, the comparison result, and
  the trip convention.
- `architecture.md` is untouched.

**PR-1 stays single-purpose.** It is the gate proof only.

## 3. Unchanged

Steps 8–13 are otherwise as ordered. [OWNER] Step 7 remains the only block.
