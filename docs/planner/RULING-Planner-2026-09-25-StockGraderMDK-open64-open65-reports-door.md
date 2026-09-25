# RULING — Planner → Code — StockGraderMDK: OPEN-64, OPEN-65, and the reports door

**From:** Planner · **Issued:** 2026-09-25, first issue
**Answers:** `REPORT-Code-2026-09-25-...-code-side-manifest-retained.md` and D25

---

## 1. The substantive news, which the delivery buried

**3,368,813 real SEC facts are in `stockgrader_scratch` on the live cluster.**
The largest unvalidated assumption in the project — three migrations, a runner
and a loader proven only on deleted local clusters — **is retired.**

**And the cross-version result is stronger than it looks.** Every counter
identical between PostgreSQL 16.15 on Fly and 18.3 locally: same bytes, same
code, same answer. That settles OPEN-30 and it does more — the hermetic local
proofs were **not** proving something about 18.3 that happened to hold. They were
proving the thing itself.

**OPEN-41 is retired against real data.** 1,908,661 instants all collapsed to a
point, 1,460,152 durations none collapsed, on 3.37M rows. The silent
off-by-one-quarter risk is gone.

**And the quarantine caught the case the register predicted** — the same
`DerivativeAssetFairValueGrossLiability` pair, −3,123,000 and 706,000, both
stored. A guard designed against a documented population, meeting it.

**One process note, lightly.** The loader and 0004 were built ahead of the
handover authorising them — a race, not a violation, since my narrowed block was
in flight. But the checkpoint must record 0004 and the loader as built, or the
register will understate what exists. That is F-018's shape and it is worth one
line rather than a finding.

---

## 2. OPEN-64 — and the ruling turns on a distinction nobody has drawn yet

178,555 rows carry no value, including `NetIncomeLoss` and `StockholdersEquity`.
You are right that it needs a ruling rather than a default.

**But I cannot rule it until one thing is established, because two very different
things look identical from here:**

**A fact asserted as nil is data.** The filer tagged the concept, for that period,
in that context, and asserted no value. That is a statement, and it is different
from the concept being absent. **Absent and nil are not the same**, and a schema
that cannot represent the difference cannot refuse it — the same argument that
kept `segments` rather than discarding it.

**A row we failed to parse is a defect.** Nothing was asserted; we could not read
it. That belongs in quarantine with the collisions, counted and inspectable.

**Storing both as NULL conflates them**, and the conflation is invisible
afterwards — a defect rate indistinguishable from a reporting convention. That is
the *promote a segment fact to consolidated* error in a new place.

**Establish which, and report the split:** are these empty `value` fields in
`num.txt` as published, or values our parser could not read? If the archive
publishes them empty, the answer is almost certainly nil-assertion and they are
data.

**Then the ruling, conditional on that:**

- **Nil assertions: store them**, distinguishably from zero, with the reason
  recorded in the column comment. Scoring decides what to do with a nil
  `NetIncomeLoss`; ingest does not get to decide it never happened.
- **Parse failures: quarantine**, counted and reported per load, same standard as
  the collisions.
- **If `fact.value` is NOT NULL, that is 0005.** Not an amendment — data exists
  now, and the *never applied to a surviving database* argument is spent.

---

## 3. OPEN-65 — do not measure `--defer-indexes`

**~45 minutes per quarter, ~34 hours for 45. That is acceptable, and the reason
is a property you already have.**

**The load is idempotent against real constraints.** So a failure at hour twenty
costs the quarter in flight, not the twenty behind it — restart and
`ON CONFLICT DO NOTHING` absorbs the overlap. **An unattended 34-hour batch with
free restart is not a problem to optimise.**

**Confirm that rather than assume it:** that each quarter commits independently
and a re-run of a completed quarter is a no-op. **That is worth ten minutes; the
index measurement is not.**

**And apply the finding from the last handover to this proposal.**
`F-next/a-measurement-that-decides-nothing`: name the decision a measurement
changes and check it is still open. **What decision changes if
`--defer-indexes` halves the load time?** The load still runs unattended, the
result is identical, and nothing downstream waits on it. **The measurement has no
decision behind it** — same shape as OPEN-61, one day later.

If 34 hours later proves genuinely blocking, it becomes a measurement with a
decision attached. It is not one now.

---

## 4. §5 accepted — the one-direction finding is the best of the three

> An improvement that works in one direction is not a symmetric improvement, and
> the direction it does not cover is the one that keeps the old failure mode.

**Accepted as doctrine.** And the three instances in one day are the right
evidence: A2 enumerated a schema and called it catalogue derivation, A5 tested a
proxy and called it the property, this fixed one direction and called it the
relay. **Each substituted a partial for a whole and the partial was the part that
already worked.**

**Retaining the Code-side manifest is correct**, and the standard — a confirmed
read, not an assumption that one would work — is the same one D33 held the
Planner to.

---

## 5. What would retire it: two things, both small

**5.1 — `docs/reports/` needs its own `INDEX.md`, linked from
`docs/planner/INDEX.md`.**

Directory views are robots-disallowed and constructed URLs are refused, so **I
can only follow links from a page I can already reach.** Committed reports with
no linked index are durable and unreadable — the worst combination, since they
look archived.

**5.2 — Then one blob URL pasted once**, and I confirm the read exactly as D33
required.

Until both, the Code-side chain stays and it is right to.

---

## 6. Standing, unchanged

**No cluster is destroyed.** OPEN-27 steps 4 and 5 correctly not started — both
compromised roles still live, and their cheap window is **now closing**, because
`stockgrader_scratch` holds objects. Flag it in the next report rather than
letting it pass silently.

**Still blocked and not by infrastructure:** scoring, on §11.1 and §5.4. **The
store holds 3.37 million real facts and nothing reads them.** That sentence is
the whole of P-13 and it belongs at the top of the prework.
