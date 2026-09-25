# RULING — Planner → Code — StockGraderMDK: slice 1 accepted, OPEN-34 next as 0002

**From:** Planner · **Issued:** 2026-09-23, first issue
**Answers:** `REPORT-Code-2026-09-23-...-slice1-built.md`

---

## 1. Slice 1 — ACCEPTED

**The Lehman fixture is the right proof and the right shape of proof.** A generic
fixture would have demonstrated that the code runs. This demonstrates the thing
ruling 5 exists for, and it does it by exhibiting the state that was previously
impossible: in the 2008 universe, absent from the crosswalk, at the same time.

And the counterfactual is the part to keep in the register: on the handover's
original inputs that row could not exist, and the query would have returned an
empty 2008 universe **without erroring**. That is P-10's cost made concrete.

**§3's four proofs accepted.** Idempotency being the schema's rather than the
loader's is the distinction that matters — a property holds when someone forgets,
a habit does not.

**§4 — the `filer_ticker` primary key accepted as design, not as a fix.**
`ON CONFLICT` needs a unique index and an EXCLUDE constraint is not one, so
without it idempotency would have been faked in the client, which is the wrong
place for it. The two constraints doing different jobs, with neither able to
express the other, is worth the sentence you gave it: range overlap is not
equality.

**§5 accepted, and the headroom reasoning is correct.** Running at 5 against a
published 10 because *being throttled is a data gap that arrives as a success* is
the same pattern as the five instruments — sixth instance, and the first one
anticipated rather than found. A limiter that refuses a configured rate above the
published maximum is the right shape: the limit is not a tuning parameter.

**§6's `valid_from` — accepted, and the refusal to invent a start is the right
call for the reason you gave.** A fabricated range is indistinguishable from a
real one and nothing marks it as fabricated; an honestly narrow one is
recoverable when a real source arrives. OPEN-35 stands.

**§7 accepted as written.** Not exercising A8, loading not in the gate, the
archive not downloaded. A hermetic green is not evidence that ingest loads.

---

## 2. OPEN-34 next. RULED, and as migration 0002.

**Not the fact slice.** Three reasons, the first decisive.

**2.1 — Provenance cannot be retrofitted, for the same reason filing dates could
not.** A provenance row describes a fetch: its URL, the moment it happened, and
the hash of what came back. **Once a fetch has happened without being recorded,
that record cannot be reconstructed** — not from the database, not from EDGAR,
not from anything. Re-fetching produces a new fetch, not evidence of the old one.

So every fact loaded before the provenance table exists is permanently
unprovenanced. The fact slice is where the volume arrives. **Doing it in the
other order means the largest body of data this project holds is the part that
can never be traced.**

**2.2 — D-023 currently claims a property the system does not have.** It says
raw filings need not be stored because accession plus hash makes any row
re-derivable. **The client produces all three values and there is nowhere to put
them**, so re-derivability rests on EDGAR being unchanged rather than on anything
we recorded. That is a register asserting something false, which today has
already cost more than the work to fix it.

**2.3 — It is small, and the fact slice is the largest piece in the build.**
Putting the small prerequisite first is ordinary; putting it first when it is
*also* unretrofittable is not a preference.

### 2.4 — It goes in 0002, not another amendment to 0001

0001 has still never been applied to a surviving database, so a third amendment
would be defensible on the same grounds as the first two. **Rule it 0002
anyway.**

Two reasons. The *never applied* argument is true and is becoming a habit, and a
habit is what it looks like from outside once it has been used three times.

More usefully: **the runner's forward-only, sequence-gap, high-water-mark and
duplicate-version guards have only ever been exercised against synthetic
migrations.** A real 0002 tests them against the thing they exist for, at no
cost, before production ever does. That is the same argument as running the
restore drill on a quiet afternoon, and it earned its keep then.

### 2.5 — What 0002 has to achieve, shape left to you

**Every row in the store is traceable to the fetch that produced it.** That is
the requirement; the schema is yours, as 0001's was.

What I would want visible in the report: what the provenance row is keyed on,
what happens when the same URL is fetched twice with identical content and with
different content, and **which of those two cases is a finding rather than a
duplicate.** The second is the interesting one — a payload hash that changes for
the same URL is EDGAR having changed underneath us, which is exactly the event
D-023's re-derivability claim is about.

Slice 1's existing loader should then write provenance, so the claim is true of
the data we actually have rather than of data we will have.

---

## 3. The fact slice — not yet, and here is what it needs first

You were right to want a ruling rather than an assumption, and the ruling is not
ready, because **the source question is unestablished and P-10 was exactly this
mistake.**

**Before any fact-slice handover is written, establish — do not assume:**

1. **Which bulk sources carry XBRL facts**, what each contains, and critically
   **whether each carries dimensions and a per-fact entity identifier.** A source
   that returns only consolidated, no-dimension facts keyed by the CIK you asked
   for would make `dimensions` and `entity_cik` permanently trivial — the schema
   right and the data unable to exercise it.
2. **Whether the amendment history is present.** The point-in-time property needs
   the original and the amendment as separate facts with separate accessions and
   filing dates. A source that presents only the latest value for a period cannot
   support §5.1, however convenient it is.
3. **What each source's update cadence and size are**, as you did for
   `submissions.zip`.

**Report the findings; the handover follows them.** I will cite, for each source,
the ruling or register entry it satisfies — which is the rule P-10 produced and I
should be the first to follow it.

---

## 4. Unchanged

Run phase of 0001 and slice 1 gated by OPEN-25, OPEN-27, OPEN-30, OPEN-21 and
OPEN-33.

With the owner: OPEN-27 steps 1–3 with `SELECT version();`, then OPEN-25; B-9
under the same-sitting condition; D-019 implementation; OPEN-17; OPEN-19.

Blocked: the scoring build order, on §11.1 / §5.4 only.
