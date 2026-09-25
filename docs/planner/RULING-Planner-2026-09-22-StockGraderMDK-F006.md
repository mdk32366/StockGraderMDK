# RULING — Planner → Code — StockGraderMDK: F-006, artifact v4

**From:** Planner · **Date:** 2026-09-22
**Answers:** `REPORT-Code-2026-09-22-StockGraderMDK-F006-BLOCKED.md`
**Amends:** the lay-the-Keel order and the F-004/F-005 ruling. Everything not
changed here stands.

---

## 1. Rulings

1. **F-006: option (c), ASCII and BOM. Logged as D-013.** The BOM protects
   against the next pasted character. ASCII protects against the next editor
   that strips the BOM. Either half alone leaves a path back to this defect.
2. **The `.ps1` guard goes in v4, not in a later PR.** The gate never executes
   `setup.ps1`, so without the guard nothing in CI can see this class of
   defect. That is the Principle 9 shape. Deferring it would ship a known-blind
   gate on day one.
   - A Windows CI job that actually runs `setup.ps1` under PS 5.1 is **D-014**,
     proposed as a PR after branch protection, alongside D-012.
   - D-014 depends on A-008: that the `py` launcher on a runner finds
     setup-python's 3.12.
3. **F-006 supersedes your §3.3 conclusion. It is recorded, not rewritten.**
   - F-006 carries a Planner note too: I listed the unbuilt Dockerfile as open
     but never listed the unrun installer. That was the same gap twice, and I
     recorded only one instance.
4. **On the hand-made venv you didn't create:** correct call. That is what D-011
   is for.

## 2. Artifact v4. It replaces v3; v3 is withdrawn.

`StockGraderMDK-keel-scaffold-v4.zip`, SHA-256:
`d21f51e4f056b3fe7cd587d565ef81b1f53760d8f6e65ec647cd345510f9c03f`

**Declared v3 → v4 delta.** Note that it is wider than your request, because
the guard is code.

| File | Change |
|---|---|
| `setup.ps1` | Both U+2014 replaced by `-`. Written UTF-8 **with BOM** (`ef bb bf`), pure ASCII after it. No other change. |
| `tests/test_hygiene.py` | Adds `test_powershell_scripts_are_safe_for_windows_powershell_5`. The 3 existing tests are unchanged. |
| `docs/findings.md` | F-006 added; amendment line on F-002 (count 21 → 22) |
| `docs/decisions.md` | D-013, D-014 added |
| `docs/assumptions.md` | A-008 added |
| `docs/testplan.md` | G-9 row, OPEN-4 row |

- The same 37 entries.
- Everything else is **byte-identical to v3**, including `tests/contract/openapi.v1.json`.
- If anything else differs, STOP.

**Checks on `setup.ps1` specifically:**
- The first 3 bytes are `ef bb bf`.
- No byte after them exceeds `0x7F`.
- Line endings are LF, as in v1–v3. `.gitattributes` makes them CRLF on
  checkout; PS 5.1 accepts either.

## 3. What was proven here, and what was not

**Proven in the Planner sandbox (Linux):**
- The guard went **FAILED** against the unfixed v3 file. It reported the BOM
  plus `e2 80 94` on lines 1 and 27, exactly your finding.
- On the fixed file, re-inserting an em-dash with the BOM kept → FAILED.
- On the fixed file, stripping the BOM from the ASCII body → FAILED.
- Restored → 22 passed.

**Not proven:** that Windows PowerShell 5.1 parses the fixed file. There is no
PS 5.1 here, and G-9 proves bytes, not a parse. That is OPEN-4, and your Step 3
run closes it.

## 4. Sequence

- **Step 1** re-runs against v4: the hash, the declared delta, and the
  `setup.ps1` byte checks above.
- **Step 3** as amended by the F-004 ruling: `setup.ps1` with the network on,
  then pytest alone with the network off. Expect **22**. Report yours.
- In your §4a trip table, **include the new guard.** Design your own trip for
  it, blind, as for the others.
- **[OWNER]:** Step 7 is still outstanding and gates Step 8.
