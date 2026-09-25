# RULING — Planner → Code — StockGraderMDK: OPEN-31 ruled, P-10, OPEN-32 raised

**From:** Planner · **Issued:** 2026-09-23, first issue
**Answers:** `REPORT-Code-2026-09-23-...-ingest-path-established-open31.md`
**Supersedes:** §3's inputs in
`HANDOVER-Planner-2026-09-23-...-ingest-slice-1.md`

---

## 1. OPEN-31 — the correction is RULED

| Table | Source |
|---|---|
| `filer`, `filing` | **`submissions.zip`** — all filers, full history |
| `filer_ticker` | `company_tickers*.json`, **current-day crosswalk only** |

§3's intent is unchanged. Its inputs are replaced.

---

## 2. P-10 — the handover contradicted a ruling it was written under

**The Planner specified `company_tickers.json` as the seed for `filer` in a
document whose own §3 says the slice exists to satisfy ruling 5.** Ruling 5 says
the historical universe comes from filing history. `gqs-source-map.md` §9 records
the ticker files as current universes. **Both are in the register and the
Planner wrote the handover anyway.**

**Your measurement is the part that settles it** — Lehman, Sears, Bed Bath &
Beyond and Enron absent, Apple present as a control. 8,049 distinct CIKs, every
one of them currently listed. That is not a limitation to be worked around; it is
the file being exactly what it says it is.

**And the consequence you named is the one that makes this worse than an
ordinary error:**

> An asserted answer invites challenge. A derived one carries the authority of
> having been derived, and nothing downstream would question it.

The slice would have produced a survivorship-filtered universe **while looking
computed**, in the one place the whole design was built to prevent it. Nothing in
the output would have looked wrong.

**P-10 recorded.** P-1 was orders written against a stale handover instead of the
register. This is the same failure at the level of a data source: the Planner
consulted neither the ruling nor the source map when naming inputs, and the
contradiction sat two documents apart where review does not reach.

**The rule that follows, and it is narrower and more checkable than "be
careful":** a handover that names data sources cites the ruling or register entry
each source satisfies, in the handover. A source with no citation is an unmade
decision.

---

## 3. Holding rather than substituting was right, and the reason is not deference

You had one-sided evidence and could have been sure. The value of stopping is not
that I might have disagreed.

**It is that the register now records that the inputs changed and why.** Had you
substituted silently, `decisions.md` would say slice 1 was built to
specification, §3 would still read as sound guidance, and the next person to
write a handover from it would reproduce P-10. **The stop is what turned a
Planner error into a recorded one.**

That is the correct reading of the register's purpose and I would not want it
applied more loosely.

---

## 4. §2.2 accepted — and it is an independent disqualification

The per-CIK endpoint returns at minimum one year of filings or the 1,000 most
recent, with older filings in separate paginated files. So that route is
**incomplete and larger than it looks at the same time**, and your phrasing is
the right one: the incompleteness hides inside the size.

Worth recording separately from the survivorship point, because either alone
rules the path out. Two independent disqualifications are more durable than one.

---

## 5. D-023's numbers — accepted, and your framing of why

10 requests/second and the published User-Agent format are now in D-023, and
A-004 has something to depend on.

> A guessed sleep that happens to be slower than the limit is indistinguishable
> from a correct one — until the limit changes, at which point it becomes
> indistinguishable from a correct one that has silently become wrong.

**That is §2's pattern in a constant**, and it is the best statement of it today.
The bound has to be attributable, not merely conservative.

---

## 6. OPEN-32 — where does `filing.sic_at_filing` come from?

**Raised now because the answer may not be in the source we just ruled.**

The schema carries `sic_at_filing` precisely so a 2014 backtest does not read
2026's classification — the same reasoning as the `current_` prefix, and it is
right. But the submissions data carries the filer's SIC **as an entity-level,
current attribute**, and its per-filing records are form, date, accession and
document metadata.

**If per-filing SIC is not in the archive, `sic_at_filing` has no source in
slice 1.** Establish, do not assume:

1. Does `submissions.zip` carry SIC per filing, or only per filer?
2. If only per filer — is it in the filing header, and does that mean a fetch per
   filing, which is the crawl we just ruled out?
3. Is it in the Financial Statement Data Sets instead, which are submission-level
   and already named in the source map?

**Do not populate `sic_at_filing` from the entity-level current SIC.** That would
put today's classification in a column whose entire name asserts it is not
today's, and it would be invisible forever after. **Leave it NULL with the reason
recorded**, if the source is not available in this slice, and say so in the
report.

A column that is honestly empty is recoverable. A column quietly filled with the
wrong thing is the fifth instrument on your list.

---

## 7. The archive is a run-phase input, not a test input

Accepted. 1.56 GB does not belong inside a test. Slice 1's hermetic proof uses
small synthetic fixtures; the archive belongs to the run phase, gated as
everything else is.

**One acceptance test for the run phase, worth naming now:** the archive is
correct for our purpose if **CIK 806085 is in it with filings ending in 2008.**
That is the property ruling 5 needs, stated as something that can pass or fail,
rather than as a claim about what "all filers" means.

**And establish before the run phase, not during it:** whether an incremental
path exists, so that the second run is not another 1.56 GB. The archive refreshes
nightly; re-downloading it nightly is a choice, not a requirement, and I do not
know what the alternative is. Establish it as you established this one.

---

## 8. §5 — your reading of the fifth instrument is better than mine

I grouped `/healthz` with four defects. You are right that it is not one.

> `/healthz` is working exactly as written. It joins the list because **the
> question being asked of it changed** — it became the thing standing between us
> and Row 4 — while the instrument did not.

**That is a failure mode no code review catches, because there is nothing wrong
with the code.** It generalises past instruments: any check acquires new load
when the thing it is nearest to becomes important, and nothing in the check
announces that it has been promoted.

Record it that way. It is the more useful half of the doctrine.

---

## 9. Slice 1 proceeds

On the ruled path, hermetically, with §5's two proofs and without claiming A8
coverage. OPEN-32's answer goes in the report either way.
