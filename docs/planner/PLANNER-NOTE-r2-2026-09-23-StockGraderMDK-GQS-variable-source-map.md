# PLANNER NOTE r2 — StockGraderMDK: GQS v3 read, variable-to-source map

**From:** Planner · **Issued:** 2026-09-23, second issue
**Supersedes:** `PLANNER-NOTE-2026-09-23-StockGraderMDK-GQS-variable-source-map.md`
(first issue, never delivered — `F-next/relay-loss-recurrence`).
**What changed from the first issue:** §7 only. Four items it listed as
"ratifiable now" were ruled in `RULING-RECORD-...-owner-rulings` (07:32) and are
recorded here as ruled. §§1–6 are unchanged; this document is complete in
itself and the first issue can be discarded rather than reconciled.

**Closes:** A-016. The Planner has read `TDD-growth-score.md` and
`growth-model-lineage.md` in full, not a summary of them.

---

## 1. Four findings before the sourcing work

**F-A — D-010's condition cites the wrong section and the wrong count.**
The ruling says GQS v3 has "five open questions in its §17." The TDD's own
header says **four** open questions in **§11**, and §11 contains exactly four:
R&D capitalization (11.1), sector granularity (11.2), WACC estimation (11.3),
size tilt (11.4). A completeness gate that points at a section which does not
exist cannot be checked by anyone but its author. *(Ruled — reworded, ruling 7.)*

**F-B — the TDD was written against a different codebase.**
§12's confirm-before-build list asks the Builder to check the current migration
head via `alembic heads`, to read "the existing `finance` agent's tools, module
paths and `description`," to find the settings overlay pattern, and to confirm
`place_stock_order` remains gated. None of that exists in StockGraderMDK, and
D-021 ruled forward-only numbered SQL migrations, rejecting Alembic outright.

Not a defect in the TDD — it was written 2026-09-09 for the JARVIS-side finance
agent. It is a defect in treating it as build-ready here. *(Ruled — v4 grounded
on this repo, ruling 8.)*

**F-C — the TDD's own data claim is contradicted by its own valuation block.**
§2 goal 1 says the score is "computed per ticker from SEC filings only," and
§5.1 names EDGAR as the sole source. But §4.4 ranks on free cash flow yield,
EV/Sales, EV/EBITDA, EV/gross profit and EBIT/EV — every one of which needs
**enterprise value**, which needs **market capitalization**, which needs a
**share price**. EDGAR has shares outstanding. It does not have prices.

25% of the score cannot be computed from filings. *(Ruled — SEC is one source
among several, ruling 4.)*

**F-D — Altman's Z-Score needs market data too.** The original public-firm Z
uses market value of equity over total liabilities in its fourth term; the
private-firm Z′ substitutes book value of equity. *(Ruled — Z′, ruling 11.)*

---

## 2. Scope note

§13 of the TDD is a **completeness gate**: it refuses the document for build
while any §11 question is unratified, while §5.4's R&D treatment is unresolved,
while the eligibility table has an unlisted class, or while any block holds a
placeholder metric.

§11.1 and §5.4 — the same question — remain open by ruling 12. **No scoring
build order can issue.** Ingest proceeds: the universe, the fact store and the
point-in-time property are §10 step 1 and are the same work whichever way §11.1
lands.

---

## 3. Variable-to-source map

**Legend:** **E** = SEC EDGAR (XBRL company facts / Financial Statement Data
Sets / submissions metadata), **P** = price vendor, **F** = fund filings
(N-PORT / N-CEN / prospectus), **?** = unresolved, named in §5.

### 3.1 Growth durability (§4.1, 30%)

| Variable | Source | Notes |
|---|---|---|
| Revenue CAGR 3yr / 5yr | E | Revenue tagging is the worst normalization case in the TDD — the concept moved with ASC 606 and filers use several tags. Priority list required. |
| CV of revenue growth | E | Derived from the same series. The block's most important metric per §4.1. |
| Gross profit growth | E | `GrossProfit` where tagged, else revenue minus cost of revenue. Both paths needed. |
| CV of earnings growth | E | `NetIncomeLoss`. |
| Organic vs acquired proxy | E | Goodwill additions plus cash paid for acquisitions from the cash flow statement. |

### 3.2 Profitability quality (§4.2, 30%)

| Variable | Source | Notes |
|---|---|---|
| Gross profitability (GP ÷ assets) | E | Primary metric. Cleanest sourcing in the whole model. |
| ROIC | E | NOPAT and invested capital both derivable. |
| WACC | flat rate | Ruling 9. Not sourced. Condition: the spread is never surfaced as an absolute figure. |
| Cash conversion (OCF ÷ NI) | E | |
| Gross margin trend | E | |

### 3.3 Integrity gate (§4.3)

| Variable | Source | Notes |
|---|---|---|
| Accruals ratio (Sloan) | E | Balance-sheet and cash-flow formulations differ; the definition is unverified in lineage §11. |
| Beneish M-Score | E | All eight ratios are statement-derived. |
| Altman Z′ | E | Ruling 11. Book value of equity; no price dependency in the gate. |
| Auditor change | E | Auditor name and firm ID are tagged on the 10-K cover page in recent years. A change is a year-over-year comparison. Earlier years need a different path. |
| Restatement | E, with care | Non-reliance disclosure is an 8-K item; recent 10-K cover pages also carry error-correction flags. Confirm coverage for the window you need before relying on either. |
| Share count growth | E | |

### 3.4 Valuation (§4.4, 25%)

