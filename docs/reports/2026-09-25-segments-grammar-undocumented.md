# REPORT — Code → Planner — StockGraderMDK: the `segments` grammar is undocumented, and the data breaks it

**From:** Code (Builder) · **Issued:** 2026-09-25, first issue
**Follows:** `2026-09-25-fact-loader-built.md` · **Executes:** its §8 item 3
**Branch:** `pr6-backup-strategy`, HEAD `5780c46`, pushed
**Suite:** 92 → **96** · **Fly cluster mutations: NONE** · No money spent
**Network:** two SEC fetches through the rate-limited client, declared
User-Agent, no 403

---

## 1. The task's premise did not hold

The item was *confirm the `segments` grammar against `readme.htm`.* **It cannot
be confirmed, because `readme.htm` does not state it.** The field's complete
documentation is:

> *"segments — XBRL tags used to represent axis and member reporting"*

No delimiter. No format. No example.

**The same readme settles `version`, `ddate`, `qtrs` and `coreg` precisely** —
which is why the gap is worth reporting rather than shrugging at. Four adjacent
fields are specified and this one is described.

**So the loader's grammar was established from data whether or not anyone
intended that.** The docstring now says so explicitly, because a reader who
assumes a specification exists will treat a future refusal as bad data when it
may be a wrong reading.

### 1.1 What that changes

**A refusal counter means something different under an undocumented grammar.**

- Documented: a refusal is **bad data**.
- Undocumented: a refusal is **bad data OR a wrong reading**, and the loader
  cannot separate them from the inside.

That distinction was invisible while the grammar was assumed. It is the reason
this is a finding rather than a task completion.

---

## 2. Measuring it found a real defect — 12,503 rows per quarter

Verified against **two quarters eleven years apart**, because one quarter is not
a sample:

| | 2015q2 | 2026q2 |
|---|---|---|
| `num.txt` rows | 2,588,598 | 3,608,711 |
| non-empty `segments` | 1,066,226 (**41.2%**) | 2,189,835 (**60.7%**) |
| accepted **before** the fix | — | 2,177,332 (**99.43%**) |
| accepted **after** | **1,066,226 (100%)** | **2,189,835 (100%)** |

**Both row counts reproduce the register's earlier figures exactly**, which
checks the fetch and the archive identity as well as the parser.

### 2.1 The cause

**FSDS's own extraction leaves bare `amp;` inside member values** — the wreckage
of an HTML entity whose ampersand was stripped somewhere upstream:

```
InvestmentIdentifier=Dun amp; Bradstreet Corporation, First lien senior secured loan;
InvestmentIdentifier=8th Avenue Food amp; Provisions, Inc., First lien senior secured loan 1;
InvestmentIdentifier=Cube Industrials Buyer, Inc. and Cube Aamp;D Buyer Inc., ...
```

**The delimiter character occurs inside the values it delimits.** Splitting on
`;` cut `Dun & Bradstreet` in half, and the refusals concentrated in exactly the
filers whose holdings carry ampersands — a systematic bias, not scattered noise.

### 2.2 The fix, and why it is not a special case

**A semicolon ends a pair only when what follows begins another one.** A fragment
containing no `=` cannot be a new pair, so it rejoins the previous member.

That is derived from the grammar's own shape rather than from a list of
known-bad strings, so it handles ampersands it has never seen.

### 2.3 The mangling is preserved, not repaired

`store, don't filter`. Un-escaping `amp;` to `&` is a correction that cannot be
justified per row, and **dimensions are part of `fact_one_per_filing`** — so
patching some rows and not others would manufacture false distinctions in the
uniqueness key. Every value carries the same distortion, the store stays
internally consistent, and the distortion is recorded rather than silently
patched.

---

## 3. What is NOT established

**Whether a member value may legitimately contain `=`.** If one does, the rejoin
would mis-split it.

**Zero occurrences across 3,256,061 real values in two quarters eleven years
apart.** That is strong evidence. It is not a specification, and §1.1 is exactly
why the difference matters here. **Noted, not closed.**

---

## 4. The shape, for the third time today

| | The stated basis | What it actually covered |
|---|---|---|
| **A2** (OPEN-60) | "derived from the catalogue" | one schema |
| **A5** (OPEN-59) | "no uniqueness that would refuse a competing value" | any uniqueness touching `concept` |
| **`segments`** | "the documented grammar" | a grammar inferred from data |

**Each was reasonable and each was narrower than the thing it stood in for.**
Two of the three were found by something forcing the question — a constraint
refusing a row, a fix being blocked. This one was found by reading the source.

---

## 5. State

**HEAD `5780c46`, pushed. 96/96 under this repository's own `.venv`.**
No cluster mutation, no money spent. Nothing half-built.

`tools/check_segments_grammar.py` reproduces the measurement. **Both archives are
cached locally (139 MB)**, so the first real load needs no refetch.

---

## 6. Next, and it is one thing

**OPEN-27 steps 1–3, owner at the keyboard, one command at a time.**

Everything else on the path is built and waiting: four migrations, the runner,
the EDGAR client, slice 1, the fact loader, 96 tests, and two real archives on
disk. **None of it has met a Fly cluster.**

After the `schema_admin` exists and is proven: apply 0001–0004 to
`stockgrader_scratch`, load a real quarter, then the first DB-backed endpoint —
which closes D-029's application half and moves recovery row 4 off `Never`.

**Still blocked, and not by infrastructure:** scoring, on §11.1 and §5.4. **P-13
remains the finding that matters** — deferred to "its own session" on day one,
no session ever scheduled.
