# GQS variable-to-source map — where every number comes from

*StockGraderMDK · recorded 2026-09-23 from
`PLANNER-NOTE-r2-2026-09-23-StockGraderMDK-GQS-variable-source-map.md`*

This is the Planner's map after reading `TDD-growth-score.md` and
`growth-model-lineage.md` **in full** (closing A-016). It is the answer to
"where does each variable come from," recorded before ingest is built, because
the answer constrains the schema.

**Legend:** **E** = SEC EDGAR (XBRL company facts / Financial Statement Data
Sets / submissions metadata) · **P** = price vendor (unchosen, testplan OPEN-9)
· **F** = fund filings (N-PORT / N-CEN / prospectus) · **?** = unresolved.

---

## 1. Growth durability (§4.1, 30%)

| Variable | Source | Notes |
|---|---|---|
| Revenue CAGR 3yr / 5yr | E | **The worst normalization case in the TDD.** The concept moved with ASC 606 and filers use several tags. A priority list is required, not a single tag. |
| CV of revenue growth | E | Same series. The block's most important metric per §4.1. |
| Gross profit growth | E | `GrossProfit` where tagged, **else** revenue minus cost of revenue. Both paths needed. |
| CV of earnings growth | E | `NetIncomeLoss`. |
| Organic vs acquired proxy | E | Goodwill additions + cash paid for acquisitions, from the cash flow statement. |

## 2. Profitability quality (§4.2, 30%)

| Variable | Source | Notes |
|---|---|---|
| Gross profitability (GP ÷ assets) | E | Primary metric. **Cleanest sourcing in the whole model.** |
| ROIC | E | NOPAT and invested capital both derivable. |
| WACC | **flat rate** | Ruling 9 — not sourced. **Condition: the ROIC-WACC spread is never surfaced as an absolute figure.** |
| Cash conversion (OCF ÷ NI) | E | |
| Gross margin trend | E | |

## 3. Integrity gate (§4.3)

| Variable | Source | Notes |
|---|---|---|
| Accruals ratio (Sloan) | E | Balance-sheet and cash-flow formulations **differ**; the definition is unverified in lineage §11. See OPEN-13. |
| Beneish M-Score | E | All eight ratios are statement-derived. |
| Altman **Z'** | E | Ruling 11. Book value of equity - **no price dependency in the gate**, which is the point of choosing Z'. |
| Auditor change | E | Auditor name and firm ID are tagged on the 10-K cover page **in recent years**. A change is a year-over-year comparison; earlier years need a different path. |
| Restatement | E, **with care** | Non-reliance is an 8-K item; recent 10-K cover pages carry error-correction flags. **Confirm coverage for the window you need before relying on either.** |
| Share count growth | E | |

## 4. Valuation (§4.4, 25%)

| Variable | Source | Notes |
|---|---|---|
| Enterprise value | **E + P** | Net debt from filings; market cap needs price × shares. |
| FCF yield (FCF ÷ EV) | **E + P** | FCF itself is EDGAR: OCF − capex. |
| EV/Sales, EV/EBITDA, EV/gross profit | **E + P** | |
| Earnings yield (EBIT ÷ EV) | **E + P** | |
| Sector-relative ranking basis | E + **?** | Ruling 13 replaced SIC with Lynch archetypes. **The classifier is unbuilt** - testplan OPEN-11. |

## 5. Reinvestment runway (§4.5, 15%)

| Variable | Source | Notes |
|---|---|---|
| Reinvestment rate | E | Capex, R&D and acquisitions over NOPAT. **Gated by §11.1** - the R&D treatment decides this. |
| Incremental ROIC | E | |
| Net debt/EBITDA, interest coverage | E | |
| Capital allocation record | **E + P** | Buyback dollars are in the cash flow statement, but *"executed at low valuations"* requires **the valuation at the time of the buyback** - a historical price. |

## 6. Eligibility and universe (§5.3)

| Variable | Source | Notes |
|---|---|---|
| ≥3yr filing history | E | |
| Financials / REITs exclusion | E | SIC ranges from submissions metadata. **SIC survives here** even though ruling 13 replaced it for valuation ranking - **exclusion and ranking are different jobs.** |
| Pre-revenue detection | E | |
| Market cap floor | **E + P** | |
| Liquidity / volume floor | **P** | Volume is not in any filing. |

---

## 7. The price dependency, stated once

**Three parts of the model need a share price:** the valuation block, the
capital-allocation metric, and the market-cap and liquidity floors. Ruling 11
removed the fourth (Altman). **This is not avoidable by better EDGAR work** -
shares outstanding is filed, price is not.

Two properties the price source must have. **Neither is the usual one**, and
both belong in the vendor question (testplan OPEN-9):

**7.1 — Unadjusted closes, not just adjusted ones.** Back-adjusted series
restate history for splits and dividends. **Multiplying a back-adjusted price by
shares outstanding gives a market cap nobody ever observed.** This is the
identical failure to the restated-financials lookahead the TDD rejects in §5.1 -
same shape, different dataset - and **it will pass every test that does not
check for it specifically.** Store the as-traded close and the adjustment
factors separately.

**7.2 — Delisted coverage.** §5.1's point-in-time property exists so a backtest
reads what was knowable. A vendor that drops delisted names **hands back
survivorship bias through the door ruling 5 closed.** Ask it in the operative
form: *does a delisted ticker's history stay retrievable after delisting* - not
*does the vendor claim "full history."*

---

## 8. Fund side (D-027 / D-028)

**Holdings:** SEC N-PORT data sets, free, flattened from NPORT-P XML. **The
public portion covers the third month of each fiscal quarter only** - the first
two months stay confidential. D-027's quarter-lag is **statutory**, and no amount
of money removes it.

**Identifiers:** holdings carry **CUSIP/ISIN/LEI, not tickers.** The crosswalk to
scored equities is a build item and is **where `UNRESOLVED_IDENTIFIER` comes
from** (A-002). **CUSIP is licensed** - worth a look given D-020 keeps the repo
public.

**Non-equity weight (D-028's floor):** N-PORT's per-position asset category
supports this directly. **Best-sourced part of the fund design.**

**The gap - expense ratio and turnover.** D-027 states **cost is the strongest
single predictor of long-run fund outcomes**, and it is the one variable with
**no established free source.** Not in N-PORT. It lives in the prospectus fee
table and the annual report's financial highlights; N-CEN *may* carry some of it.
**Unverified, and not asserted.** Tracked as testplan OPEN-12.

---

## 9. Universe construction — the survivorship answer

`company_tickers.json` and `company_tickers_mf.json` are **current** universes.
Delisted stocks and dead funds are not in them.

Derive the historical universe from **filing history**. A CIK that filed 10-Ks
from 2011 to 2017 and stopped **is in EDGAR permanently.** Building the universe
from the fact store's own filing record gives a **point-in-time universe by
construction**; the ticker files then serve only as the current-day identifier
crosswalk.

Ruled — ruling 5. **Constrains the first migration** (see D-next/universe-from-filings).

---

## 10. What this map rests on that is not yet verified

**Lineage §11 holds ten citations written from memory without web access.**
TDD §12 requires them verified before any reach a user-facing surface. **Two are
load-bearing for this map:**

- the exact **Novy-Marx gross-profitability** definition (§2 above), and
- **Sloan's accruals** formulation (§3 above).

Until verified, §2 and §3 rest on the Planner's recollection — **the same class
of claim the register exists to stop.** Tracked as testplan OPEN-13.
