# RULING RECORD — Owner → Planner — StockGraderMDK: thirteen rulings, 2026-09-23

**From:** Planner, recording owner rulings received 2026-09-23
**For:** `decisions.md` on `pr6-backup-strategy`
**Status:** twelve ruled, one recorded as a deferral rather than an answer
(11.1), which is itself the owner's ruling on how that question is handled.

---

## 1. Ruled — drill and infrastructure

**1. Cutover-and-stay. RULED.** `stockgrader-db-r1` becomes the live cluster.
Today's ticker load goes onto it. §4 of the amended ruling runs as written.

**2. B-1 through B-8 as amended. RATIFIED.** Status moves PROPOSED → RULED in
`decisions.md`. B-2 carries the amended rationale (deliberateness, not absence),
B-6 the chain-root reading of retention, B-8 the corrected scope claim.
B-6a remains an open testplan item dated 2026-10-03.

**3. B-9 — PITR window probe. APPROVED.** Runs after §4 completes, never
interleaved. The restored probe cluster is destroyed immediately once the window
is recorded. The measured boundary is the finding; a refusal names it as
usefully as a success.

**6. Old cluster destroy and `fly-user`. RULED as proposed.** The old cluster is
destroyed once the ticker load and a DB-backed endpoint are proven on
`stockgrader-db-r1`. That destroy retires both the exposed application credential
and `fly-user` rather than either being rotated in place. **This is the closure
of D-029, and it is the honest one** — replace, never rotate. Until the destroy,
both credentials remain live against the old cluster and that is a stated fact,
not a hypothetical.

---

## 2. Ruled — data and model

**4. SEC is one source among several. RULED.** The TDD's §2 goal 1 ("from SEC
filings only") and §5.1's single-source framing are **corrected** in v4. Data is
taken where it is available.

**This is a ruling on sourcing policy, not a vendor selection.** The price
vendor is still unchosen, and the deciding question is delisted coverage —
a vendor that drops dead names reintroduces survivorship bias through a door the
universe fix (ruling 5) just closed. Tiingo and EODHD both need that question
put to them directly before either is picked. Tracked as an open item.

**5. Universe derived from filing history. RULED.** The historical universe comes
from the fact store's own filing record, not from `company_tickers.json`. The
ticker files serve as the current-day identifier crosswalk only. This constrains
the first migration: the fact store carries filing dates and accessions from the
start, which §5.1 already required for a different reason.

**7. D-010's condition reworded. RULED.** "Five open questions in its §17"
becomes **"the four open questions in its §11."** The condition is unchanged in
substance; it now points at a section that exists.

**8. GQS v4, grounded on this repo. RULED.** GQS v3 is revised to v4 rather than
ported inside a build order. §12's confirm-before-build list is rewritten against
StockGraderMDK — `alembic heads` is removed (D-021 rejected Alembic), the
`finance` agent and settings-overlay items are replaced with this repo's
equivalents, and §3's `place_stock_order` non-goal becomes moot rather than
satisfied, since no such path exists here.

**Rationale worth preserving:** §13 refuses the document for build. Carrying the
port inside a build order would mean the refusal never formally lifts, and a
completeness gate that is routed around once stops being a gate.

**9. §11.3 WACC — flat rate for v1. RULED as proposed.** **Condition:** the
ROIC−WACC spread is never surfaced as an absolute figure while the flat rate is
in force. It is defensible for a relative ranking and indefensible as an absolute
number, and the condition is what keeps the two apart.

**10. §11.4 size tilt — available, default off. RULED as recommended.** Enabling
it is a deliberate act rather than a hidden thumb on the scale.

**12. §11.1 R&D capitalization — DEFERRED to its own session. Not ruled.**
The owner agreed it warrants dedicated treatment. **§11.1 therefore remains an
open question, and §5.4 with it.** §13 continues to refuse the TDD for build on
those two grounds. This is recorded as a deferral, not an answer, so that no
later reader mistakes agreement-to-defer for a ruling.

**Obligation attached by the owner:** the deferral carries forward into a
**closeout and prework document** for its dedicated session, not into memory.
That document names what §11.1 has to decide (capitalize or unadjusted GAAP;
if capitalized, what useful life), what it would reorder, and what evidence
would settle it — so the session opens on a prepared question rather than on a
re-derivation of why the question is hard.

---

## 3. Ruled — the two clarified items

**11. Altman variant — Z′. RULED.** The private-firm form, book value of equity
in the fourth term. The disqualifier does not move with the share price.

**Reason recorded, per the owner's instruction:** §3 of the TDD names price and
technical signals as a non-goal on the grounds that including them quietly
converts a hold model into a trading model. An integrity gate built on market
value of equity would disqualify a company on a day its fundamentals did not
change, which is that failure in its least visible form — inside a gate rather
than inside a block. Z′ is chosen for that reason and not for sourcing: ruling 4
means market equity is available, so this is a design choice made with the
alternative in hand.

**13. §11.2 sector granularity — option (c), Lynch-style archetypes with
per-archetype metric sets. RULED**, with an explicit fallback (below).

Two consequences to carry into v4, neither of them objections:

**Archetype assignment becomes its own computed thing.** Fast growers,
stalwarts, cyclicals, turnarounds and asset plays are not derivable from SIC —
SIC says what industry a company is in, not which of Lynch's five it behaves
like. The classifier needs its own definition, its own `insufficient_data` path
for companies that fit none cleanly, and its own place in the output, because a
reader who cannot see which archetype was assigned cannot evaluate the
sector-relative rank that followed from it.

**It is partly circular, and the circularity needs stating rather than solving.**
Classification would draw on growth stability, margin behaviour and asset
intensity — the same fundamentals the blocks then score. That is tolerable if
the classifier is specified independently and frozen before scoring runs, and it
is a quiet disaster if the classifier is tuned until the rankings look right.

**The fallback, made operational.** The owner's "if we find we need to change
that later, we can" only fires if something is watching for it. §11.2 falls back
to SIC-as-is if either holds: the archetype classifier is still unspecified when
every other §13 condition has cleared, or a hand-check finds it assigns
archetypes the owner disagrees with more often than it agrees. Recorded in
`testplan.md` so the fallback has a trigger rather than a hope.

---

## 4. §13 completeness gate — current state

| §13 condition | State |
|---|---|
| Any §11 question unratified | **OPEN** — 11.1 deferred. 11.2, 11.3, 11.4 ruled |
| §5.4 R&D treatment unresolved | **OPEN** — same question as 11.1 |
| Eligibility table contains an unlisted class | Believed clear; confirm in v4 |
| Any block contains a placeholder metric | Confirm in v4 |
| Point-in-time property weakened in build order | Not yet applicable |

**No scoring build order can issue.** Ingest is unaffected and proceeds.

---

## 5. Unblocked now

The drill has everything it needs. Coder hands over amended §4 one command at a
time, then B-9, then ingest per rulings 4 and 5.
