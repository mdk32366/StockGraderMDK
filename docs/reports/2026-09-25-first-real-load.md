# REPORT — Code → Planner — StockGraderMDK: 3.37 million facts are in a real cluster

**From:** Code (Builder) · **Issued:** 2026-09-25, first issue
**Follows:** `2026-09-25-segments-grammar-undocumented.md`
**Branch:** `pr6-backup-strategy`, HEAD `6b45c09`, pushed · **Suite: 96/96**
**Fly cluster mutations: `stockgrader_scratch` only — schema applied, one quarter loaded**
**No money spent. `stockgrader` untouched. No cluster destroyed.**

---

## 1. The headline

**The largest unvalidated assumption in this project is gone.**

Four migrations, the migration runner, the EDGAR client, slice 1's patterns and
the fact loader had been proven **only on local throwaway clusters that were then
deleted.** They have now met a Fly cluster, and 3,368,813 facts are in it.

**OPEN-27 steps 1–3 complete. OPEN-30 closed. Migrations 0001–0004 applied.
First real data loaded.**

---

## 2. The counts are identical across two major versions

The live cluster runs **PostgreSQL 16.15**. Everything was developed on **18.3**.

| | Local 18.3 | **Fly 16.15** |
|---|---|---|
| facts seen | 3,608,711 | **3,608,711** |
| facts loaded | 3,368,813 | **3,368,813** |
| refused — co-registrant | 61,134 | **61,134** |
| refused — no value | 178,555 | **178,555** |
| refused — filing absent | 0 | **0** |
| collapsed duplicates | 14 | **14** |
| quarantined | 195 | **195** |
| extension facts | 259,489 | **259,489** |
| accounting | BALANCED | **BALANCED** |

**Same bytes, same code, same answer.** I said before the run that a divergence
would stop the work. There was none, and that is worth more than a green result
because the failure condition was stated first.

---

## 3. The two checks that mattered more than the counters

**3.1 The period derivation, on 3.37M real rows.**

```
duration   1,460,152    collapsed to a point:         0
instant    1,908,661    collapsed to a point: 1,908,661
```

**A clean 100% / 0% split.** OPEN-41 warned that an off-by-one-quarter error here
is **silent**, poisons every growth metric in §4.1, and that a sample-inferred
encoding *would look right on the samples it was inferred from.* This is the
derivation meeting 3.4 million rows instead of a fixture.

**3.2 The quarantine caught the case the register itself documented.**

`fact_collision` holds 195 rows. `DerivativeAssetFairValueGrossLiability` carries
competing values including **−3,123,000 and 706,000**, and **645,000 and
1,591,000** — **the exact pairs recorded** in
`F-next/fsds-violates-its-own-documented-key` when the collision was first
measured, months of reasoning ago and in a different session.

**Both sides are stored.** `ON CONFLICT DO NOTHING` would have kept one and
discarded a genuinely different value with no record — the failure 0001, 0003 and
the quarantine exist to make impossible. **It is now observed rather than
argued.**

`coverage_window` reports `2026q2..2026q2`, 1 quarter, **0 gaps**, refused
239,689 = 61,134 + 178,555.

---

## 4. What went wrong, in order, because that is most of the value

**4.1 A2 fired on first contact with a real database.** `keel_disposable_canary`
— a hand-placed disposability marker whose **presence** makes a database safe to
truncate and whose **absence** refuses the harness against production. A2 must
exempt it; A3 would refuse a static exemption on production where no canary
exists. **Two correct guards in direct conflict.** Resolved with a conditional
exemption. **Undiscoverable hermetically** — a local throwaway database has no
canary. See **F-029**.

**4.2 The first proxy load died mid-`executemany`.** One round trip per row is
3.4 million round trips inside one transaction. The connection closed part-way.
**The transaction rolled back whole** — `fact`, `filing`, `fetch_log` and
`coverage_quarter` all verified at 0 afterwards. Replaced with COPY into a
staging table plus one server-side insert, so idempotency stays the schema's
property.

**4.3 I converted the facts and left `load_submissions` on `executemany`.** The
round-trip argument applies to every insert path over a proxy, not only the
largest.

**4.4 The stall was index maintenance, and it is OPEN-57 on the write path.**
`pg_locks` showed `RowExclusiveLock` on `fact` and **all seven** of its indexes.
Seven index structures per row, 3.4M rows, **1 GB of shared CPU**. Locally that
phase costs ~50 s because the indexes sit in RAM.

> **Both previous attempts to settle Basic's adequacy measured READS.** Neither
> touched ingest. The tier's first real constraint appeared somewhere nobody was
> looking — and on quarter one of forty-five, in a disposable database.

**Not a correctness problem.** It completed and balanced. **A cost problem:**
~45 min per quarter is **~34 hours** for 45. Recorded as **OPEN-65** with two
non-exclusive levers — `--defer-indexes` (built, and proven to reproduce all five
index definitions exactly) and a larger tier, which the owner has ruled is not
cost-blocked.

---

## 5. Three probes that reported on work that had not happened

Recorded as **F-033** because they are one shape and I produced all three in one
sitting.

| | What it claimed | What was true |
|---|---|---|
| `tup_inserted = 0` | nothing had been inserted | the counter is not flushed mid-transaction; it could not answer the question |
| index drop-and-rebuild check | `DEFINITIONS IDENTICAL` | the rebuild had crashed on a syntax error; it compared a file to itself |
| red-test precondition | `SETUP FAILED` on every case | **correct** — it asserted `"applied 3 migration"` and 0004 had arrived |

**The third is the one that failed safe**, and the difference is the lesson: it
compared against a **stated expectation**, so reality moving made it complain.
The other two compared a thing to itself, or read a counter whose semantics were
assumed.

> **A probe that cannot fail is not evidence.** The test is to ask what result
> would have made it complain.

The index check now prints the intermediate count — 7 indexes, then 2, then 7 —
so the drop is **proven to have happened** before the comparison is trusted.

---

## 6. State

**HEAD `6b45c09`, pushed. 96/96 under this repository's own `.venv`.**

**On the cluster:** `stockgrader_scratch` holds 0001–0004, 3,368,813 facts, 195
quarantined, 7,714 filings, 6,179 filers, one coverage row. **`stockgrader` is
untouched. No cluster destroyed. Both compromised roles still live** — OPEN-27
steps 4 and 5 are deliberately not started.

**Register:** 103 findings, 37 open, 30 closed. New: **F-029** through **F-033**,
**OPEN-64** (4.9% of rows carry no value — needs a ruling), **OPEN-65** (the write
path cost).

---

## 7. Next

1. **Measure `--defer-indexes` on one quarter** — it decides OPEN-65 and costs
   one load.
2. **OPEN-64** — the 178,555 valueless rows include `NetIncomeLoss` and
   `StockholdersEquity`, both core GQS inputs. **Needs a ruling, not a default.**
3. **The first DB-backed endpoint.** There is now real data behind it. This
   closes D-029's application half and moves recovery row 4 off `Never`.
4. **Then the 45-quarter load**, once 1 and 2 are settled.

**Still blocked, and not by infrastructure:** scoring, on §11.1 and §5.4. **P-13
remains the finding that matters** — deferred to "its own session" on day one, no
session ever scheduled. The store now has real facts in it and **still nothing
reads them.**