| Variable | Source | Notes |
|---|---|---|
| Enterprise value | E + P | Net debt from filings; market cap needs price × shares. |
| FCF yield (FCF ÷ EV) | E + P | FCF itself is EDGAR: OCF minus capex. |
| EV/Sales, EV/EBITDA, EV/gross profit | E + P | |
| Earnings yield (EBIT ÷ EV) | E + P | |
| Sector-relative ranking basis | E + ? | Ruling 13 replaced SIC with Lynch archetypes. The classifier is unbuilt — see §5. |

### 3.5 Reinvestment runway (§4.5, 15%)

| Variable | Source | Notes |
|---|---|---|
| Reinvestment rate | E | Capex, R&D and acquisitions over NOPAT. |
| Incremental ROIC | E | |
| Net debt/EBITDA, interest coverage | E | |
| Capital allocation record | E + P | Buyback dollars are in the cash flow statement; "executed at low valuations" requires the valuation *at the time of the buyback* — a historical price. |

### 3.6 Eligibility and universe (§5.3)

| Variable | Source | Notes |
|---|---|---|
| ≥3yr filing history | E | |
| Financials / REITs exclusion | E | SIC ranges from submissions metadata. SIC survives here even though ruling 13 replaced it for valuation ranking — exclusion and ranking are different jobs. |
| Pre-revenue detection | E | |
| Market cap floor | E + P | |
| Liquidity / volume floor | P | Volume is not in any filing. |

---

## 4. The price dependency, stated once

Three parts of the model need a share price: the valuation block, the
capital-allocation metric, and the market-cap and liquidity floors. Ruling 11
removed the fourth. This is not avoidable by better EDGAR work — shares
outstanding is filed, price is not.

Two properties the price source must have, and they are not the usual ones:

**Unadjusted closes, not just adjusted ones.** Back-adjusted series restate
history for splits and dividends. Multiplying a back-adjusted price by shares
outstanding gives a market cap nobody ever observed. This is the identical
failure to the restated-financials lookahead the TDD rejects in §5.1 — same
shape, different dataset, and it will pass every test that does not check it.
Store the as-traded close and the adjustment factors separately.

**Delisted coverage.** §5.1's point-in-time property exists so a backtest reads
what was knowable. A vendor that drops delisted names hands back survivorship
bias through the door ruling 5 closed. The question has to be asked in the form
the Builder gave it in testplan OPEN-9: whether a delisted ticker's history
stays retrievable *after* delisting — not whether the vendor claims "full
history."

---

## 5. Fund side (D-027 / D-028) — sourcing, with one real gap

**Holdings:** SEC N-PORT data sets, free and flattened from the NPORT-P XML.
The public portion covers the third month of each fiscal quarter only; the first
two months stay confidential. D-027's quarter-lag is statutory, and no amount of
money removes it.

**Holdings carry CUSIP/ISIN/LEI, not tickers.** The crosswalk to scored equities
is a build item and is where `UNRESOLVED_IDENTIFIER` comes from. CUSIP is
licensed, which is worth a look given D-020 keeps the repo public.

**Non-equity weight (D-028's floor):** N-PORT's per-position asset category
supports this directly. Best-sourced part of the fund design.

**The gap: expense ratio and turnover.** D-027 states cost is the strongest
single predictor of long-run fund outcomes — and it is the one variable with no
established free source. Not in N-PORT. It lives in the prospectus fee table and
the annual report's financial highlights, and N-CEN may carry some of it.
**Unverified, and not asserted.** Named as a research item.

---

## 6. Universe construction — the survivorship answer

`company_tickers.json` and `company_tickers_mf.json` are **current** universes.
Delisted stocks and dead funds are not in them.

Derive the historical universe from **filing history**, not the ticker files. A
CIK that filed 10-Ks from 2011 to 2017 and stopped is in EDGAR permanently.
Building the universe from the fact store's own filing record gives a
point-in-time universe by construction. The ticker files then serve only as the
current-day identifier crosswalk. *(Ruled — ruling 5. Constrains the first
migration.)*

---

## 7. Status of everything in this note — REVISED FROM FIRST ISSUE

**Ruled since the first issue was written:**
- §11.3 WACC — flat rate, with the never-as-an-absolute condition (ruling 9)
- §11.4 size tilt — available, default off (ruling 10)
- F-D Altman — Z′ (ruling 11)
- F-A — D-010's condition reworded to four questions in §11 (ruling 7)
- F-B — GQS v4 grounded on this repo (ruling 8)
- F-C — SEC is one source among several (ruling 4)
- §11.2 — Lynch archetypes, option (c), with the SIC fallback trigger (ruling 13)

**Still open:**
- **§11.1 / §5.4 R&D capitalization.** Deferred to its own session with a
  prework document (ruling 12). Gates §13 twice.
- **The archetype classifier.** Ruling 13 created work this note did not
  anticipate: the five Lynch archetypes are not derivable from SIC, so the
  classifier needs its own definition, its own `insufficient_data` path, and a
  place in the output. It must be specified and frozen before scoring runs.
- **Price vendor selection.** testplan OPEN-9.
- **Expense ratio and turnover sourcing.** §5 above.
- **Lineage §11 citation queue.** Ten items written from memory without web
  access; TDD §12 requires them verified before any reach a user-facing surface.
  Two are load-bearing for this map: the exact Novy-Marx gross-profitability
  definition, and Sloan's accruals formulation. Until verified, §3.2 and §3.3
  rest on the Planner's recollection — which is the same class of claim the
  register exists to stop.
