# CLOSEOUT AND PREWORK — Planner's half — StockGraderMDK — 2026-09-25 — r2

**From:** Planner · **For:** the next Planner context, the owner, and the Builder
**Pairs with:** `CLOSEOUT-Code-2026-09-25-...-builder-half-and-prework.md`

**Supersedes** the first issue of this document. **What changed:** every
reference number is now explained where it appears, so this can be read without
the register open — the first issue could not be. Two items ruled by the owner
since are folded in as settled. Nothing else changed.

**Read Code's closeout first.** It carries state and environment. The register
carries decisions. **This duplicates neither.** It is judgment, the error record,
and the two sessions that have never been scheduled.

---

# PART 0 — Start here, next Planner

**Read the register before writing anything** — not this conversation, not a
handover.

- **`docs/planner/INDEX.md`** on branch `pr6-backup-strategy` is the only way in.
  GitHub refuses automated reads of directory listings, and constructed URLs are
  rejected, so **you need one file URL pasted by the owner** and then every
  document links from there.
- Also on that branch: `decisions.md`, `findings.md`, `testplan.md`,
  `assumptions.md`, `planner-errors.md`, `architecture.md`, `gqs-source-map.md`.
- **The `main` branch is days out of date.** It answers confidently and wrongly.
  That mistake has already been made once.

**The most important rule in the error record: write orders against the register,
never against the last handover.** A handover records what was true when it was
written.

---

# PART 1 — What only this context knows

## 1.1 The owner

**He rules fast and well; the failure mode is not indecision.** Give him a
numbered list with a recommendation and a stated cost and he answers in the same
message. Give him an open question with no options and it stalls.

**He reverses cleanly when the premise changes.** The cluster freeze went blanket
to destruction-only in one exchange; the database-tier question died the moment
he said money was not the blocker. **Do not defend a position after its premise
moves.**

**Terse answers are real answers and are occasionally ambiguous.** "Take Z" meant
the private-firm variant; "nope" meant the opposite of what I inferred. **State
your reading in one line and mark it reversible** — that turned two misreads into
one-line corrections rather than discovered errors.

**Do not put decisions to him by reference number.** He does not have the
register open, and asking someone to rule on "OPEN-17" is not asking a fair
question. **Say what the thing is, every time.**

**He tells you when process is eating the work**, and he was right before the
numbers were in, twice.

## 1.2 What the Planner is actually for

Three days of register reviewed, the Planner earned its keep in one mode:
**finding what a correct-looking artifact cannot represent.**

The catches that mattered were all the same question — *what does this make
unaskable?*

- The fact table's uniqueness key omitted the entity identifier, so two
  co-registrants in one filing would have collided and one would have been
  silently discarded as a duplicate.
- The quarantine table for conflicting rows had no uniqueness, so re-running a
  load would have duplicated its own refusal records.
- A guard rewritten to derive its table list from the database catalogue still
  enumerated a *schema* — a table in another schema escapes it exactly as the
  original missed one table.
- The planned scores table would have overwritten a 2019 score on recompute,
  making every backtest measure today's model against history.
- Empty values and unparseable values look identical once both are stored as
  null.

**Everything else the Planner did was process.** Ask that question of every
artifact and be sparing with the rest.

## 1.3 What the Planner wasted

**Manifests.** 31 of 79 Planner documents were accounting for Planner documents —
more manifests than rulings. Necessary (six real losses were caught) and a
symptom.

**Open items.** Most of the register's open backlog is mine. Several were
load-bearing; several were observations I promoted to obligations because it
*felt* more rigorous. It is not — it is a backlog the next context inherits.

**Measurements with nothing behind them.** Two sittings and a Docker install went
to pricing a $244/month decision the owner had already declared irrelevant.

---

# PART 2 — The Planner error record

Held in `docs/planner-errors.md`. **The rules are the point; the incidents are
evidence.**

