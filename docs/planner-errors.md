# Planner errors — what the Planner got wrong

*StockGraderMDK · opened 2026-09-23*

**Why this file exists.** Ruling
`RULING-Planner-2026-09-23-...-manifest-scheme-and-pr6.md` §3 drew the line:

> A finding is something we learned about the system; a Planner error is
> something the Planner got wrong. Filing one as the other inflates the findings
> register and hides the pattern.

`findings.md` answers *how do we know?* This answers *what did we get wrong, and
what rule came out of it.* Entries are numbered `P-n` by the Planner and are
self-recorded unless noted.

**Builder note:** P-1 through P-3 were first recorded inside
`findings.md` as `F-next/orders-written-against-handovers`, before this file
existed. They are moved here on the ruling's principle. The finding remains, but
now records *what was learned* rather than enumerating the errors. Reversible if
the Planner wants them back — say so and they go back.

---

### P-1 — Orders were written against the last handover, not the register
**Date:** 2026-09-23 · self-recorded
The steps 5–6 handover was written from the 2026-09-22 handover, which said
steps 5–6 were outstanding. They had been executed and merged in PR-5 the same
day. The register was never read before orders were written against it.
**Rule adopted:** orders are written against `decisions.md`, `findings.md`,
`assumptions.md` and `testplan.md` — **not against the last handover.** A
handover records what was true when it was written; the register records what is
true.

### P-2 — Finding numbers assigned from a document rather than from `findings.md`
**Date:** 2026-09-23 · self-recorded
F-018 and F-019 were reserved for content that already had other content.
**Rule adopted:** the `F-next/<short-name>` convention. The Planner does not
assign numerals.

### P-3 — Speculation dressed as a finding
**Date:** 2026-09-23 · self-recorded
`fly mpg users create` was named a "suspected new offender" when the F-014
amendment had already settled that it prints `Name` and `Role` only. On the
strength of that speculation the Planner invented a disposable `sg_a017_test`
account **and a carve-out to authorise it** — for a test already run as
`builder_a017_probe` that had already held. Both withdrawn.
**Why it matters:** reasoning about what a command *probably* does is not a
finding, and dressing it as one spends the register's credibility — which is the
only thing making the other entries worth reading.

### P-4 — A ruling record reissued under its predecessor's filename
**Date:** 2026-09-23 · self-recorded
The 07:29 owner-ruling record was revised at 07:32 by **editing the delivered
document in place**, with no supersession marker in the body. Only a status line
differed. The Builder caught it on a 1,651-byte difference in a directory
listing — **luck, not a guard.**
**Rule adopted:** **filenames are not identity.** A revision carries a revision
marker in its filename and a supersession block in its body naming what it
replaces and what changed. The §4-amended ruling did this correctly and is the
pattern.
**Consequence had it been missed:** the register would have recorded two open
questions that were in fact ruled, and the archetype classifier work would never
have been opened.

### P-5 — The manifest omitted itself
**Date:** 2026-09-23 · self-recorded
The first manifest listed seven documents and was itself an eighth. **By its own
rule** — *a document not on the manifest was not issued by the Planner* — **it
invalidated itself.** It also carried no revision marker, so a second manifest
the same day would have reused its filename: **P-4 reproduced inside the control
written to prevent P-4.**
**Recorded because the pattern matters more than the instance:** *a guard's own
artifact is the first thing outside its coverage, and it is where the next
failure of this class will appear.*
**Resolution:** the D-numbered manifest scheme, where **continuity** — each
manifest naming the previous one — is the guard rather than self-reference. A
manifest that never arrives cannot report its own absence, whatever it says
about itself. See `D-next/delivery-manifest`.
