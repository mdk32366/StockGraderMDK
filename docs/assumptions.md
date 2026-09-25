# Assumptions — What are we taking for granted?

Two bars. If you can't state the test that falsifies it, it doesn't go in. If
nothing breaks when it's false, it's a detail, not an assumption. Read this
file when writing a decision and when something breaks. Never on a schedule.

---

**A-001 — Public N-PORT filings give usable position-level fund holdings**
Relies on: SEC N-PORT filings disclosing each fund's holdings with weights, on a
cadence and lag we can state.
Falsified when: the current public-disclosure cadence or lag (verify it; the
SEC amended N-PORT timing recently and the regime in force is unconfirmed) makes
holdings too stale to support an overlap claim, or a target fund doesn't file
N-PORT at all.
Consequence: overlap is a dated snapshot at best. Every overlap response must
carry its holdings as-of date either way.
Status: ASSUMED

**A-002 — Holdings resolve to a common identifier across funds**
Relies on: N-PORT positions carrying a CUSIP or ISIN that matches the same
security in another fund.
Falsified when: a material share of a fund's weight carries only "other
identifier" or none at all. Measure it per fund as resolution coverage.
Consequence: overlap is silently **understated**, the plausible-and-wrong shape
(KEEL P11). Mitigation: coverage is always reported, and unresolved holdings are
a named category, never dropped.
Status: ASSUMED

**A-003 — The price source permits redistribution through our API**
Relies on: the vendor's terms allowing prices, or values derived from them, to
be served to another application.
Falsified when: the terms prohibit redistribution or derived-data display.
Consequence: the data layer is rebuilt after launch. Scraped or unofficial
sources almost always fail this.
Status: ASSUMED · settled by D-007

**A-004 — SEC EDGAR access stays within fair-access terms from Fly**
Relies on: a declared User-Agent with contact info, and request rates within
SEC limits, being accepted from Fly egress IPs.
Falsified when: EDGAR returns 403 or 429 to ingestion.
Consequence: ingestion stops. Unless a guard turns it red, the data quietly
ages. Ingestion must fail loudly and responses must show data age.
Status: ASSUMED

**A-005 — A changed runtime secret reaches the app without an image rebuild**
Relies on: Fly applying `fly secrets set` (or a staged secret plus
`fly secrets deploy`) by restarting Machines on the existing image.
Falsified when: a secret change triggers a rebuild, or the app keeps the old
value (the KEEL P4 scar: a secret left Staged returned zero rows instead of an
error).
Consequence: re-pointing at a restored database costs a build. Recovery Access
Problem 3.
Status: ASSUMED · test on a non-emergency day, then record the exact command in
architecture.md

**A-006 — Pinned dependencies render an identical OpenAPI schema on Windows and Linux**
Relies on: FastAPI/pydantic schema output being deterministic across OS for the
pinned versions, and `read_text` normalizing CRLF.
Falsified when: `test_openapi_matches_committed_contract` passes on one platform
and fails on the other with no code change.
Consequence: a false red on one side, or a snapshot regenerated on the wrong
platform that masks real drift.
Status: TESTED 2026-09-22. The contract test passed on Windows (PS 5.1, Python
3.12.10, F-008) and on Linux (Python 3.12.3, F-002) against the same snapshot.
Sample: one run per platform. Re-test whenever a pin changes.

**A-007 — As-originally-filed fundamentals are recoverable from SEC XBRL data**
Relies on: each reported fact carrying its filing date and accession number, so
the value knowable on any past date can be reconstructed even after later
restatement.
Falsified when: restated values overwrite originals in the source, or facts lack
a usable filed date for the periods needed.
Consequence: any backtest reads hindsight numbers, and the score looks better
than anything that was actually knowable. GQS v3 §5.2's point-in-time
requirement could not be met.
Status: ASSUMED · load-bearing only if D-010 adopts GQS; if so, test before the
first migration