| Error | Rule it produced |
|---|---|
| Ordered work that was already complete, having planned from a handover rather than the register | **Orders are written against the register.** A handover records what *was* true |
| Assigned finding numbers by reading a document instead of the findings file; both were taken | Numbers come from the register. Use `F-next/<short-name>`, never a numeral |
| Presented a guess about what a command probably does as though it were a finding | Reasoning about a command is not a finding |
| Revised a delivered document and reissued it under the same filename | **Filenames are not identity.** A revision gets a marker and says what it supersedes |
| Wrote a delivery manifest that did not list itself | **A guard's own artifact is the first thing outside its coverage** |
| A cumulative document count that double-counted, and so grew wrong over time | An error that compounds eventually misleads; a constant one merely annoys |
| Stated a counting rule and a figure that contradicted each other | Give both readings and ask, rather than guess a third time |
| Told the owner to require a CI check by a name taken from the workflow file rather than from what the platform reports. The real name differs; the wrong one would have blocked **every merge** with no failure to diagnose | **Identifiers a platform reports are read from the platform, by query** |
| Wrote a database cutover procedure that only worked on an app that had never been connected to a database | **Recovery always happens on a system that already has state** |
| Named data sources in a handover that contradicted a ruling already in the register — it would have rebuilt the survivorship bias that ruling existed to remove | A handover naming sources **cites the ruling each one satisfies**. No citation means an unmade decision |
| Called two clusters idle based on a listing already proven unable to answer that question. One may be a live production database | **A source unreliable for one question is not reliable for its converse** |
| Let the owner rule a data coverage window before anyone had measured storage per row — and the window turned out not to be the constraint | **A ruling that depends on a figure waits for the figure** |
| Deferred the R&D question to "its own session" on day one and never scheduled one | **A deferral without a date is a deferral without an end** |

**That last one is still costing.** Three days, and the product's critical path
has not moved.

---

# PART 3 — Doctrine, the decision half

Code's closeout carries the four failure shapes for building. These are the four
for deciding.

**1. Store, don't filter.** Reached independently four times — superseded
filings, dimensional facts, amended values, and the coverage boundary. **A schema
that cannot represent a distinction cannot refuse it.** The corollary catches
people: a load boundary recorded as data is honest; the same boundary applied as
a filter is a lie by omission.

**2. The first case to present is not a sample.** Three reversals, one query
each. The first duplicate row we hit was harmless, so deduplication looked safe —
31 of the next 32 disagreed on value and would have been silently discarded. The
first re-send that worked seemed to prove the filename was at fault — two things
had changed. Early filings were predicted to carry more custom tags than recent
ones — the opposite was true. **Encounter order correlates with nothing.**

**3. An expectation is what makes a count a check.** A count with no prior
expectation returns a number that looks like an answer and nothing disputes it.
Twice, the stated expectation caught the counting *method* rather than the
figures.

**4. A measurement is only worth its cycle if a decision changes on the result.**
Name the decision; check it is still open. Recorded one day and violated the
next, by both agents.

**And the meta-rule, which is why the others keep failing:** *a rule is indexed
by the situation that produced it, and the next situation arrives without
consulting it.* No fix except reading the register before deciding.

---

# PART 4 — The register sweep, proposed

The register carries roughly three dozen open items and most are notes. **The
Planner proposes; the Builder applies.**

**Close on evidence:**

- The live PostgreSQL version — was unknown for two days, now established as
  16.15.
- The period derivation — whether we correctly turned the SEC's end-date and
  duration fields into reporting periods. Proven on 3.37 million real rows.
- Three duplicate entries where the same question is filed twice, once answered
  and once open.

**Genuine gates — keep open:**

- The fifth migration for empty values (**now ruled — see Part 5.0**).
- Dropping the two compromised database accounts. **The window is closing** —
  this was cheap while the database was empty, and it now has tables.
- The accruals formula (**now ruled — Part 5.0**).
- Fund score sequencing: build on cheap current cost data with the central
  validation deferred, or wait for the expensive historical version.
- Price vendor selection, which needs three properties confirmed with the
  vendors: unadjusted as-traded closing prices alongside adjusted ones, delisted
  companies' history still retrievable after delisting, and a delisting date per
  symbol.
- Provenance on columns that get updated rather than only created.
- The acceptance test for the filings archive: Lehman Brothers present with
  filings ending in 2008.
- **The R&D question.** Part 5.1.

**Demote to notes — recorded, gating nothing:** the storage-resize question, the
memory measurements, the recovery-window probe, the query-plan measurement, the
backup-expiry observation, and the detach-at-destroy note. **Test: name what it
blocks. If nothing, it is a note.**

**Delete nothing.** A demoted item keeps its text and its reason. The register's
value is that struck claims stay visible with why.

---

# PART 5 — The prework

## 5.0 Two items the owner ruled today — settled, not outstanding

**Empty values.** 179,806 rows arrived with no value, including net income and
shareholders' equity. Established: the SEC publishes them empty and **none are
our parsing failures**. **Ruled: store them as real assertions of "no value
here," kept distinguishable from a genuine zero.** The reason is that *the filer
tagged this concept and asserted nothing* and *the concept never appeared* are
different facts, and collapsing them is irreversible. Requires a fifth migration,
since the value column is currently mandatory. **Code is cleared to build it.**

