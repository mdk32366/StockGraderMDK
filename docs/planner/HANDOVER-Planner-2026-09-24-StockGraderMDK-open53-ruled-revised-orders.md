# HANDOVER — Planner → Code — StockGraderMDK: OPEN-53 ruled, revised fact-slice orders

**From:** Planner · **Issued:** 2026-09-24, first issue
**Records:** an owner ruling on OPEN-53, received 2026-09-24
**Amends:** §5 of `HANDOVER-Planner-2026-09-24-...-fact-slice.md` and §4 of
`RULING-Planner-2026-09-24-...-open54-open55-open53-framed.md`

---

## 1. OPEN-53 — RULED: narrow by concept, defer the tier question

**The store is narrowed by concept. The disk and plan tier are not increased
now.**

**The costs, established from Fly's published pricing 2026-09-24**, so the ruling
rests on figures rather than impressions:

| | Storage | Plan | Monthly |
|---|---|---|---|
| Today, 15 GB Basic | $4.20 | $38 | **$42** |
| 100 GB Basic | $28 | $38 | **$66** |
| 150 GB Basic | $42 | $38 | **$80** |
| 150 GB Launch | $42 | $282 | **$324** |

Storage is **$0.28 per provisioned GB per 30-day month** — *provisioned*, not
used — capped at 1 TB, with up to 500 GB at creation.

**The storage line was never the decision.** $24 a month to go from 15 GB to
100 GB is noise. **The decision is RAM.** Basic is Shared-2x with **1 GB**. At
100 GB, `fact_one_per_filing` alone would be roughly 42 GB of index against 1 GB
of memory, and the initial load has to *build* that index. Index construction at
that ratio spills to disk and may simply thrash.

**Whether it matters is unmeasured**, and the workload is favourable — batch
loads plus low-QPS scoring queries from one calling application, not OLTP. But
**buying Launch now is paying $324 a month against a requirement nobody has
measured**, and if the concept cut lands the store near 10–15 GB the question
disappears rather than being answered expensively.

**Reversibility is what makes this safe**, as before: FSDS archives are immutable
and re-readable, so a narrowed store can be widened later from files that have
not changed.

---

## 2. The finding that pays for all of this — clusters are billed per cluster

**Each MPG cluster carries its own plan fee.** The plan determines CPU and memory
*for a cluster*, so four clusters means four plan fees.

`fly mpg list` showed **four ready clusters in the organisation**:

| Cluster | Status |
|---|---|
| `stockgrader-db-r1` | live, ours |
| `stockgrader-db` | **retained, holding nothing** |
| `kyzl60xz9zyrpj9g` | PharmFoldMDK restore orphan |
| `zp2wjrej9lwodn4q` | PharmFoldMDK restore orphan |

**Ruling 6 says the old cluster "holds nothing and costs little." The second half
is wrong.** At Basic with 10 GB provisioned it is approximately **$41 a month**,
and the two orphans are approximately **$38 each plus their storage.**

**That is on the order of $120 a month of idle spend — more than the entire cost
of the storage decision we have spent two deliveries analysing.**

Record as `F-next/cluster-plan-fee-is-per-cluster`, and **amend ruling 6's
rationale**: the old cluster's destroy is not only credential hygiene, it is the
largest single saving available. It still waits on the ticker load and a
DB-backed endpoint — the ordering was right for other reasons — but it should
stop being described as costing little.

**And B-9's destroy condition is now financial as well as procedural.** At 15 GB
an orphaned probe cluster is a rounding error, which is precisely why the two
next door survived unnoticed. At any size, the plan fee alone makes it $38 a
month indefinitely.

---

## 3. The narrowing — tier 1, and it needs no scoring decisions

**Tier 1: everything under the standard taxonomy; filer extension tags
excluded.**

This requires no concept list, no normalization mapping, and no TDD rulings. It
is a superset of anything GQS will want, and it avoids the dependency that makes
a tighter cut impossible today — **you cannot filter to a concept set you have
not defined.**

**Extensions are excluded, not dropped silently.** Count them, record the count
per quarter, and report it. OPEN-48 asks how extensions are distinguishable in
the first place; that answer governs this.

**If tier 1 does not fit, report and stop.** Do not choose the next lever. The
options, for the owner to rule on a real figure:

1. An explicit concept allowlist from the TDD's §4 blocks — **requires
   normalization work that does not exist yet.**
2. Fewer quarters, on top of tier 1.
3. Increase disk, and then the RAM question in §1 becomes live.
4. **Not** narrowing dimensions — unchanged, and §4 of the previous ruling
   showed it would not have worked anyway.

---

## 4. The measurement — and one quarter is not a sample

**4.1 — Measure the standard-versus-extension split on TWO widely separated
quarters**, not one. 2015q2 and 2026q2.

**§3 of your last report is the reason.** Measuring 2026q2 and multiplying by a
count was wrong by 56% because quarters are not interchangeable. **The extension
share is at least as likely to vary across eleven years as the row count was** —
taxonomies mature, filers extend less, and the early quarters plausibly carry a
*higher* extension share than the recent ones. A cut sized on 2026q2 alone would
be the same error in a new variable.

**4.2 — Re-estimate by archive bytes, not by quarter count.** The 70.22 ratio you
established replaces ×45. Apply the tier-1 retained fraction to it.

**4.3 — Report:**
- rows by `version`/`tag`; standard versus extension counts and percentages, for
  both quarters
- the cumulative share of the top N tags, which tells us how much headroom a
  tighter cut would have if tier 1 falls short
- the tier-1 retained fraction, and the re-estimated total against 15 GB
- whether the split is stable across the two quarters, stated either way

---

## 5. Order of work

1. **OPEN-48, 49, 50** — `version` and extension tags, `segments` truncation,
   `adsh` formatting. OPEN-48 gates §3's exclusion rule. Plus **OPEN-44's**
   fetch-twice test, per source.
2. **The §4 measurement.** Report and stop if tier 1 does not fit.
3. **0003** — provenance on `fact`, A5's enumeration inverted to an exclusion
   list with reasons, and OPEN-55's quarantine table. **Independent of 1 and 2**
   and needed under every option.
4. The fact loader, once the measurement lands.

Run phase gated as before: OPEN-25, OPEN-27, OPEN-30, OPEN-21, OPEN-33, plus
slice 1's own run.
