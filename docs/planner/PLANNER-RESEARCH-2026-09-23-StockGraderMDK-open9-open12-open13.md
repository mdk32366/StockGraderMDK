# PLANNER RESEARCH — StockGraderMDK: OPEN-9, OPEN-12, OPEN-13

**From:** Planner · **Issued:** 2026-09-23, first issue
**Method:** web research, 2026-09-23. Primary and near-primary sources where
available. Where a question is not settled below, it is marked unsettled rather
than answered.

---

## 1. OPEN-13 — the two load-bearing citations. VERIFIED.

### 1.1 Novy-Marx gross profitability — lineage §7 is correct

Robert Novy-Marx, *The Other Side of Value: The Gross Profitability Premium*,
**Journal of Financial Economics 108(1), 1–28, 2013.** The lineage's year and
title are right. An earlier NBER working paper (w15940, 2010) carries the
subtitle *Good Growth and the Gross Profitability Premium*, which is where the
alternative title in circulation comes from.

**Definition confirmed as the TDD has it:** gross profits divided by **book value
of total assets**, where gross profit is revenue minus cost of goods sold. The
paper's own shorthand is GP/A.

**One implementation detail the TDD does not state:** the denominator is total
assets, not book equity. Several later papers use book equity and get a
different factor. `§4.2` must specify total assets explicitly or the
normalization layer will eventually be built against the wrong one.

**No change to the design.** §4.2 stands as written.

### 1.2 Sloan accruals — lineage §5 is correct, and the formulation matters

Richard G. Sloan, *Do stock prices fully reflect information in accruals and cash
flows about future earnings?*, **The Accounting Review 71(3), 289–315, 1996.**

**The original is the balance-sheet formulation:**

```
ACC = (ΔCA − ΔCash) − (ΔCL − ΔSTD − ΔTP) − DEP
```

scaled by **average** total assets — the mean of current and prior-year total
assets, not ending assets.

Where ΔCA is the change in current assets, ΔCash the change in cash and
equivalents, ΔCL the change in current liabilities, ΔSTD the change in debt
included in current liabilities, ΔTP the change in income taxes payable, and DEP
depreciation and amortization expense.

**This resolves the ambiguity the note flagged**, and the answer has a
consequence the note did not anticipate.

### 1.3 F-E — the accruals gate has a formulation problem that lands on §4.1

Two methods are in general use: Sloan's balance-sheet differencing, and the
cash-flow method (earnings minus operating cash flow, both taken from the cash
flow statement). **They disagree, and they disagree most for companies with
acquisitions, divestitures or discontinued operations** — because a balance-sheet
difference reads an acquired subsidiary's working capital as if the company had
generated it.

**Those are exactly the companies §4.1's organic-versus-acquired proxy exists to
catch.** A roll-up would get a distorted accruals ratio from the gate and a
goodwill discount from the growth block, and the two would be measuring the same
underlying fact with one of them doing it wrongly.

**Recommendation:** use the **cash-flow formulation** for the integrity gate, and
record that this is a deliberate departure from Sloan's original rather than an
implementation shortcut. The balance-sheet version is the historical definition;
the cash-flow version is the one that survives contact with acquisitive
companies, which this universe is full of.

**Owner ruling required.** This is a change to §4.3's stated basis.

### 1.4 F-F — the anomaly has reportedly decayed, and the gate should not rest on it

Published work reports the accruals anomaly generated excess returns for roughly
four decades but weakened after 2002, with one line of argument attributing the
decline to the spread of analyst cash-flow forecasts.

**This does not break §4.3 and it does change its justification.** The lineage
calls Sloan the most operationally important result in the literature, which is a
claim about *return prediction*. If the return premium has decayed, that claim is
weaker than stated.

**The gate survives on a different and better argument:** accruals-driven
earnings reverse, and a buy-and-hold model has no business rating a company
highly on earnings that are about to reverse — whether or not the market still
pays for the distinction. That is an accounting-quality argument, not a factor
argument, and it is the one §4.3 should be written on.

Lineage §5 and §9's third axiom need that distinction added.

---

## 2. OPEN-12 — expense ratio and turnover. ANSWERED, and N-CEN is the wrong form.

**N-CEN does not carry them.** The SEC does publish Form N-CEN Data Sets — free,
flat files extracted from the XML submissions, updated quarterly — but N-CEN is a
census of fund *operations*: service providers, auditors, custodians, board and
compliance structure, ETF authorized-participant data, fund-action flags. Not
fees, not turnover.

