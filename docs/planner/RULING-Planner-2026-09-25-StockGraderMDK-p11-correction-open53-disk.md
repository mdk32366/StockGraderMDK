# RULING — Planner → Code — StockGraderMDK: P-11 correction, and OPEN-53 framed for disk

**From:** Planner · **Issued:** 2026-09-25, first issue
**Answers:** `REPORT-Code-2026-09-25-...-tier1-does-not-fit.md`
**Corrects:** §2 of
`HANDOVER-Planner-2026-09-24-...-open53-ruled-revised-orders.md`

---

## 1. P-11 — I called two clusters idle on evidence that established only that
## they exist. Correct this before anything acts on it.

**The claim to strike: "the two PharmFoldMDK orphans."** And with it "~$120/month
of idle spend" and "destroying the three idle clusters pays for the disk three
times over."

**What the sweep actually established:** four clusters, ready, Basic, billing.
Two are ours — `stockgrader-db-r1` live, `stockgrader-db` deliberately empty.
**The other two are attached to other projects and their status is unknown.**

**One of them is named `sentinel-holy-rain-4562 restored 2026-08-17…` and is
attached to `sentinel…`.** Sentinel is a live project. **That cluster may be
Sentinel's production database**, restored at some point and in use ever since.
Nothing in the listing distinguishes that from an orphan.

**And we already know why nothing can.** Your own finding: the ATTACHED APPS
column records which clusters have ever been attached and not detached — **it
does not say what an app is using.** That was recorded as a credential-era
finding. It applies identically here, and I repeated Code's word "orphan" without
applying it.

**Operational consequence, stated plainly: do not destroy either non-StockGrader
cluster, and do not record them as idle.** A cost argument that ends in *destroy
the three idle clusters* is one action away from deleting a live production
database on the strength of a name in a listing.

**Recorded as P-11:** the Planner asserted status from an artifact already
established as non-authoritative, in a document that then propagated the claim
into a cost argument. Same shape as P-10 — a source consulted without checking it
against a finding already in the register.

### 1.1 What survives the correction

**The mechanism is untouched and it is the part that mattered.** Each MPG cluster
carries its own plan fee, so an empty cluster costs about $38/month before
storage. `F-next/cluster-plan-fee-is-per-cluster` stands.

**And the argument still works on the one cluster we can vouch for.**
`stockgrader-db` is ours, deliberately empty, and costs roughly **$41/month**.
**That alone more than covers the ~$38/month the disk increase needs.** The
inversion you identified in §5.2 holds without touching anyone else's
infrastructure.

**The other two are a question for PharmFoldMDK's and Sentinel's own registers**
— which cluster did each project cut over to. If those registers answer it, the
answer is a document read. If they don't, that gap is the finding, and it is
theirs.

---

## 2. §5 accepted — the concept lever does not have the range

**Tier 1 retains 91.5%; ~114 GB against 15 GB; still 7.6× over. The top five tags
are already 16.7%.** Fitting means three or four concepts, and GQS needs dozens.

**D23 §4.1 was wrong and the reason is worth recording accurately:** the
reasoning was sound and the distribution was not what it assumed. **The tag curve
is flatter than a short allowlist needs.** That is a fact about XBRL, not an
error in the argument — and it was only knowable by measuring.

**§5.1's table is the register entry.** Every lever priced, each removed by a
number rather than an opinion. **And the principled refusal of dimension
narrowing cost nothing**, because it would have left ~49 GB anyway. Worth keeping
explicitly: a principle that also happened to be free is the cheapest kind of
evidence that the principle was not doing the work.

---

## 3. §2, §3, §4 — the establishments

**OPEN-48 answered from documentation** — `version = adsh` marks an extension,
documented rather than heuristic. That is §4's rule satisfied properly.

**My prediction was wrong, in the direction the order was designed to catch.**
D24 §4.1 said early quarters plausibly carry a higher extension share. Measured:
7.3% in 2015q2, 8.5% in 2026q2. Filers extend slightly *more* over time.

**The two-quarter instruction is what made the stability claim supportable**, and
had one quarter been measured the number would have been right and the claim
unsupported. That distinction — a correct figure with an unsupported
generalisation — is the one this project keeps finding.

**OPEN-49 — `segments` is not truncated**, established by the right test: a hard
cap produces a spike at one exact length, and there is none, with different
maxima in the two quarters. **And your closing distinction is the important
half:** "no cases found" and "the rule is unnecessary" are different claims. The
refuse-rather-than-default-to-`'{}'` guard stays.

**OPEN-50 — 0 failures across 15,926 submissions.** The 100%-refusal scenario
does not arise, and §3's cross-check between the two SEC products remains
meaningful rather than being swamped by a formatting artifact.

---

## 4. §7 — `the-first-case-to-present-is-not-a-sample`, now three

Accepted as doctrine on three instances, and the third being **the Planner's
prediction rather than the Builder's sample** is what makes it general rather
than a note about sampling method.

> The first case is selected by encounter order, not representativeness, and
> encounter order correlates with nothing.

Each reversal cost one query. **Count the population before recommending the
handling.**

---

## 5. OPEN-53 — with the owner, and two things to establish first

Disk is the only lever with 8× in it. Before the owner commits, two things are
measurable and neither costs money.

**5.1 — Can provisioned storage be increased later, and does it grow
automatically?** Fly documents storage growth as monitored and managed
automatically, and storage is billed on **provisioned** rather than used. If it
can be raised in place, under-provisioning is recoverable and over-provisioning
is money spent on empty space. **Establish before choosing a figure**, because
the right number depends on which mistake is cheap.

**5.2 — The RAM question, measured before it is paid for.** Load enough quarters
locally to build a `fact_one_per_filing` of realistic size against constrained
memory, and time it.

**State the caveat with the result:** a local host's page cache is not
constrained even when Postgres's is, so **the simulation will be optimistic**. It
can prove Basic is inadequate; it cannot prove Basic is sufficient. That
asymmetry is worth writing next to the number, because a green result here is
weaker than it looks.

**5.3 — And note what the drill now costs.** B-4 re-runs the restore drill after
the ticker load. At ~114 GB that produces a second cluster of the same size —
plan fee plus storage — for as long as it exists. **B-9's same-sitting destroy
condition applies with more force**, and the drill should be scheduled when
someone can see it through to the destroy.

---

## 6. 0003 proceeds

Independent of all of the above and needed under every option, as D24 §5 said.
Provenance on `fact`, A5's enumeration inverted to an exclusion list with reasons
inline, OPEN-55's quarantine table.
