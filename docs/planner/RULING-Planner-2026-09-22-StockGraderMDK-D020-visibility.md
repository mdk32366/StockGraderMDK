# RULING — Planner → Code — StockGraderMDK: D-020, and a defect in KEEL V10 itself

**From:** Planner · **Date:** 2026-09-22
**Supersedes:** §2 of `RULING-Planner-2026-09-22-StockGraderMDK-post-keel.md`
**Owner ruling received:** the repo goes private when the application has
**completed development**, not on the first live deploy.

---

## 1. D-020 — the repo stays PUBLIC. RULED by the owner.

**Choice:** `StockGraderMDK` remains public through development, connected to
the Planner. It goes private when development is complete.

**Rejected:** going private on the first live credential or first live deploy —
the wording in KEEL-2 Step 17 and KEEL-3 line 17. That wording is superseded.

**Forced by:** the owner's standing rule, which matches KEEL-1 Principle 10's
body ("private once the project is production-stable") and contradicts the two
checklists.

**Consequences, recorded so nobody re-derives them:**
- The Planner keeps direct repo access for the whole build. No snapshot
  hand-carrying.
- The repo must stay free of real credentials and real user data for longer
  than the Checklist assumed. The hygiene secret scan is therefore load-bearing
  for months, not days, and every future credential decision is made under a
  public repo.
- When the database arrives (D-009), the connection string, the recovery
  credential, and any cached filing data all land while the repo is public.
  None of them may touch the tree.

**[OWNER] — one thing still to name.** "Completed development" is a sentence,
not a mechanism. KEEL's own rule: where a specification names a stopping point,
it names the thing that stops. Name the observable that makes it true for this
project, so it can be recognised rather than argued. Candidates, none ruled:
- the first real (non-synthetic) user of the API other than the owner, or
- the first stored data that cannot be rebuilt from public sources, or
- an owner declaration recorded as a dated D-entry.

## 2. The defect in KEEL V10

This is bigger than this project, so it is stated plainly.

| Document | What it says today |
|---|---|
| KEEL-1, Principle 10, body | "goes private once the project is **production-stable**" — the current rule |
| KEEL-1, Principle 10, headline | "Go private when it goes **real**" — undefined, and the source of the drift |
| KEEL-2 Step 17 | "First real credential, first real user data, or first live deploy — **whichever comes first**, the repo goes private the same day" — superseded |
| KEEL-3 Quick Card, line 17 | same superseded wording |

**The rule was amended in one document out of three, and the two that were
missed are the operational ones** — the field manual and the card. A person
laying a Keel reads those, not the essay. On this project the Planner read the
Checklist and treated Step 17 as triggered on day one. The owner's ruling is
what caught it.

This is KEEL's own failure mode, named in its own pages: doctrine that lives in
one place has not been issued. The Assumption Register's blood line says the
same thing about numbering that started before the document existed.

**Also note what V10's own stamp claims.** KEEL-2 and KEEL-3 are stamped V10 as
reviewed sets, and KEEL-3 carries no "INSPECTED, UNCHANGED" note at all. An
inspection that did not catch the contradiction is recorded as an inspection
that passed.

**Proposed for KEEL V11** (owner's doctrine, so proposed only):
1. Align Step 17 and Quick Card line 17 with Principle 10's body.
2. Replace Principle 10's headline "when it goes real" with the observable,
   since the vague headline is what allowed two documents to drift from the body
   under it.
3. Add the scar: *a rule amended in the essay and not in the checklist is a rule
   the next person will not follow, because the checklist is what gets read on
   day one.*
4. Note in the travelogue that the V10 inspection pass did not detect it, so the
   next inspection knows that "INSPECTED, UNCHANGED" has been wrong once.

## 3. PR-4 additions

On top of the post-Keel ruling's §3 list:

- **decisions.md:** D-020 as **RULED** (not open), with the rejected alternative
  and the consequences above.
- **findings.md:** F-013 — KEEL V10 states the go-private rule three ways across
  three documents, two of them superseded. Artifact: KEEL-1 Principle 10 body,
  KEEL-2 Step 17, KEEL-3 line 17. Consequence: the Planner applied the
  superseded rule until the owner corrected it.
- **testplan.md:** under *How to read a red*, add — when doctrine and a checklist
  disagree, the checklist is what gets followed, so an amendment lands in both
  or it has not landed.