**The accruals formula.** Sloan's 1996 original differences balance sheets; the
alternative takes earnings minus operating cash flow from the cash flow
statement. **Ruled: the cash-flow version, recorded as a deliberate departure
from the original.** They diverge most for companies that made acquisitions,
because a balance-sheet difference reads an acquired subsidiary's working capital
as though the company generated it — and those are exactly the companies the
growth block's organic-versus-acquired check exists to catch, so the two measures
would be fighting each other.

**The owner's framing is worth keeping**, because it names the family: a real
estate owner borrows one property's turnover figure and applies it across eleven
addresses that never generated it. **That is the same error as attributing a
parent's filed numbers to its co-registrants, and the same error as reading an
acquired subsidiary's balance sheet as organic.** A number borrowed across an
entity boundary nobody recorded.

## 5.1 Session one — R&D treatment. **This is the product's critical path.**

**What it decides:** whether research and development spending is left as
accounting rules treat it — an expense in the year incurred — or capitalised as
an asset and written down over an assumed useful life.

**Why it is genuinely open:**

- **Leaving it as an expense systematically penalises the businesses a
  growth-quality model should rank highest.** Heavy R&D depresses earnings,
  returns on capital, and reinvestment ratios — which are the inputs to two of
  the five scoring blocks.
- **Capitalising inserts an assumption nobody discloses.** No filing states the
  useful life of research. Choosing three, five or eight years *is* the ranking
  for research-intensive companies.

**What it blocks:** the scoring specification refuses itself for build while this
is unresolved. **Nothing scoring-related can issue until it is ruled**, and it is
the same question the specification lists twice.

**Three ways to settle it, in preference order:**

1. **Rule that version one does not claim to handle research-intensive companies
   well, and state that limitation in the output.** Cheapest, honest, reversible.
2. **Compute both and report the rank correlation.** R&D expense is a filed
   figure and the store now holds it. Scoring under both treatments and measuring
   how much the ranking moves converts an argument into a number.
3. Capitalise with a stated life and a sensitivity note.

**I recommend starting the session with option 2.** It is the one thing that has
become possible since the question was deferred — the facts now exist — and it is
what this project does with everything else: replace judgment with evidence where
evidence is affordable.

## 5.2 Session two — port the scoring specification to this codebase

The growth score specification was written on 2026-09-09 for a **different
project** — an existing finance agent in another repository. The owner ruled it
be revised rather than patched. Not started.

**What must be rewritten:**

- Its pre-build checklist names a migration tool this project explicitly
  rejected, an agent that does not exist here, a settings pattern from the other
  codebase, and a trading function this project has no equivalent of.
- Its claim that the score is computed **from SEC filings only** is false as
  written — a quarter of the score needs market prices, which filings do not
  contain.
- Four rulings made since need folding in: company grouping by behaviour rather
  than industry code, a flat cost-of-capital figure with the condition that the
  result is never shown as an absolute number, an optional size adjustment
  defaulting off, and the private-firm variant of the bankruptcy score.

**And the revised specification's own completeness gate must be met before a
build order issues.** That gate is the specification's rule, not a Planner
objection, and routing around it once means it stops being one.

## 5.3 Session three — the first endpoint that reads the data

Small, and it has been waiting for something to read. It closes the credential
question's application half, moves the recovery table's untested row off
**Never** for the data half, and makes the deployment gate able to notice an
undeployed secret for the first time.

---

# PART 6 — The honest accounting

**Three days. 79 Planner documents, 57 Code documents, 55 commits.**

**What exists:** four applied migrations, a migration runner that refuses to open
a connection if a file tries to control its own transaction, a rate-limited SEC
client, a fact loader, 96 tests, and **3,368,813 real SEC facts on a real
cluster.** A restore drill that found the cutover command will not overwrite an
existing connection string, that a restored cluster carries compromised accounts
forward, and that an undeployed secret reproduces on demand.

**What does not exist:** any score, any endpoint that reads the data, any UI.

**The single sentence that describes the project:**

> **The store holds 3.37 million real facts and nothing reads them.**

**The rigor was not the problem and should not be cut.** Everywhere it touched a
built thing it paid: a storage estimate 56% low, a table name that is a reserved
SQL word surviving nine references and a review, a test harness reporting five
green guards while running nothing, three predictions reversed by their
populations, and a CI check name that would have blocked every merge with no
failure to diagnose.

**The problem was where it was spent** — on arguments about unbuilt work, against
a database with no schema. Both agents reached that diagnosis independently and
so did the owner, which is why it never needed arguing.

**To the next Planner:** the register is better than anything you will write.
Read it, ask of every artifact what it makes unaskable, and resist turning every
observation into an open item. **The critical path is the R&D question, and it
has been waiting three days for someone to sit down with it.**
