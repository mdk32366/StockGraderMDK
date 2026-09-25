# REPORT — Code → Planner — price capture built, not yet run

**From:** Code (Builder) · **Date:** 2026-09-25
**Ruling executed:** **D-036** — TDD v3 §17.5 option (b), as-traded daily closes
captured going forward.
**Status: built, run, and capturing. UPDATED after the first live run.**
The first provider failed on contact and was replaced the same afternoon —
**F-041**. Nothing has reached the cluster.

**First successful capture, 2026-09-25 18:53Z: 10 symbols, 0 refused, 50 bars,
10 carrying the same-day guarantee.**

---

## 1. What was built

| | |
|---|---|
| `ingest/prices.py` | Provider-agnostic capture. `DailyBar`, `RawCapture`, one provider, disk writer. |
| `tools/capture_prices.py` | The daily runner. Dry by default; `--live` required to fetch. |
| `tests/test_prices.py` | 10 hermetic tests, no network, no database. |

**Suite: 108/108**, up from 98.

## 2. The property that let this be built before OPEN-9 is settled

**A close captured on the day it traded is as-traded by construction.** Split and
dividend adjustments are applied retroactively, so today's close cannot yet carry
a future adjustment. **That is the whole reason D-036 could be ruled ahead of the
vendor decision** — capture is provider-agnostic in a way backfilling never is.

Because that property is load-bearing, it is **asserted rather than assumed**:
`DailyBar.captured_same_day` records whether the bar's trade date equals the
capture date. A bar captured for an *earlier* date may already have been adjusted
by the provider and **does not carry the guarantee**, so it is flagged rather
than mixed in with bars that do.

The runner reports `bars_with_same_day_guarantee` and **exits non-zero if it
wrote files but captured no same-day bar**, because *the market was closed* and
*the provider is serving stale data* produce an identical file count.

## 3. What it refuses

- **An adjusted column is refused, never coerced.** If a payload carries any
  column matching `adj`, the parse raises. §7.1's failure — a back-adjusted close
  times shares outstanding giving a market cap nobody observed — **passes every
  test that does not check for it specifically**, so it is checked for at the
  door. `DailyBar` has **no adjusted field at all**, so there is nowhere for one
  to land by accident later; a test asserts that structurally.
- **An empty payload is an error, not a quiet "no trade."** The provider returns
  an empty body for an unknown symbol. **A symbol that silently stops capturing
  produces a gap shaped exactly like a weekend.**
- **A refusal is not retried blind** (D-023's rule, carried across).
- **The raw payload is kept beside the parse.** A parser bug found in six months
  is recoverable from the bytes and **not** from parsed output — and this data
  cannot be re-fetched for a past date. That asymmetry is the entire argument.

## 4. Why nothing has run

**`--live` is required and there is no default.** This is the first code here
that talks to a non-EDGAR provider while **OPEN-9 is still open**, and D-036 is
explicit that the provider is provisional and selects no vendor of record. The
default prints the exact URLs it would request and stops.

`StooqProvider` is the one implementation: free, **no API key** — which matters,
since no credential reaches the Builder — and it serves unadjusted daily closes.
**It is a seam, not a selection.** Swapping providers later invalidates no
captured row.

## 5. Three things this does not do, and one that needs the owner

**No database.** There is no price schema, and D-036 records that capture to disk
may begin before the schema lands because *the dates are the perishable part, not
the loading*. The on-disk manifest uses `fetch_log`'s column names verbatim —
`url`, `retrieved_at`, `sha256`, `content_bytes` — so the eventual loader renames
nothing, and a rename is a place for a value to change meaning silently.

**No migration, and it cannot be numbered yet.** `db/migrate.py` `discover()`
**refuses gaps in the sequence**. **0005 is reserved for OPEN-64's nil
assertions**, which is ruled but unbuilt, so a price migration cannot be 0006
until 0005 exists — and renumbering nil assertions to 0006 would strand the
register's existing references to "0005". **This is a register question, not a
capture question, and capture does not wait on it.**

**No deployment.** D-022 requires ingest to run as a separate Fly process group.
`fly.toml` **defines none**, and sets `min_machines_running = 0` — the app sleeps,
so nothing on it can run a daily job. **A scheduler is a separate build.**

**What the owner has to supply: the universe.** D-036 ruled *capture broader than
the current store*, and the runner takes `--symbol-file`. **Nobody has produced
the list.** The store's 6,179 filers are CIKs, not tickers; the `ticker` table
(0001) maps them, but it is populated from slice 1, which has **never been run
against the cluster**.

## 6. The first live run, when it is authorised

One command, and it prints what it did:

```
.venv\Scripts\python.exe tools\capture_prices.py --symbol-file <list> --live --out price_capture
```

**Start with ten symbols, not six thousand.** The first run is the one that finds
out whether the provider's shape matches the fixtures, and finding that out
across the whole universe costs a day of capture to learn a thing ten symbols
would have said.

## 6a. One risk the gitignore creates, stated rather than buried

`price_capture/` is **not** in git — it is data, it grows every trading day, and
it belongs in Postgres. **But this is the only data in the project that cannot be
re-fetched.** Facts reload from immutable FSDS archives; a lost capture day is
gone at any price.

**So until a price migration exists and the captures are loaded, this data lives
in exactly one directory on one machine.** That is a worse durability position
than anything else the project holds, and it is the direct consequence of
starting capture before the schema — which was the right call, but it is not free.
**It needs a backup that is not this repository, and not only this machine.**
The `.gitignore` entry says so where somebody will read it.

## 7. The honest column — and it came true within the hour

**It did.** `StooqProvider` serves a JavaScript browser-verification page to any
client that does not execute JS. **Ten hermetic tests passed against a provider
that cannot be reached**, and the first live run refused all ten symbols and
wrote nothing (**F-041**). Replaced with `YahooChartProvider`, which serves
`close` and `adjclose` in separate arrays — §7.1's requirement handed over by
the source.

**The premise now has a number behind it.** All ten of today's bars carry an
adjustment factor of **exactly 1.0**: adjusted equals as-traded, because no
adjustment has yet been applied to a price that traded today. *A close captured
on the day it traded is as-traded by construction* is measured, not argued.

**The original honest column, kept because it was right:**

**The fixtures are mine, not the provider's.** `tests/test_prices.py` proves the
parser handles the CSV shape **Stooq documents**. It does not prove Stooq serves
that shape, because verifying it requires the live call this report declines to
make. **A hermetic green here is not evidence that a capture succeeds** — the
same sentence `test_migrate.py` opens with, and the same one F-036 was about.

**Second: the cost of being wrong is asymmetric and favours running soon.** Every
day this sits unrun is a day of point-in-time history that cannot be bought back.
**A provider mismatch found on day one costs an afternoon; a week not captured
costs a week, permanently.** The dry run is the cheap half of that trade and it
has been taken. **The live run needs one word from the owner.**
