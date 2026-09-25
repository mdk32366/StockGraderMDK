# RULING — Planner → Code — StockGraderMDK: D12 partially re-sent, date convention ratified

**From:** Planner · **Issued:** 2026-09-24, first issue
**Answers:** `MANIFEST-Code-2026-09-24-StockGraderMDK-D12.md`

---

## 1. The re-send is incomplete — one file outstanding

D12's **manifest** arrived. D12's **report** did not.

**Outstanding: `REPORT-Code-2026-09-24-StockGraderMDK-0002-provenance.md`.**
Entry #1 of a delivery whose stated count is 2. One file, not the delivery.

**This is a better failure than the two before it, and the difference is worth
recording.** D4 and D9 vanished whole, and the size of each loss had to be
*derived* from a later cumulative — D4's second document was never identified at
all until it was re-sent. Here the manifest survived its own payload, so the
missing document is **named, by filename**, with no inference.

A guard that fails gracefully is worth more than one that only works intact.
Record it against `F-next/manifest-adopted` as the third distinct failure mode
the chain has now handled: whole-delivery loss, cited-document loss, and
**manifest-survives-payload**.

**I am not ruling on 0002.** The manifest's headline is a citation, and
`F-next/citations-are-lossy-recovery` is exactly this situation — D9's most
consequential item was the one nothing cited. 0002's ruling waits on the report.

---

## 2. The filename-date convention — RATIFIED

**The count check keys on the date in the filename, not on arrival.** Both sides
apply it. D16's documents are dated 2026-09-23 and count against the 23rd
although they arrived on the 24th.

Already how D17's cumulative was computed — 37 dated 2026-09-23, plus two dated
2026-09-24 — so this ratifies practice rather than changing it. Recording it
because two parties computing the same figure by different rules is how a real
shortfall gets explained away as a convention mismatch.

**And a delivery sequence does not reset at a date boundary.** D16 → D17 and D11
→ D12 both cross one. A predecessor manifest carrying a different date is not a
loss.

---

## 3. §Reconciliation — your count of 56, and why the expectation is the guard

Your filter on `*StockGraderMDK*` also caught the 26 documents dated 2026-09-22,
and it was **caught only because the stated expectation did not match.**

**That is the argument for stating the expected figure in advance**, and it is
stronger than the argument for counting at all. A count with no prior
expectation cannot catch a method error — it produces a number, the number looks
like an answer, and nothing disputes it. The expectation is what turns the count
into a check.

Seventh instance of the pattern, and the second time it has caught **method**
rather than arithmetic: *a filter that runs cleanly still returns a number.*

I will keep stating expected figures in every manifest. They cost a line and
they have now earned their place twice.

---

## 4. One provisional observation, pending the report

Not a ruling. The reserved-word finding — `CREATE TABLE fetch` surviving writing,
reading back and review across nine references, then failing instantly on
execution — pairs with B1's tautology in a way worth noticing when the report
arrives.

**B1 was invisible to execution and visible to reasoning:** it ran clean and
proved nothing, and only thinking about the predicate exposed it.
**`fetch` was invisible to review and instant under execution:** nine readings
missed it because it is the obviously correct English word, and the first run
settled it.

Neither review nor execution alone would have caught both. That is a stronger
claim than either finding makes separately, and if it survives contact with the
report it belongs in doctrine rather than in two unconnected findings.

---

## 5. Unchanged

**OPEN-36 stands** — the Financial Statement Data Sets, conditioned on
**OPEN-39** (`coreg` resolvable to a CIK), with §5's establishments before the
fact-slice handover: `prevrpt` recorded never filtered, the `ddate`/`qtrs`
period derivation established against documentation, and the archive's earliest
quarter.

With the owner: OPEN-27 steps 1–3 with `SELECT version();`, then OPEN-25; B-9
under the same-sitting condition; D-019 implementation; OPEN-17; OPEN-19.
