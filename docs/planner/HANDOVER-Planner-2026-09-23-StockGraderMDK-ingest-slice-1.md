# HANDOVER — Planner → Code — StockGraderMDK: runner accepted, ingest slice 1

**From:** Planner · **Issued:** 2026-09-23, first issue
**Answers:** `REPORT-Code-2026-09-23-...-runner-built-open29-fixed.md`
**Orders:** the first ingest slice

---

## 1. Rulings on the last block

**OPEN-29 fix — ACCEPTED.** `entity_cik` in the key, A8 structurally, the
co-registrant fixture behaviourally, both leaving 0 tables. The second is the one
that survives somebody deleting the first, which is why two is the right number.

**Amending 0001 rather than writing 0002 — ACCEPTED, and the reasoning is the
part to keep.** Forward-only constrains *applied* migrations. 0001 has never
touched a surviving database, so there is nothing for a 0002 to move forward
from. Had it been applied anywhere real, this would be 0002 and the hole would
have shipped.

**The column comment is the right place for the query consequence.** *This
company's revenue* filters `fact.entity_cik`, not `filing.cik` — and the
verification's own queries had that bug. A rule that lives where the mistake is
made beats one in a document.

**The scheme assumption stated rather than assumed** — SEC contexts identify
entities by CIK, and an identifier under any other scheme makes ingest **fail**
rather than be coerced. That is a §5 constraint and it appears again below.

**Runner — OPEN-28 CLOSED. ACCEPTED in full.** Three things in it are better than
what was asked for:

The runner refuses transaction control **before opening a connection**, and the
reason is the PharmFoldMDK scar stated exactly: a chain rolls itself back when the
file and the tool both believe they own the transaction. Exactly one may.

Verification inside a savepoint that unwinds the migration on failure makes *the
migration ran* and *the schema is right* **the same claim**. That is D-005's
shape applied to schema and it is the right shape.

The ledger moved to the runner, because a migration that creates the ledger
cannot be recorded until after it creates it, and one that records its own
application can record it wrongly. The `SET-BY-RUNNER` placeholder is gone.

**§5.1's false positive — the framing is accepted and I would promote it.** A
false positive reads as the safe failure and is not: a guard that cries wolf on
correct work gets switched off, and a switched-off guard protects nothing. A
false positive on day one is how a real protection is lost by month three.

**OPEN-30 — fold `SELECT version();` into OPEN-27 step 3. ACCEPTED.** The owner
is already connected proving the new `schema_admin` can run DDL. Free is better
than scheduled.

`btree_gist` confirmed credential-free through the Fly API is a good catch — a
recorded dependency now has evidence rather than an assumption.

**§6 — accepted as written.** A hermetic green is not evidence that a migration
applies. The local cluster is not the platform's major and not behind a pooler.
Saying so is worth more than the green.

---

## 2. The pattern is now five, and it deserves a name

`F-next/a-check-that-could-not-fail` is the third instance you named. Counting
the ones adjacent to it, today produced:

1. The D-019 counter — a number that looked like an answer.
2. The trip harness — five guards reported green while running nothing.
3. B1's tautology — `filing_date <= D AND filing_date > D`, empty by
   construction, incapable of failing.
4. The duplicate-count loop — returned 8 against 3 candidates.
5. `/healthz` — returns 200 against a database that is not there, which is why
   Row 4 is still `Never`.

**They are one failure: an instrument that cannot report the condition it exists
to detect, and whose output is indistinguishable from the healthy case.** Every
one of them failed in the favourable direction, which is why none of them
announced itself.

**Your sharpened rule is the right one and should be recorded as project
doctrine, not as a finding's footnote:** *a guard never seen red is not a guard*
was about running the trip test. **The prior requirement is that the check be
capable of failing in principle.** Trying to make a tautology go red proves the
tautology, not the system.

**And the review consequence, which is yours:** B1 survived review because it
*reads* like a negative assertion and the shape of the sentence is right. The
defect was in the logic, not the intent, and **a reviewer checking intent finds
nothing wrong.** Checking a guard means constructing the case that should trip
it — not reading it.

---

## 3. Ingest slice 1 — the universe, not the facts

**Scope: filers and filings. No XBRL facts.**

The TDD calls the XBRL tag-normalization layer the largest single piece of work
in the build. It should not be the first thing built, and it does not need to be
to prove the schema end to end.

**In:**
- `company_tickers.json` / `company_tickers_exchange.json` → `filer` rows and the
  ticker records with their validity bounds.
- EDGAR submissions metadata per CIK → `filer.current_*` with `metadata_as_of`,
  and `filing` rows with accession, form type, filing date, period of report and
  `sic_at_filing`.

**Out:** facts, concepts, taxonomy handling, TTM assembly, anything scoring-shaped.

**What this slice is for:** it is the smallest thing that exercises ruling 5 end
to end. When it lands, *which CIKs had filed a 10-K in the three years before
date D* has an answer computed from data rather than asserted from design.

---

## 4. Constraints on the EDGAR client

**D-023 governs: no silent retry on 403.** A 403 from EDGAR means the request was
refused, usually for a missing or unacceptable User-Agent, and retrying makes the
refusal worse rather than better. It fails loudly.

**Rate limiting is a first-class requirement, not a politeness.** Establish
EDGAR's current published limit and honour it with a bound you can point at, not
a sleep someone guessed.

**Establish before choosing the retrieval path:** the SEC publishes bulk archives
alongside the per-CIK endpoints. Whether the bulk route is available, current,
and appropriate here is worth ten minutes before building a crawler that makes
thousands of requests. I am not asserting what exists — establish it.

**Idempotency is the schema's, not the client's.** Re-ingesting a submission must
land on `ON CONFLICT DO NOTHING` against the real key and change nothing. Prove
that by running the slice twice and asserting row counts are identical.

---

## 5. Two things to prove, and one not to claim

**Prove the scheme assumption fails loudly.** §2.1 says an entity identifier
under any scheme other than CIK must make ingest fail rather than be coerced.
Construct that case and show it failing. An assumption stated in a comment and
never tested is the shape §2 of this document is about.

**Prove double-ingest idempotency**, as above.

**Do not claim ingest exercises A8.** If this slice — or the later fact slice —
draws from a per-CIK endpoint, the entity is whatever CIK was requested, so
`entity_cik` is trivially correct and the co-registrant case never arises. **The
schema is right and that path would not test it.** A8 and the fixture remain the
only evidence, and the report should say so rather than letting a green ingest
imply coverage.

---

## 6. Sequence

Ingest slice 1 is hermetic: built and proven against a local cluster, exactly as
0001 and the runner were. It does not touch Fly and is not gated by OPEN-25,
OPEN-27, OPEN-30 or OPEN-21.

**The run phase — slice 1 against `stockgrader-db-r1` — is gated by all four**,
as 0001's is, and for the same reasons.

Still with the owner: OPEN-27 steps 1–3 with `SELECT version();`, then OPEN-25;
B-9 under the same-sitting condition; D-019 implementation; OPEN-17; OPEN-19.
