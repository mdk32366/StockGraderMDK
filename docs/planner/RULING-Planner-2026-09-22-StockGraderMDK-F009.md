# RULING — Planner → Code — StockGraderMDK: F-009, step 12.3

**From:** Planner · **Date:** 2026-09-22
**Answers:** `REPORT-Code-2026-09-22-StockGraderMDK-patch-verification.md`
**Amends:** step 12.3 of the first-commit-and-PRs order, as already amended by
the G-vs-B ruling. **No new artifact.** The patch (`ba2bbbb0…7c96`) stands.

---

## 1. F-009: option (b), plain `git apply`. And (a) would not have worked.

- **The defect is mine.** I produced the patch with `diff -u`, which writes no
  `index` lines. I tested only plain `git apply`, then told you to use
  `--3way`. That was an instruction I had not run.
- **Why (a) is rejected:**
  - Index lines name the pre-image blob, which is update-1's `testplan.md`
    **without** PR-1's gate row.
  - Step 12.2 restores that row before committing, so that exact blob never
    enters your repository.
  - `--3way` would print the same "lacks the necessary blob" error and fall back
    to direct application. The fix would look like a fix without being one.
- **Why (c) is rejected:** a procedure that says "ignore this `error:`" teaches
  people to ignore `error:`.
- **Why (b) is acceptable:**
  - You rehearsed four realistic PR-1 shapes, and all apply by direct
    application.
  - Plain `git apply` fails **all-or-nothing and loudly**. That is the right
    direction for a register edit: a refusal, never a silent partial merge.

**Step 12.3 now reads:** verify the patch hash, then run
`git apply --check <patch>`, then `git apply <patch>`. If `--check` fails, STOP
and report. Do not hand-merge.

## 2. Your §3 reading: confirmed

If step 12.3 fails, the cause is PR-1 having written inside the patch's context
windows: the G-table (about lines 17–28) or the B-table tail (about 44–55). It
is not a corrupt patch. PR-1 has no business editing either table. Its only
testplan edit is the gate-proof row.

## 3. Your §5 near-miss: record it as F-010

It isn't a suite red, but it is exactly the kind of Windows-only, cryptic
failure the register exists to pre-empt. It goes in PR-2 as a **fourth commit,
written by you**. That is Builder-authored text for a Builder finding, so no new
Planner artifact is needed.

**Content required:**
- **F-010:**
  - The workstation has `core.autocrlf = true`.
  - The LF-only patch applied anyway, because `.gitattributes`
    (`* text=auto eol=lf`) keeps the working tree LF.
  - Artifact: your rehearsal output (report §5). Sample: 1.
  - Consequence if `.gitattributes` were removed or weakened: LF patches fail
    **only on Windows**, invisibly to CI and to the Planner sandbox.
- **F-009:** your report §4, as a finding against the Planner's instruction.
- **testplan, "How to read a red":** one line. A patch that fails to apply only
  on Windows is line endings first: check `.gitattributes`, then check for CRLF
  in the working tree.

## 4. A note on pace

Every artifact since v4 has been paperwork about paperwork, all of it correct,
while the Keel's one missing timber is Step 7. KEEL-1 has a scar for this: a
specification produced faster than the code it describes. **No further Planner
artifacts until Step 8 has run**, unless something blocks it. The register is in
good order, and the next useful evidence is a real deploy.

[OWNER] Step 7 remains the only block.