**A-008 — On a windows-latest runner, `py -3.12` finds a Python installed by actions/setup-python**
Relies on: setup-python registering its install so the `py` launcher can
resolve `-3.12`.
Falsified when: the D-014 job fails at setup.ps1's `py -3.12` check although
setup-python reported success.
Consequence: D-014 needs a different interpreter-discovery step, or setup.ps1
needs a documented CI path. The rule must not be weakened to fall back to
another Python (D-011).
Status: **TESTED 2026-09-22, HOLDS.** First D-014 run, Actions run
[35755627563](https://github.com/mdk32366/StockGraderMDK/actions/runs/35755627563),
job `windows-setup (PS 5.1)`: setup-python reported CPython 3.12.10, and
`py -3.12 --version` returned `Python 3.12.10`, resolving to
`C:\hostedtoolcache\windows\Python.12.10d\python.exe`. `setup.ps1` then
reached `Suite GREEN`, and `-SuiteOnly` ran green after it. **Sample: 1 run.**
Note: the runner's `py` default is `3.14`, the same shape as the workstation in
F-005 -- `py -m venv` on either machine yields 3.14, not the pinned 3.12. D-011
now has two independent instances rather than one.

**A-009 - A platform region stays available**
Relies on: a region named in `fly.toml` continuing to accept new resources.
Falsified when: provisioning is refused for a region already in the config.
Consequence: configuration goes stale with **no code change and no warning**,
and it fails at provisioning time rather than at review time. Nothing in the
repo changed between the config being correct and being wrong.
Status: **REFUTED once already, 2026-09-22**, for `sea` (F-011). Held for `sjc`
as of the same date. Required alongside D-017.

**A-014 - Enough of a typical fund's weight resolves to securities carrying a GQS**
Relies on: the identifier spine resolving a large majority of a fund's weight to
US-listed common stocks that have enough filing history to score.
Falsified when: scoreable weight for ordinary funds sits below D-027's coverage
floor.
Consequence: the fund score returns `insufficient_data` for the funds people
most want scored, and D-027 Part B (cost, turnover, tenure, concentration)
carries the whole thing on its own. That is not a failure of the design, but it
must be discovered before the look-through machinery is built, not after.
Status: ASSUMED. Tested by Phase 2's resolution-coverage figure.

**A-015 - Quarter-lagged holdings are close enough to current to be informative**
Relies on: a fund's basket not turning over so fast that last quarter's holdings
misdescribe today's portfolio.
Falsified by: high-turnover funds, where last quarter's basket is not this
quarter's.
Consequence: the score describes a portfolio that no longer exists, while
looking current. Mitigation: report turnover alongside it, and carry both dates
per D-027 trap 3 so nobody has to infer the lag.
Status: ASSUMED.

**A-016 - The Planner has not read GQS v3**
Relies on: nothing - this is a statement of what is not known.
Falsified when: the TDD and `docs/finance/growth-model-lineage.md` reach the
Planner.
Consequence: D-010 is ruled on the **Builder's summary** of the document, not on
the document. A summary is not knowing (P8). Until the Planner has read both,
no scoring design work proceeds, and D-010's condition - ratification of the
open questions in the TDD - cannot even be assessed.
Status: **CLOSED 2026-09-23.** Falsified as intended: the Planner has read
`TDD-growth-score.md` and `growth-model-lineage.md` **in full, not a summary of
them**, and produced `PLANNER-NOTE-r2-2026-09-23-...-GQS-variable-source-map.md`.
**The reading immediately produced four findings** (F-next/gqs-tdd-defects) that
a summary had not surfaced - including that D-010's own condition cited a section
that does not exist, and that 25% of the score cannot be computed from the source
the TDD names as its only one. **That is the assumption doing its job:** it was
written to say the difference between reading and being told mattered, and the
difference turned out to be four findings and four rulings.

**A-017 - A `writer` can do everything the application needs**
Relies on: the application requiring row access only, with schema changes
confined to the D-021 migration runner.
Falsified when: the app cannot run its queries, or the migration runner turns
out to need the application's credential.
Consequence: D-031 cannot proceed and the app stays over-privileged at
`schema_admin`, leaving Step 16's separation nominal (F-017).
Status: **TESTED 2026-09-22, HOLDS.** Run as `builder_a017_probe` (`writer`)
against `stockgrader_scratch` on cluster `d1zj5omk443ryqkv`:

| Test | Result |
|---|---|
| `INSERT` | `INSERT 0 1` - works |
| `SELECT count(*)` | works |
| `UPDATE` / `DELETE` | `UPDATE 1` / `DELETE 1` - work |
| `CREATE TABLE` | **refused** - `permission denied for schema public` |
| `DROP TABLE` | **refused** - `must be owner of table` |

**Sample: 1 account, 1 database.** The second falsifier - the migration runner
needing the app's credential - remains **untested** and stays so until Phase 1.
The scratch canary table was verified back at **zero rows** afterwards, so the
test cleaned up after itself.

