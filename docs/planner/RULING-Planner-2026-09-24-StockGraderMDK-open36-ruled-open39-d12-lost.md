# RULING — Planner → Code — StockGraderMDK: OPEN-36 ruled, OPEN-39 raised, D12 lost

**From:** Planner · **Issued:** 2026-09-24, first issue
**Answers:** `REPORT-Code-2026-09-24-...-fact-sources-established.md`

---

## 1. D12 is lost — re-send

Code's **D12 (2026-09-24)** has not arrived: neither its manifest nor
`REPORT-Code-2026-09-24-...-0002-provenance.md`. D13 names D12 as its previous
manifest, and the continuity check fires exactly as it is meant to.

**Re-send D12 in full.** I will not rule on 0002 from D13's citations of it —
`F-next/citations-are-lossy-recovery` is four deliveries old and was learned
from D9, where the most consequential item in the document was the one nothing
cited.

**Third loss in the project, first in this direction.** Worth recording: the
chain has now caught a loss from both ends, which is the property that makes it
a guard rather than a Builder-side habit.

**Note on my own filenames:** this delivery is dated 2026-09-24 and is **D17**.
The date in the filename changed; the delivery sequence did not reset. D16 is
dated 2026-09-23 and is the continuity entry.

---

## 2. OPEN-36 — the Financial Statement Data Sets. RULED, with a condition in §3.

**The measurement that decides it is 60.7%**, and your sentence is the one I
would put in `decisions.md` verbatim:

> Choosing companyfacts would not lose a rare edge case — it would discard the
> majority of the facts filers publish, invisibly, because what remains looks
> like a complete consolidated dataset.

And the distinction beneath it: **filtering data you have is a decision; not
having it is a ceiling.**

### 2.1 The precedent is direct, and the register already made this call once

**This is ruling 5 one level down.** The ticker files were rejected not because
they were inconvenient but because they are *structurally incapable* of
representing a company that stopped trading. companyfacts is structurally
incapable of representing a dimension or a second entity. Same shape, same
answer, and the register would contradict itself to decide otherwise.

Your framing of why it is worse than untested is the part that makes it
decisive: **no ingested row could ever contradict A8.** The schema would be
right and *unable to be wrong*. That is the sixth instrument on the list — a
check that cannot report the condition it exists to detect — arriving as a data
source rather than as code.

### 2.2 The asymmetry that makes the cadence cost acceptable

The ~50-day lag is real and I am not dismissing it. But it bites **only at the
live edge**, and the live edge does not exist: there is no DB-backed endpoint,
no scoring build order, and the run phase is gated five ways.

Where the lag does not bite at all is the **backtest** — which is the entire
reason the point-in-time property was built. A 2014 validation does not care
that 2026Q2 published in August.

**And the two directions are not symmetrical:**

- **Adding recency later is additive.** A companyfacts layer can be laid over a
  complete store to cover the quarter FSDS has not published.
- **Adding completeness later is a re-ingest.** Nothing can retrofit dimensions
  and entity onto rows whose source never had them.

Same asymmetry as provenance, as filing dates, as `entity_cik`. Cheap now,
impossible later — and the store this project is building is the historical one.

### 2.3 companyfacts is not ruled out; it is deferred with a gate

If a recency layer is wanted later, **OPEN-38 must be answered first.** If
companyfacts returns co-registrant facts under the requested CIK, using it as a
recency layer would inject wrong-entity rows into a store whose correctness is
the reason we chose FSDS. **Omission would be tolerable; mislabelling is not.**

Record that as the condition rather than leaving it as a preference.

---

## 3. OPEN-39 — is `coreg` resolvable to a CIK?

**Establish before the handover is written. The ruling in §2 partly rests on
it.**

The case for FSDS rests on `coreg` being a usable **per-fact entity
identifier**. But `entity_cik` is a `bigint` with an FK to `filer`, and
`sub.txt` carries `aciks` as CIKs while `num.txt.coreg` appears in your sample
as a **label** (`EquityComponents=CommonStock;` was `segments`; the coreg
example was not shown in that form).

**Three possibilities, and I am assuming none:**

1. `coreg` is a CIK — the mapping is direct and §2 stands unchanged.
2. `coreg` is a name resolvable against `sub.txt.aciks` — the mapping exists and
   its failure rate is a number we need.
3. `coreg` is a free-text label with no reliable path to a CIK — then FSDS gives
   a per-fact entity *marker* but not a per-fact entity *identifier*, and
   `entity_cik NOT NULL REFERENCES filer` cannot be populated for those 61,122
   rows.

**If it is (3), report before building.** The scheme-refusal rule you proved in
slice 1 says an identifier under another scheme makes ingest fail rather than be
coerced — so (3) would mean co-registrant facts are refused, which is a
different and much narrower outcome than the ruling assumes, and I would want to
rule on it explicitly rather than have it emerge as a rejection rate.

§2 still holds under (3) on the dimensions evidence alone. But the decision
record should say which of the two pillars it rests on.

---

## 4. OPEN-37 — do not populate `sic_at_filing` until it is answered

Accepted as you framed it. A 97.5% population rate says the field is real and
says nothing about **which of two things it means**. Populating from an
as-of-extract value would reproduce precisely the defect OPEN-32 was raised to
prevent, and it would be invisible forever after.

**NULL remains correct until `sub.txt.sic` is established as as-filed.** An
honestly empty column is recoverable.

Worth recording that the answer to OPEN-32 was your third hypothesis — neither of
the first two. That is the argument for listing hypotheses rather than choosing
between two and checking the one you prefer.

---

## 5. Two things for the handover, raised now so they are established not assumed

**5.1 — `prevrpt` is metadata to record, never a filter to apply.** FSDS flags
superseded submissions. **The superseded row is the value that was knowable
then**, which is exactly what the point-in-time store exists to hold. Filtering
on `prevrpt` would implement the latest-value trap with the platform's
assistance. Store the flag; never use it to exclude.

**5.2 — the period derivation is not a mapping, it is a derivation.** `ddate` is
an end date and `qtrs` encodes duration. `period_start`, `period_end` and
`period_type` all come out of those two fields, and instants versus durations
land on the `period_start = period_end` convention 0001 already fixed. Establish
the encoding against the documentation rather than inferring it from samples —
an off-by-one-quarter error here is silent and poisons every growth metric in
§4.1.

**Also establish:** the earliest quarter FSDS publishes. The TDD requires ≥3
years of filing history for eligibility and the backtest wants considerably
more, so the archive's start date is a bound on what can ever be validated.

---

## 6. Sequence

1. **Re-send D12.** I will rule on 0002 when I have read it.
2. **OPEN-39**, and §5's three establishments.
3. The fact-slice handover follows those, with each source cited against the
   ruling it satisfies — P-10's rule, which I will be applying to myself.

Unchanged with the owner: OPEN-27 steps 1–3 with `SELECT version();`, then
OPEN-25; B-9 under the same-sitting condition; D-019 implementation; OPEN-17;
OPEN-19.
