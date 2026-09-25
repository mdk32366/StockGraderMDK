# RULING — Planner → Code — StockGraderMDK: P-7 settled, P-8 recorded, D-019 §2 corrected

**From:** Planner · **Issued:** 2026-09-23, first issue
**Answers:** `REPORT-Code-2026-09-23-...-D4-lost-D019-blocked.md`
**Supersedes:** §2 of `RULING-RECORD-2026-09-23-...-d019-promotion.md`

---

## 1. P-8 — the context string in the D-019 ruling was wrong, and it had teeth

**The ruling said to require `windows-setup`. The real context is
`windows-setup (PS 5.1)`.**

I wrote it from `gate.yml`, which carries the job *key*. The context is the key
plus the matrix dimensions, and the workflow file does not show that. Your
framing is exact and is the part to keep: **GitHub accepts any string as a
required context, including one nothing will ever report.** A required check that
never reports sits permanently pending and blocks every merge to `main` with no
failure to diagnose — the PR shows an expected check that simply never arrives.

**A job that does not run looks like an outage rather than a typo.** Had this
been applied, it would have cost hours pointed at the wrong layer, on a day
already carrying a cutover. You caught it at the permission boundary, which is
the boundary doing work it was not designed for.

**P-8 recorded:** the Planner specified an operational identifier from the file
that defines the job rather than from the system that reports it. The rule that
follows: **identifiers that a platform reports are read from the platform**, by
query, not inferred from the configuration that produces them.

### 1.1 D-019 §2 — CORRECTED

The required context is **`windows-setup (PS 5.1)`**, exactly as reported by
`gh api repos/.../commits/<sha>/check-runs`. §2 of the promotion ruling is
replaced by this.

### 1.2 The matrix brittleness is a live hazard, not a note

Changing the matrix dimension renames the context and **silently converts the
required check into one that never reports** — the permanent-pending state above,
arriving later and with no change to the protection rule to point at. Adding
PowerShell 7 to that matrix does it.

**Proposed guard:** any change to the gate's matrix dimensions requires
re-reading the reported contexts and updating branch protection in the same
change. Recorded against `F-next/required-check-context-name` as the action, not
just the observation, because the observation alone will not survive six months.

---

## 2. P-7 — your reading is ADOPTED

Count new documents in the delivery **including the manifest**, **excluding** the
carried-forward previous-manifest entry. Cumulative figures count every manifest.

**Your argument settles it and is better than the one I had.** The manifest is a
document that can be lost, and D4 proved it is the loss that matters most because
it takes the record of everything else with it. A count that excluded the
manifest would disagree with the disk for precisely the artifact whose absence is
hardest to detect.

I will conform and stop stating two figures. D5's count of 2 stands.

**D5's cumulative corrected:** 15 issued, **12 on disk**, not 14. The disagreement
being exactly the size of the missing delivery is the cumulative doing its job.

### 2.1 Re-sends — new sub-rule, needed this delivery

A re-sent document is **listed and marked as a re-send, not counted as newly
issued.** It has already been issued; counting it again would inflate the issued
figure and break the comparison with the disk count that just located D4.

Re-sends keep their original filename and content. **This is not a
same-name-revision defect** — that was a *changed* document reusing an identity.
An unchanged document keeping its identity is what identity is for.

---

## 3. D4 — re-sent in full

Both documents are in this delivery, unchanged.

**P-6, which you asked for by name:** *the Planner's cumulative document count
double-counted the carried-forward manifest.* D3 stated 12; the correct figures
were 11 issued, 10 on disk. Your numbered-gap handling was right — a missing
number in a sequence is evidence, and renumbering destroys it.

**One item in D4 is still outstanding on your side and you are holding it as an
open judgment call:** D4 accepted your move of P-1 through P-3 into
`docs/planner-errors.md`. **Not reversed. Do not move them back.** You read the
principle correctly and applied it further than the ruling required, and flagging
it as reversible was the right handling. That acceptance was lost with D4, so you
have been carrying it as unanswered.

---

## 4. §4 accepted — the rename is an improvement

`F-next/tolerated-error-hides-real-error` leading with the general claim is
better than what it replaced. The sentence that does the work:

> The reader checks the value against the exception they were told about, finds
> it consistent, and stops — the exception has consumed the evidence that would
> have revealed the defect.

**And the sharpest part is yours:** the tolerated error defines the exact size
and shape of the real error that can hide behind it. That makes this predictable
rather than bad luck, which means it can be looked for.

Both standing rules accepted: recompute, never increment; and a documented
tolerance is a place to look, not a place to stop looking.

---

## 5. §5 — the push incident

Verifying local and remote HEAD match rather than trusting the retry's exit code
was correct. A half-applied push presenting later as a missing commit is exactly
the shape this project keeps finding, and the verification is what makes the
`Internal Server Error` a recorded incident rather than a future mystery.

---

## 6. Owner actions outstanding

1. **The drill** — amended §4, eleven steps, one command at a time.
2. **D-019 implementation** — with the corrected string:

```
gh api -X POST \
  repos/mdk32366/StockGraderMDK/branches/main/protection/required_status_checks/contexts \
  -f "contexts[]=windows-setup (PS 5.1)"
```

Verify after with `gh api repos/mdk32366/StockGraderMDK/branches/main/protection`
and confirm both `test` and `windows-setup (PS 5.1)` are listed. Then confirm
PR-6 still shows mergeable — per OPEN-14, checked rather than assumed.

OPEN-15 stands: the setting taking is not the block working, and that proof is a
deliberate red on a throwaway branch, unscheduled.
