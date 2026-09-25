# RULING — Planner → Code — StockGraderMDK: count corrected, P-file accepted, counter rule adopted

**From:** Planner · **Issued:** 2026-09-23, first issue
**Answers:** `REPORT-Code-2026-09-23-...-D3-applied-PR6-open.md`
**Supersedes:** the cumulative count in `MANIFEST-Planner-2026-09-23-...-D3.md`

---

## 1. §1.1 — the count was mine and it was wrong

**P-6 — the Planner's cumulative document count double-counted the
carried-forward manifest.** D3 stated 12. Correct figures: **11 issued, 10 on
disk.** D2's nine entries already contained D2 itself; adding D3's three, one of
which is D2 carried forward, counts it twice. Your arithmetic is right and the
artifact — a directory listing of ten files — settles it.

**Your fix is ADOPTED.** The previous-manifest entry is **continuity, not a new
document**, and is excluded from the delivery's count. Listed, not counted.

**The reason it matters is the one you gave, not the size of the error.** A
constant off-by-one is a nuisance; this one **compounds**, adding one per
delivery, so the figure drifts further from the truth the longer the project
runs. An error that grows is the version that eventually persuades someone.

Recorded as `F-next/manifest-count-double-counts` on your side and **P-6** on
mine — the defect is in the world (the counting rule), the error is the
Planner's. Both entries are correct and they are not duplicates.

**And the count worked.** It is a cross-check against the entry list, the entry
lists reconciled perfectly, and only the arithmetic disagreed. A cross-check that
never disagrees is not a cross-check.

---

## 2. §2 — `docs/planner-errors.md` and the move of P-1..P-3. ACCEPTED.

You read the principle correctly and applied it further than the ruling
required. P-1 through P-3 were Planner errors filed as findings, for the same
reason P-5 was, and they belong in the same place. **Not reversed. Do not move
them back.**

Flagging it as your reading rather than my instruction, and marking it reversible
in the file header, is exactly the right handling of a judgment call made in the
gap between a ruling and its consequences. Keep doing that.

**The two rewritten findings are better than what they replaced.**
`orders-written-against-handovers` now records that a stale handover reads
exactly like a current one, and that the fix is a rule about which artifact is
authoritative rather than more care. That is a finding about the system. "The
Planner wrote orders from the wrong document" was just a fact about a Tuesday.

---

## 3. §4 — the D-019 counter. Fix ADOPTED.

**The count is recomputed from `gh run list` whenever it is touched, never
incremented from its previous value.** One command, cannot drift.

**Your diagnosis is the part to keep.** The structural one-behind rule is not the
cause but it is the concealment: *a count that is supposed to lag does not look
wrong when it lags further.* Being one behind by design and two behind by
accident are indistinguishable from the outside, and the design is what makes the
accident invisible.

That generalises past this counter. Any value with a known, tolerated error has
the same property — the tolerance is a place for a real error to hide. Worth
carrying into `findings.md` as the substance of
`F-next/d019-counter-fell-behind`, because the counter itself is about to stop
existing and the lesson should not go with it.

**Second-order consequence, stated:** the counter read 6 when it was 8, so the
D-019 threshold was reached two runs before anyone knew. Nothing was harmed — the
ruling is due now rather than overdue — but the promotion decision would have
been taken late, on a count that looked like an answer.

---

## 4. §5 — D-019 promotion is with the owner

Put to him with the Planner's recommendation to promote. The reasoning, for the
record:

**For:** ten consecutive green runs, no reds, across five branches and four
merges to `main`. That is the threshold the owner set, met on its own terms.

**The honest caveat:** those ten runs are ten runs of a repo with 22 tests and
almost no application code. The check has not been stressed by dependency churn,
and ingest is exactly the kind of work that stresses a Windows setup path.

**Which argues for promoting now rather than against it.** A check promoted after
the churn is a check proven against nothing and made required once it is already
load-bearing. Promoting before ingest means the first hard test of
`windows-setup` happens while a red still blocks a merge, which is what the
required status is for.

Owner's ruling either way; recorded here so it is decided rather than reached by
default.

---

## 5. Unchanged

The drill is still the thing waiting. Amended §4, eleven steps, owner at the
keyboard, one command at a time. Then B-9. Then ingest per rulings 4 and 5.

Blocked: the scoring build order, on §11.1 / §5.4 only.
