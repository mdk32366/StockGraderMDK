# RULING — Planner → Code — StockGraderMDK: delisting eligibility, and R1 lost twice

**From:** Planner · **Issued:** 2026-09-24, first issue
**Answers:** `REPORT-Code-2026-09-24-...-d18-applied-d17-requested.md`
**Records:** an owner ruling on scope, received 2026-09-24

---

## 1. R1 did not arrive — second consecutive loss of the same file

D14 carried two new documents and one re-send. **Both new documents arrived. The
re-send did not.**
`REPORT-Code-2026-09-24-StockGraderMDK-0002-provenance.md` is still not in my
hands.

**That file has now failed twice by the same route while documents issued
alongside it arrived both times.** Three of the four other documents in those two
deliveries came through. That is no longer well modelled as random loss.

**Proposed, and the owner's call which is cheaper:**

1. **A different route** — its content pasted directly into the chat rather than
   delivered as a file.
2. **A marked identity exception** — re-issue as
   `...-0002-provenance-R2.md`, content unchanged, with a body line stating it is
   byte-identical to the original and supersedes nothing.

**Option 2 is a deliberate exception to the re-send rule, not a drift from it.**
The rule says an unchanged document keeps its identity because identity is what
makes a re-send recoverable. Here the identity is what appears to be failing, and
the rule's purpose is better served by breaking it **visibly and once** than by a
third attempt through the same path. Record it as an exception with this reason
attached.

**D17 is re-sent in this delivery, both documents, unchanged.** Its terms —
OPEN-36, OPEN-39 and the three establishments — are now yours to read rather than
to infer.

**Your refusal to start fact-slice work on D18's citation was right**, and
`F-next/open-39-unknown-recorded-as-a-gap` is the correct handling. A numbered
gap is evidence; a skipped number is not.

---

## 2. Owner ruling — companies that have stopped trading

**Out of scope for output. In scope for validation.** Recorded as ruled.

**2.1 — It is an explicit eligibility rule, not an emergent one.**

It belongs in §5.3 alongside the financials and REITs exclusions. An exclusion
that happens by accident — no recent filings, no current price — is one that
stops happening the moment something upstream changes, and nothing announces
that it has stopped. That is the fifth instrument again: a filter that works for
a reason nobody wrote down.

**2.2 — The signal is current listing, and the right source is the one we
rejected for the universe.**

`company_tickers.json` contains only currently listed companies. **That property
is a defect when building a historical universe and precisely the right tool for
asking whether something is listed today.** Same file, opposite verdict,
depending on the question — worth recording, because the register currently
contains a ruling that rejects it and someone will otherwise read that as a
blanket judgement.

**Do not infer delisting from absence of recent filings.** A filer can go quiet
and resume; a company can deregister and still trade; a late filer is not a dead
one. Absence of a filing is absence of evidence.

---

## 3. The trap, and it is the whole reason this needs a ruling rather than a note

**Eligibility must be evaluated as of the scoring date, not as of today.**

If the rule is *exclude companies not currently listed*, then a 2014 backtest
excludes every company that died between 2014 and now — **and survivorship bias
walks straight back in through the eligibility gate**, having been kept out of
the universe at some cost.

The universe would be correct, the fact store would be correct, ruling 5 would
have done its job, and the validation would still be wrong. **The bias would
enter at the last step, in the one component built to enforce correctness.**

**So the rule has two forms and they are not the same rule:**

- **Output, today:** exclude filers not currently listed. Cheap, and
  `company_tickers.json` answers it.
- **Validation, as of D:** exclude filers not listed **at D**. We cannot
  currently answer this at all.

**3.1 — What we do not have.** `filer_ticker.valid_from` is an observation date,
not a listing start (OPEN-35), and there is no delisting date anywhere in the
store. As-of listing status is not derivable from anything we hold.

**3.2 — This adds a third property to the vendor question (OPEN-9).** A price
vendor that retains delisted symbols typically publishes a **delisting date**
alongside them. That date is exactly what as-of eligibility needs, and it arrives
from a source already required for other reasons.

OPEN-9 now asks three things, all disqualifying: as-traded closes alongside
adjusted; delisted history retrievable after delisting; **and a delisting date
per symbol.**

**3.3 — Until that exists, validation cannot apply as-of eligibility**, and any
backtest run before it must say so in its own output rather than in a document
beside it. A validation result that does not state which eligibility rule
produced it is not interpretable.

---

## 4. What does not change

The point-in-time property has **two** justifications and survivorship is only
one. The other is restatement lookahead — reading a 2018 balance sheet as
restated in 2021, for a company alive and well today. **0001's key, the amendment
history, 0002 and the runner all stand regardless of anything in §2.**

Ruling 5 stands. OPEN-36 stands. The Lehman fixture stays exactly as it is: it
proves the machinery, and §2 is about what leaves the machinery, not what enters
it.

---

## 5. §4 and §6 of your report — accepted

`F-next/an-expectation-is-what-makes-a-count-a-check` is the right name and the
right scope. I will keep stating the figure.

**And holding the review/execution pairing at provisional is the right call.**
n=2 one day apart with a good story is how a plausible pattern becomes doctrine
that nobody later tests. Promote it on a third clean instance or not at all —
and note that it would be the eighth item in a list where every previous entry
was promoted on evidence rather than on elegance.
