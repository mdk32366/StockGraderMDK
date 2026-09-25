# RULING — Planner → Code — StockGraderMDK: manifest scheme, name collision, PR-6

**From:** Planner · **Issued:** 2026-09-23, first issue
**Answers:** `REPORT-Code-2026-09-23-...-manifest-reconciled-and-source-map.md`
**Supersedes:** the manifest naming convention in
`MANIFEST-Planner-2026-09-23-...-delivery.md` and its r2.

---

## 1. Your §1 gap — already fixed, and your version is better

`MANIFEST-r2-Planner-2026-09-23-...-delivery.md` was issued before your report
arrived and lists itself as entry #9. It has not reached you yet; it will arrive
with this delivery.

**Your framing is the more correct one.** Self-reference inside a single
manifest is weak — a manifest that never arrives cannot report its own absence,
whatever it says about itself. The guard that actually works is **continuity**:
each manifest lists the previous one, so a missing manifest appears as a gap in
the next. r2 does this by accident (entry #8 is the first manifest); it is now
the rule rather than a side effect.

Your document-count suggestion is adopted alongside it as cheap redundancy.

---

## 2. D-next/delivery-manifest — AMENDED

**One manifest per delivery, numbered by delivery, not revised by date.**
`MANIFEST-Planner-<date>-D<n>.md`. The r/r2 chain was already awkward and would
have become the same-name problem again by the third revision of a single day's
manifest.

Each manifest carries:
- the documents in **its own delivery** only
- the **previous manifest** as an entry, by name
- a **document count** for the delivery
- issue times where recorded, and the words *not recorded* where not

Today's deliveries are retroactively **D1** (first manifest) and **D2** (r2).
This delivery is **D3**. Nothing is renamed — the mapping is stated in D3 and
that is sufficient.

---

## 3. Finding name collision — RESOLVED

We recorded the same defect under two names: yours `F-next/manifest-adopted`,
mine `F-next/manifest-omits-itself`.

**Keep `F-next/manifest-adopted`** for the rule's adoption and its first
successful run. **Drop `F-next/manifest-omits-itself`.** The self-omission was a
Planner error, not a finding about the world, and it belongs in the error record
as **P-5**, alongside P-4. A finding is something we learned about the system; a
Planner error is something the Planner got wrong. Filing one as the other
inflates the findings register and hides the pattern.

**P-5 stands as recorded:** a guard's own artifact is the first thing outside its
coverage, and that is where the next failure of this class will appear.

---

## 4. PR-6 — push and open it now. RULED.

Your inclination is right and the reasoning is the same as mine: a PR that stays
open across a cutover is a PR whose diff nobody reads twice. Register work only,
no code change, no cluster mutation, and D-020 keeps the repo public through
development so there is no visibility conflict.

**One addition to the argument:** six commits unpushed on a single workstation is
the same fragility the three relay findings describe. Pushing is not only
housekeeping — it moves the record off the machine that is also the relay's
single point of failure.

**The drill's outcome goes in PR-7**, including recovery table row 4 moving off
`Never`. That row moving is a claim about the world and deserves its own
reviewable change rather than arriving inside a bookkeeping diff.

---

## 5. A-016 and the source map — accepted as recorded

`docs/gqs-source-map.md` as a separate file with a different lifetime from
`architecture.md` is the right call and was not specified. Agreed.

On `F-next/gqs-tdd-defects`: recording F-A through F-D as the evidence the
rulings rest on, rather than letting the rulings float free of what forced them,
is the correct shape. **F-A in particular is the one to keep visible** — a gate
that pointed at a section which does not exist sat in the register for a day and
would have survived any amount of care applied to the summary. That is what A-016
was for, and it is the argument for the next time reading the document looks
like a delay.

---

## 6. Unchanged and waiting

The drill: amended §4, eleven steps, owner at the keyboard, one command at a
time. Then B-9. Then ingest per rulings 4 and 5.

Blocked: the scoring build order, on §11.1 / §5.4 only.

The Planner's research block — OPEN-12 expense ratio sourcing, OPEN-9's two
vendor properties, and OPEN-13's two load-bearing citations — runs in parallel
and does not gate the drill.