**Where they actually live:**

- **Financial Highlights**, in the prospectus (485BPOS) and the shareholder
  report (N-CSR): ratio of operating expenses to average net assets, and
  portfolio turnover rate, as a multi-year table. This is the historical series
  and it is **HTML/prose, not structured data.**
- **Inline XBRL tagging of shareholder reports**, required under the SEC's
  Tailored Shareholder Reports rule, which added Item 27A to Form N-1A and
  requires funds to tag the report contents in Inline XBRL. **This is the
  structured path, and it is recent.**

**The shape of the answer, which is what matters for D-027:**

**Recent years are cheap. History is expensive.** A current expense ratio is
obtainable from tagged data. A ten-year series — which is what a cost-versus-
outcome validation needs — means parsing Financial Highlights tables out of
prospectuses and shareholder reports, per share class, across filers with no
common layout.

**Consequence for D-027's pre-registration.** The honest null was stated as
*does look-through quality add anything over expense ratio and turnover alone?*
That test needs a historical cost series, which is the expensive half. The
look-through half is comparatively cheap because N-PORT is structured.

**So the cheap work and the validating work are not the same work**, and building
the cheap half first would produce a fund score whose central question stays
untested indefinitely. That is a sequencing decision for the owner, not a
Planner call.

**Unconfirmed and stated as such:** the Tailored Shareholder Reports compliance
date, and therefore exactly how many years of tagged data exist. Confirm before
scoping the parser.

---

## 3. OPEN-9 — vendor properties. Half answered.

### 3.1 EODHD — delisted coverage is documented and specific

EODHD retains delisted tickers: the exchange symbol list endpoint takes a
`delisted=1` flag, and the standard end-of-day, fundamentals, dividends and
splits endpoints then work on those tickers as they do on active ones. Their
published figure is about 60,000 delisted symbols on US exchanges as of
September 2026.

**The limitation, and why it does not bite us.** Data availability is tiered by
delisting date: after 2018, end-of-day plus fundamentals, dividends and splits;
after 2021, intraday as well; **before 2018, end-of-day only.**

**We only need prices from the vendor.** Fundamentals come from EDGAR under
ruling 4 and the point-in-time requirement, and EDGAR keeps a dead company's
filings permanently. So EODHD's pre-2018 fundamentals gap falls on data we were
never going to source there. **The architecture makes the vendor's main
limitation irrelevant** — which is worth recording, because it is an argument for
the architecture and not only for the vendor.

### 3.2 The ticker-reuse trap reinforces ruling 5

EODHD's own documentation warns that a remembered ticker may now belong to a
different company, and that symbols get reassigned.

**This is ruling 5 arriving from the vendor side.** A universe keyed on ticker is
wrong in both directions — it misses dead companies and it silently merges two
different ones. The fact store must key on CIK and carry ticker as a
time-bounded attribute, not an identity. If that is not already explicit in the
first migration's design, make it explicit.

### 3.3 Still unanswered — and these are the questions to put directly

1. **Does EODHD serve as-traded closes alongside adjusted closes?** The
   unadjusted-price requirement is not addressed in what I found, and it is the
   disqualifying property, not a preference. A back-adjusted close times shares
   outstanding is a market cap nobody observed.
2. **Tiingo's delisted position is unestablished.** I found no vendor
   documentation either way, only forum commentary, which is anecdote and is
   recorded as such rather than as evidence. Ask directly.

**Preliminary read, not a recommendation:** EODHD has answered the harder of the
two questions in writing, with figures and an endpoint. Tiingo has not answered
it to me at all. That is a difference in what is *established*, not necessarily in
what is *true*, and the second question above decides it either way.

---

## 4. What this changes

**Needs an owner ruling:** §1.3, the accruals formulation. Cash-flow rather than
balance-sheet, as a recorded departure.

**Needs a lineage edit:** §1.4, separating the accounting-quality argument from
the return-prediction claim in §5 and §9.

**Needs a sequencing decision:** §2, whether the fund score is built on cheap
current-cost data with its central validation deferred, or waits on the
historical parser.

**Needs two direct questions to vendors:** §3.3.

**Closes:** OPEN-13's two load-bearing items. The remaining eight in lineage §11
are unverified and are not load-bearing for the source map.
