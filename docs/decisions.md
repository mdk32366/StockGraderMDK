# Decisions — Why is it like this?

Numbered in the order resolved. Each entry names the rejected alternative and
what forced the call. Status is RULED (owner decided), PROPOSED (Planner
drafted, owner has not ruled), or OPEN (not yet decided).

---

### D-001 — The name is StockGraderMDK, everywhere
**Status:** RULED 2026-09-22 (the owner created the repository under this name)
**Choice:** Repo `StockGraderMDK`; Fly app `stockgradermdk` (Fly app names are
lowercase).
**Rejected:** "Ticker Analysis System", the name of the Claude Project where
planning began.
**Forced by:** the repo already existed. One name everywhere (Day-One Step 1),
so the Claude Project is renamed to match. The repo is not renamed.
**Note:** this supersedes the Planner's first-turn sketch, which proposed
`ticker-analysis-system`. The Builder's preflight report called this question
"D-000"; it is answered here and has no separate entry.

### D-002 — FastAPI + Postgres on Fly.io
**Status:** RULED 2026-09-22 (the owner accepted the scaffold)
**Choice:** Python 3.12 / FastAPI, with Postgres when data arrives, deployed on
Fly.io.
**Rejected:** other hosts (the owner specified Fly); a Node API (no advantage,
and it breaks parity with Sentinel and PharmFoldMDK, whose Fly operating
knowledge transfers directly).

### D-003 — API shape: /v1, X-API-Key, contract snapshot
**Status:** DELIVERED 2026-09-22 in the Keel commit (`0ac7a7d`). `/v1/meta`,
`X-API-Key` and the committed OpenAPI snapshot are live; auth verified against
the running service (401 without a key, 401 with a wrong one).
**Choice:** Versioned paths (`/v1`). A single shared key in the `X-API-Key`
header, compared in constant time, failing closed (503 if the server key is
unset). GET for single-item lookups (cacheable); POST for batch scoring and
multi-fund overlap (list bodies). The OpenAPI schema is committed as a
snapshot, and the gate fails on drift.
**Rejected:** unversioned paths (the first breaking change strands the
consumer); OAuth (overkill for one machine consumer); no contract test (KEEL:
a spec naming a producer and consumer names the test between them).

### D-004 — Test-DB safety is two-factor positive identity; hostname is never consulted
**Status:** DELIVERED 2026-09-22 in the Keel commit (`0ac7a7d`); trips B-2, B-3,
B-4, B-10 and G-3..G-6. **Owner ruling STILL NEEDED on the residual** — delivery
does not close that question. Note also that the guard's real-Postgres half is
unproven until OPEN-1 closes.
**Choice:** When `DATABASE_URL` is set, both factors are required. Factor 1 is a
typed confirmation sentence (`KEEL_TEST_DB_DISPOSABLE`) that is banned from env
files by a test. Factor 2 is the `keel_disposable_canary` table. A row-count
tripwire applies in addition. Any failure is a hard error.
**Rejected:** a hostname or port check (defeated by a tunnel: the 4,535-row
scar); a row count alone (production is near-empty early in the project, so it
would pass exactly when it matters least).
**Residual:** defeating the guard against production takes two deliberate acts:
running the canary script on production AND typing the sentence in a shell
pointed at it. **Owner: accept this residual, or add a third factor?**

### D-005 — A deploy is verified by the live build SHA, not by a green job
**Status:** DELIVERED 2026-09-22 in the Keel commit (`0ac7a7d`) and exercised on
every deploy since. Verified on `6f69a09`, `ae4e61a` and `d267f1d`, each time on
attempt 1.
**Choice:** The image bakes in `GIT_SHA`, and `/healthz` reports it. The deploy
job fails unless the live service reports the commit just shipped.
**Rejected:** trusting "deploy job succeeded" (PharmFoldMDK 3.4: a green gate
and a changed service are different claims).

---

## Open rulings (owner only)

### D-006 — What POST means; rate limiting; per-client keys
**Status:** OPEN. Read-only batch and overlap only, or does a POST also trigger
refresh or ingest? This decides the auth and rate-limit design.

### D-007 — Price data vendor and budget
**Status:** OPEN. Settles A-003 (redistribution rights). Blocks all price-derived
scoring.

### D-008 - Universe: US common stocks, US mutual funds, and US ETFs
**Status:** RULED 2026-09-22 (owner)
**Choice:** US-listed common stocks, US mutual funds, **and US ETFs**.
**Rejected:** mutual funds only -- it leaves the obvious question
("how much does my fund overlap my ETF?") unanswerable; non-US -- identifier
coverage collapses, A-002 gets materially worse, and there is no demand yet.
**Forced by:** ETFs file N-PORT, so overlap extends to them at almost no extra
cost, and fund-versus-ETF is the comparison people actually want.

### D-009 - Fly Managed Postgres, one cluster, region `sjc`
**Status:** RULED 2026-09-22. **DELIVERED** the same day -- cluster
`d1zj5omk443ryqkv` (`stockgrader-db`), basic/10 GB, status ready.
**Choice:** Fly **Managed** Postgres, a single cluster in `sjc`, with the
application database `stockgrader` created deliberately rather than using the
`fly-db` default.
**Rejected:**
- **Unmanaged Fly Postgres** -- the recovery maze that cost two hours was on that
  path, and the backup-list command was the thing we could not run.
- **DuckDB** -- better columnar analytics, but single-writer and wrong for a
  hosted API with a live consumer.
- **SQLite** -- PharmFoldMDK proved a hermetic SQLite test can pass while the
  real schema behaves differently.
- **A warehouse** -- cost and latency for no benefit at this size.
**Region:** `sjc` follows D-017. App and cluster in one region; MPG is available
there.
**Consequences realised on delivery:** F-014 (credentials printed by
`fly mpg create` and `fly mpg attach`), F-015 (`DATABASE_URL` left Staged),
F-016 (the backup command run for real), F-017 (Step 16 separation nominal).

### D-010 - The stock score is GQS v3
**Status:** RULED 2026-09-22 (owner), **with a condition that is not yet met.**
**Choice:** the owner's *Growth Quality Score TDD v3* is adopted as the
stock-side design -- its four independently ranked blocks, its integrity gate,
its `insufficient_data` fourth state, its point-in-time requirement, and its
attribution of score moves (fundamentals deteriorating versus price rising and
valuation compressing).
**Condition, binding.** **Reworded by owner ruling 7, 2026-09-23:** it read
*"five open questions in its §17"*; it now reads **"the four open questions in
its §11."** Unchanged in substance - it now points at a section that exists.
Those four are ratified, or **the build order for scoring does not issue**.
Adopting a draft without answering the questions its own author flagged is how a
draft becomes doctrine by accident.
**Superseded by GQS v4 (ruling 8):** v3 is revised to v4 grounded on this repo,
rather than ported inside a build order. §12's confirm-before-build list is
rewritten against StockGraderMDK - `alembic heads` removed (D-021 rejected
Alembic), the `finance` agent and settings-overlay items replaced with this
repo's equivalents, and §3's `place_stock_order` non-goal becomes **moot rather
than satisfied**, since no such path exists here.
**Why not port it inside a build order:** §13 refuses the document for build.
Carrying the port inside a build order would mean the refusal never formally
lifts, and **a completeness gate that is routed around once stops being a gate.**
**Current state: still refused.** See the §13 table in `testplan.md`.
**Rejected:** the Planner's first-turn placeholder component list, which was a
sketch and is superseded.
**Consequence:** A-007 becomes load-bearing. Point-in-time integrity constrains
the **first migration**, so the schema must carry it from Phase 1 whether or not
scoring is built yet -- it is unaffordable to retrofit.
**Blocking: LIFTED 2026-09-23.** A-016 is closed - the Planner has read
`TDD-growth-score.md` and `growth-model-lineage.md` in full. The reading produced
four defects (`F-next/gqs-tdd-defects`), **one of them in this entry's own
condition** (F-A, fixed by ruling 7). The variable-to-source map that came out of
it is `docs/gqs-source-map.md`. GQS covers businesses, not
funds; the fund score is a separate design -- see D-027.

### D-011 — Python 3.12 everywhere: local, CI, image
**Status:** DELIVERED 2026-09-22. 3.12.10 locally, `python-version: "3.12"` in
CI, `python:3.12-slim` in the image. `setup.ps1` as the sole sanctioned venv
path is enforced by its own hard failure, and D-012's `-SuiteOnly` refuses to
create a venv rather than become a way around it.
**Choice:** 3.12 on the workstation (installed alongside 3.11 via the `py`
launcher), in CI, and in the Docker base image.
**Rejected:** downgrading CI and the image to 3.11 to match the workstation's
current default. That lets one machine's install history set the platform
version, and the gap would reopen at the next upgrade.
**Forced by:** F-003, amended by F-005.
**Amendment (2026-09-22, from F-005):** `setup.ps1` is the ONLY sanctioned way
to create `.venv`. A venv made by hand (`python -m venv` gives 3.11, `py -m venv`
gives 3.14) is a deviation, and a green result from one is not evidence.

### D-012 — setup.ps1 gains a first-class offline suite mode
**Status:** DELIVERED 2026-09-22 in PR-3 (`d267f1d`). Trip: B-14.
**Choice:** Add `-SuiteOnly`: skip venv creation and install, verify `.venv`
exists and is 3.12, then run pytest. Hard error if either check fails. Delivered
as the **first real PR after branch protection** is on, so it goes through the
gate.
**Rejected:** changing `setup.ps1` inside the artifact before the first commit.
That churns code in an artifact the Builder has already verified, for a
convenience the manual sequence in testplan OPEN-3 covers today.
**Forced by:** F-004.

### D-013 — .ps1 files are pure ASCII AND carry a UTF-8 BOM, enforced by test
**Status:** DELIVERED in artifact v4 and live since the Keel commit (`0ac7a7d`).
Guard `test_powershell_scripts_are_safe_for_windows_powershell_5`; trips G-9,
B-9a, B-9b — each half bites alone. The parse itself is proven by D-014's job.
**Choice:** Both halves at once, with
`test_powershell_scripts_are_safe_for_windows_powershell_5` failing the gate if
either is missing. Each half was tripped independently (testplan G-9).
**Rejected:**
- (a) BOM only: an editor that strips the BOM silently re-arms any non-ASCII
  character.
- (b) ASCII only: relies on nobody ever pasting a typographic character.
- (d) Require PowerShell 7: a second Day-One install to work around two
  characters, when 5.1 is what ships with Windows.
**Forced by:** F-006.

### D-014 — CI executes setup.ps1 under Windows PowerShell 5.1
**Status:** DELIVERED 2026-09-22 in PR-3 (`d267f1d`). A-008 tested and holds
on the first run. Counter for promotion to required: see testplan D-019.
**Choice:** Add a `windows-latest` job that runs `.\setup.ps1` with
`shell: powershell` (5.1, not pwsh).
**Rejected:** relying on G-9 alone. G-9 closes this encoding class, but only
executing the sanctioned entry point proves that the entry point works.
**Depends on:** A-008.

### D-015 — Warnings are errors, with named, dated allowances
**Status:** DELIVERED 2026-09-22 in PR-3 (`d267f1d`). Trips: B-15, B-16.
Mis-specification lesson recorded as F-012.
**Choice:** `pytest.ini` gains `filterwarnings = error`, plus one `ignore`
line per F-007 warning. Each allowance carries a comment naming F-007 and the
condition that retires it.
**Rejected:**
- Leaving warnings visible but non-failing: by the tenth run they are
  background noise.
- A blanket ignore: that hides the next deprecation too.
**Proof required:** introduce a new, unallowed warning in a test and watch the
gate go red.
**Forced by:** F-007.

### D-016 — The first commit is the verified artifact, byte for byte; everything after is a PR
**Status:** DELIVERED 2026-09-22. Commit `0ac7a7d` was verified against
scaffold v4 twice — working tree before `git add`, then every committed **blob**
after, which is the check that matters because `.gitattributes` rewrites
`setup.ps1` to CRLF in the working tree while the stored blob stays LF.
**Choice:** The initial commit is scaffold v4 unchanged. Its message cites
SHA-256 `d21f51e4f056b3fe7cd587d565ef81b1f53760d8f6e65ec647cd345510f9c03f`.
Every later change, including register updates, goes through a PR and the gate.
**Rejected:** folding F-007, F-008, and the trip table into a v5 before the
first commit. That spends the verified-artifact provenance on items that block
nothing, and it asks the Builder to re-verify a fifth artifact.

### D-020 - The repo stays PUBLIC through development
**Status:** RULED 2026-09-22 (owner). Observable named 2026-09-22.
**Choice:** `StockGraderMDK` remains public for the whole build, connected to
the Planner. It goes private when the application has **completed development**.
**Rejected:** going private on the first live credential, first real user data,
or first live deploy -- the wording in KEEL-2 Step 17 and KEEL-3 line 17, now
superseded in KEEL V11 (F-013).
**Forced by:** the owner's standing rule, matching KEEL-1 Principle 10's body.

**The observable -- development is complete when ALL FOUR are true:**
1. Scores exist across the ruled universe (D-008), not a sample.
2. A portfolio can be constructed from those scores and tracked over time.
3. That tracking has run long enough to say whether the scoring system works.
4. The API is available to an external consumer -- a bot building or tracking its
   own portfolio, or watching a stock, fund or ETF.

Condition 4 is also "the first user who is not you" -- the trigger the Planner
thought would never fire. It fires.

**Two sub-rulings still OPEN, both [OWNER], and both must be answered BEFORE the
portfolio starts:**
- **How long is "long enough"?** Name a number of months now. Named afterwards,
  it becomes however long it took to get a result somebody liked.
- **What result would mean the scoring system does NOT work?** Write it before
  the data exists. Criterion 3 is a validation study, and a validation whose
  success criteria are set after the numbers arrive is a rationalisation. GQS v3
  pre-registers at the component level; this is the same discipline at the
  portfolio level.

**Consequences, recorded so nobody re-derives them:**
- The Planner keeps direct repo access for the whole build. No snapshot
  hand-carrying.
- The repo must stay free of real credentials and real user data for **months,
  not days**. The hygiene secret scan is load-bearing for the whole build.
- **Accepted risk, crossed deliberately:** the Planner's post-Keel §2 noted that
  staying public stops being near-zero risk the moment a database exists. The
  cluster now exists (D-009) and the repo is still public. The connection
  string, the recovery credential and all cached filing data live outside the
  tree, and nothing may bring them in.

### D-017 - Fly region is `sjc`
**Status:** RULED 2026-09-22
**Choice:** `sjc` for the app, and for the database cluster when D-009 creates
it.
**Rejected:** `sea` -- withdrawn by the platform, and the cause of the first
deploy failure (F-011). Latency is irrelevant for a filings-and-prices API, so
nearest-surviving-West-Coast was the only criterion that mattered.
**Binding consequence:** the D-009 cluster is created in `sjc`. An app in one
region with its cluster in another is a latency and failure-domain problem
nobody chooses on purpose.

### D-018 - Branch protection as configured
**Status:** RULED 2026-09-22
**Choice:** `main` requires a PR and the `test` check, with
`enforce_admins: true`, `required_approving_review_count: 0`, `strict: false`,
and no force pushes or deletions.
**Rejected:** requiring an approving review (nothing could ever merge for a solo
owner); `strict: true` (forces a rebase and rerun on every PR for no gain at
this size).
**Residual, stated rather than hidden:** with `strict: false`, a stale branch can
merge green and still break `main`, because the required check ran against an
older base. The post-merge `deploy` job and the live-SHA check (D-005) are what
would catch it. **Revisit both settings the day a second person can push.**

### D-019 - `windows-setup` is a required check
**Status:** **RULED 2026-09-23 (owner) - PROMOTED.** Supersedes the 2026-09-22
ruling, which held it non-required until 10 consecutive green runs. **The counter
is retired.**
**Choice:** `windows-setup` is a **required** check on `main`. **A red on Windows
blocks merge.**
**Met on:** 10 consecutive green runs, **no reds**, across five branches and four
merges to `main`. The ruling was made **on** the threshold rather than reached by
default.
**The caveat is recorded with the ruling, not against it.** Those ten runs are
ten runs of a repo with 22 tests and **almost no application code**.
`windows-setup` has not been stressed by dependency churn, and **ingest - the
next work - is exactly what stresses a Windows setup path.** That is the argument
*for* promoting now: **a check made required after the churn is one that was
proven against nothing and then made load-bearing at the moment it started to
matter.**
**Reversal path, named in advance** so it is a decision rather than a scramble:
the same settings change in reverse. **Condition: a red attributable to the
runner rather than to the repository, twice.** One is noise.
**Superseded rationale, kept:** the 2026-09-22 entry rejected promotion because
two green runs was a sample of two and a runner outage would block every merge on
a job guarding one script. That was right then; the counter is what changed it.
**What protected the entry point meanwhile:** the required `.ps1` byte guard
(G-9 / D-013), inside the required `test` job. It stays.
**IMPLEMENTATION NOT YET APPLIED.** Branch protection is a repository settings
change, not a commit, and the change was blocked at the Builder's permission
boundary. **testplan OPEN-14** carries it.
**Required context: `windows-setup (PS 5.1)`.** The promotion ruling's §2 named
`windows-setup`, which nothing ever reports; **§2 is superseded and corrected**
by `RULING-Planner-2026-09-23-...-p7-settled-p8-context-string.md` §1.1. The
error is **P-8**; the hazard is `F-next/required-check-context-name`.

### D-024 - Decision status vocabulary, and the rule that keeps it true
**Status:** PROPOSED 2026-09-22
**Choice:** the vocabulary is exactly `OPEN`, `PROPOSED`, `RULED`, `DELIVERED`,
`SUPERSEDED by D-NNN`, `REFUTED [date]`. **The PR that delivers a decision
updates that decision's status in the same PR** -- not the next one, not a
cleanup pass.
**Forced by:** D-012, D-014 and D-015 sat at `PROPOSED - deliver as a PR after
branch protection` for an hour after they were merged and live. A register that
describes the future for work already shipped is a record that no longer matches
the world, and the register is what the next reader acts on.
**Rejected:** a periodic cleanup pass. It makes staleness normal between passes,
and the window is exactly when someone reads the entry and acts on it.
**Applied retroactively in this PR** to D-012, D-014 and D-015.

### D-025 - Status vocabulary guard
**Status:** PROPOSED 2026-09-22, for PR-5, low priority
**Choice:** a test parsing every `**Status:**` line in `decisions.md`, failing on
any value outside D-024's vocabulary.
**Scope, to be stated inside the test itself:** it catches **malformed and
unknown** statuses only. **It cannot catch a status that is valid but stale** --
a `PROPOSED` entry whose work shipped yesterday passes this guard. That is what
D-024's same-PR rule is for, and that rule is a ritual enforced by people, not
by a test. The guard must not be allowed to imply otherwise; a guard that
documents a blind spot rather than closing it is an open defect, and this one
closes a different, smaller thing than it might appear to.

### D-021 - Forward-only numbered SQL migrations, run by our own runner
**Status:** RULED 2026-09-22
**Choice:** numbered, forward-only SQL migrations applied by a runner we own.
Each migration runs **in its own transaction, under a session advisory lock**,
and is followed by a **verification query** asserting that the objects it claims
to create exist and are the right shape.
**Forced by:** "the migration reported success" and "the schema changed" are
different claims - D-005's shape, applied to schema instead of deploys.
**Rejected:** Alembic with SQLAlchemy 2.0 as delivered. PharmFoldMDK section 3.1
records a migration chain that **silently rolled itself back** because a `SET`
ran before the transaction the tool owned. We can adopt it later deliberately;
we are not inheriting that failure on day one.
**Consequence:** the runner holds schema rights and the web process does not.
That is what makes D-031 possible.

### D-022 - Ingestion runs as a separate Fly process group
**Status:** RULED 2026-09-22
**Choice:** ingestion never runs inside the web process - a separate process
group or scheduled machine.
**Rejected:** background tasks in the API process. A slow or rate-limited fetch
would touch API latency, and a crashed ingest would take the API down.

### D-023 - EDGAR client rules
**Status:** RULED 2026-09-22
**Choice:** a declared User-Agent with contact details; a hard client-side rate
limit; retry with backoff on 429 and 503; and **no retry that hides a 403**.
Every fetch records source URL, retrieval timestamp, and a hash of the payload.
**Raw filings are not stored** - EDGAR is the authoritative permanent copy, and
accession plus hash makes any row re-derivable.
**Forced by:** A-004. A 403 means we have been refused, not that we should try
again. A retry that swallows it turns a policy failure into a silent data gap.

### D-027 - Fund scoring is look-through PLUS fund mechanics
**Status:** PROPOSED 2026-09-22
**Choice:** two parts, and both are required.
- **Part A, look-through quality:** each holding's GQS weighted by portfolio
  weight.
- **Part B, fund mechanics that no look-through can see:** expense ratio, loads,
  turnover and its tax drag, manager tenure, concentration.

**Why Part B is not optional:** the published research is unusually consistent
that **cost is the strongest single predictor of long-run fund outcomes**,
stronger than anything about the holdings. The same basket of excellent
businesses at 1.4% with 90% turnover, and at 0.03% buy-and-hold, are not the
same investment, and a pure look-through score cannot tell them apart. A
buy-and-hold suitability score that ignored cost would be wrong in the most
expensive possible direction.

**Four traps this design must defuse, each with a required behaviour:**
1. **Renormalisation.** Dividing by resolved weight assumes the unscored
   holdings resemble the scored ones. **Never renormalise silently.** Report the
   weighted mean **and** the share of fund weight it was computed over, in the
   same response, always.
2. **Coverage floor.** Below a stated fraction of scoreable weight the answer is
   `insufficient_data` with its reason, not a number.
3. **Date mismatch.** Holdings are quarter-lagged; stock scores are current. A
   look-through score is today's score of what they held last quarter. The
   response carries **both** dates and labels which is which. It is never
   presented as a current portfolio.
4. **Reason codes, not blanks.** Every unscored holding carries why:
   `NON_EQUITY`, `NO_FUNDAMENTALS`, `UNRESOLVED_IDENTIFIER`, `FOREIGN_LISTING`,
   and so on.

**Pre-registration required before the fund score touches real data.** The
honest null is not "does the fund score do something". It is: **does look-through
quality add anything over expense ratio and turnover alone?** Write down, before
looking, what result would mean it does not - and report that result if that is
what comes back. PharmFoldMDK section 4 applied before the fact instead of after.

### D-028 - Asset-class scope for v1: equity only
**Status:** RULED 2026-09-22
**Choice:** bonds are out of scope for this version and get their own analysis
later.
**Hard consequence that must be BUILT, not merely noted:** a fund whose
non-equity weight exceeds a stated floor returns **`insufficient_data`**, never
a stock-only score computed over the equity part. A balanced fund that is 40%
bonds is **not a fund we scored badly - it is a fund we cannot score.**
Rendering those two the same way is exactly the plausible-and-wrong shape
Principle 11 exists for.

### D-029 - Every exposed credential is replaced or rotated before Phase 2
**Status:** PROPOSED 2026-09-22. **Amended the same day from two credentials to
three.**
**Choice:** all three are treated as compromised until resolved, and all three
are resolved **before the first real data load**. The cluster holds nothing that
matters, which is what makes this cheap now and expensive later.

| Credential | How exposed | Resolution |
|---|---|---|
| `stockgradermdk` (app) | `fly mpg attach` printed it (F-014) | **Replace**, not rotate - D-031 |
| `fly-user` (recovery) | `fly mpg create` printed it (F-014) | Rotate; it is the Step 16 account |
| `probe_ro` (reader) | **supplied in a chat transcript** (F-019) | **Delete.** It has served its entire purpose |

**A rotation is not complete when the password changes. It is complete when a
request to the live service proves the new one is in use.** `/healthz` cannot
prove it, because it touches no database; the first DB-backed endpoint can.
**Order:** the application credential goes first.

**~~RULED 2026-09-23 (owner ruling 6) - closure is by destroy, not rotation.~~**
**VOID, same day.** Ruling 6 held that destroying the old cluster retires both
exposed credentials, and that this was D-029 closing by replacement. **It is not.**

**`fly mpg restore` carries the role catalogue.** `fly mpg users list
kzpwm0j1dm204nv3` returns `fly-user` (`schema_admin`), `stockgrader_app`
(`writer`) and **`stockgradermdk` (`schema_admin`)**. Both credentials
compromised on 2026-09-22 are **live on the new cluster with their original
passwords**. The destroy would retire **two copies that no longer matter**.
See `F-next/restore-carries-compromised-roles`.

**D-029 therefore has no closure path at present.** Stated in those words rather
than left implied, because it was resting entirely on ruling 6.

**What still stands:** **D-031, in full.** The app connects as `stockgrader_app`
at `writer`, verified from the connection string's own components. That was real
work and is untouched. **The defect is the residue the restore carried, not the
replacement that was made.**

**What became false:** the claim that F-017's over-privilege is not rebuilt on a
clean cluster. **There is no clean cluster** - a restore is a copy, and the
over-privileged account came across with the data.

**The risk, neither inflated nor dismissed:** the cluster is on the private
network and unreachable from the public internet. A credential alone buys nothing
without Fly organisation access, and anyone holding that does not need the
credential. **Practical probability of exploitation is low** - and it was low
this morning, which is why the deferral was sound.
**What changed is not the probability.** It is that **the register asserted
something false** - a wrong record is worse than a known risk, because nobody
re-examines it - **and the remediation acquired a deadline it did not have.**

**Remediation is gated: see `testplan.md` OPEN-25.** It is nearly free while the
databases hold no owned objects, and becomes a schema-ownership problem the
moment migration 0001 creates tables.
`probe_ro`'s resolution is unchanged - delete.

### D-030 - Credential handling, with a procedure
**Status:** PROPOSED 2026-09-22
**Choice:**
- Credentials live as Fly secrets and are consumed from the injected environment
  at runtime. Never in a repo file, never in an env file in the tree, never in a
  transcript.
- **Fly secrets are write-only.** `fly secrets list` returns names and digests;
  no command returns a value. The platform is where credentials are **put**, not
  retrieved. A human who needs one rotates it rather than looking it up.
- The exception is the Step 16 recovery credential, which lives in the password
  manager precisely because the platform will not give it back.
- Prefer `fly secrets import` from stdin over `fly secrets set KEY=value`, which
  puts the value in shell history.
- **Known offenders that print live credentials: `fly mpg create` and
  `fly mpg attach`.** Redact before relaying. `fly mpg users create` does **not**
  - it prints only name and role (F-014 amendment).

**The procedure, added because an unspecified mechanism defaults to the nearest
one - and the nearest one is chat:**
- When the Builder needs a credential, the owner writes the value to a file
  **outside the repo tree** at a fixed, named location. The Builder reads it,
  uses it, **deletes the file, and confirms the deletion in its report.**
- **No credential is ever typed into a Planner conversation** - including by the
  owner, including when the owner knows and accepts the cost.
- A credential's lifetime is the task. Mint it scoped, drop it after. Never keep
  one "in case".

**Residual, stated rather than hidden:** anything in a machine's environment is
readable by anyone who can `fly ssh console` into it. "Never printed" is a habit;
**least privilege and rotation are the controls.**

### D-031 - The application connects as a `writer`, not a `schema_admin`
**Status:** PROPOSED 2026-09-22. Evidence in hand (A-017).
**Choice:** create a new user at `writer`, attach with it, `fly secrets deploy`,
**verify against the live service**, then drop the exposed `stockgradermdk`
account. `fly-user` stays at `schema_admin` in the password manager as the Step
16 recovery account - which then means something, because the gap is real.
**Forced by:** under D-021 migrations run from the Builder, so the web process
needs **rows, not schema rights**. F-017 found both accounts at `schema_admin`,
making Step 16's separation nominal: two accounts differing only in name give
the recovery account no capability the application lacks.
**Replace rather than rotate:** closes D-029's application half and F-017's
over-privilege in one pass, and never rotates a credential in place.
**Evidence it is sufficient:** A-017, tested on the real cluster - a `writer`
can INSERT, SELECT, UPDATE and DELETE, and is refused `CREATE TABLE`
(`permission denied for schema public`) and `DROP TABLE` (`must be owner`).

### D-032 - `postgres_probe` accepts an open connection, not a DSN
**Status:** PROPOSED 2026-09-22 (Planner)
**Choice:** the probe takes a connection object, so the non-hermetic runner
obtains it however it likes.
**Forced by:** F-019. Taking a DSN means every non-hermetic run needs a
credential string in the Builder's hands, on a platform that offers no
machine-retrievable credential path.
**Note on numbering:** the Builder independently proposed a different D-032 in
the same hour. That one is renumbered **D-034**. Numbers are allocated by the
Planner; where the Builder needs one before a ruling, it proposes
`D-next/<short name>`.

### D-033 - Sequence numbers on every document, both directions
**Status:** PROPOSED 2026-09-22
**Choice:** Planner documents are numbered `P-nnn`, Builder reports `C-nnn`, and
**each document names the last document it received from the other side.**
**Forced by:** F-020. The relay is manual and lossy, and until now neither end
could tell. A gap becomes visible immediately instead of surfacing later as a
stale decision or an unanswered question.

### D-034 - Report before the next unit of work; no silent infrastructure mutation
**Status:** RULED 2026-09-22. Adopted from the Builder's proposal and renumbered
from its D-032 to resolve the collision recorded in D-032.
**Choice:** the Builder writes its report **before starting the next unit of
work**, and **every cluster mutation** - a database, a user, a secret, a schema
object - appears in a report **before anything else is done**.
**Forced by:** F-018. For code, git is the record and the commit is automatic.
For infrastructure there is no commit, so work can outrun its record and nothing
in the documents reveals it. The register is assembled from reports; a chat is
not a record.

---

## Backup strategy - B-1 to B-9

**Source:** `HANDOVER-Planner-2026-09-23-...-backup-strategy-restore-drill.md` §2,
received 2026-09-23, **as amended by**
`RULING-Planner-2026-09-23-...-backup-mechanics-section4-amended.md`.
**Status: B-1..B-8 RATIFIED by owner ruling 2, 2026-09-23** (PROPOSED -> RULED).
**B-9 APPROVED by owner ruling 3.** B-6a remains an open testplan item (OPEN-7) dated
2026-10-03. The `B-n` labels
are the Planner's. B-2, B-6 and B-8 below are the **amended** texts; the
originals were withdrawn on the Builder's evidence and are described as withdrawn
rather than deleted.

**B-1 - Automatic backups are the floor, not the plan.** The rolling schedule
covers ordinary operation. Everything below is what the schedule does not do.
**[Builder, F-next/backup-cadence-observable]** the floor is higher than assumed:
hourly incrementals, 6-hourly differentials, daily fulls, observed on this
cluster.

**B-2 - A manual full backup before any deliberate act that could destroy data.**
**AMENDED 2026-09-23** on the Builder's argument. Before a migration, a bulk
load, a cutover, a destroy: `fly mpg backup create <CLUSTER_ID> --type full`.
**Original rationale withdrawn.** It read *"the alternative is depending on
whenever the rolling schedule last happened to fire"* - but the schedule fires
hourly (F-next/backup-cadence-observable), so worst-case unguarded exposure is
~60 minutes, not an unknown. **B-2 now stands on deliberateness: a checkpoint you
took is a recovery point you can name**, and an hour of a bulk load is a real
loss.

**B-3 - A manual full backup immediately after a cutover.**
**Rationale REPLACED 2026-09-23**, exactly as B-2's was and by the same argument.
The original read *"a restored cluster has no lineage until one is made or the
schedule fires, and the window between those is unguarded."* **Observed: the
schedule took a full at 16:00:17Z, roughly six minutes after the restored cluster
went ready** (`F-next/restored-cluster-joins-the-schedule-immediately`). The
window is ~6 minutes, not open-ended.
**B-3 stands on deliberateness, not absence:** a checkpoint you took is a
recovery point you can **name**, and the first act after a cutover is when you
most want a named one. Restore builds a new cluster and backup history does not
follow it - that part is unchanged and true.

**B-4 - A backup that exists is not a backup that restores.** Recovery table row
4 stays **Never** until a restore is driven end to end including cutover. Re-run
after the ticker load, when row counts make the data half meaningful.

**B-5 - Recovery is not finished when the data comes back.** It is finished when
the app points at the new cluster and a live request proves it: `fly mpg attach`,
**then** `fly secrets deploy`, then verify. F-015 is the scar.

**B-6 - Retention is whatever chains still have a living root.**
**REWRITTEN 2026-09-23.** The original read *"10-day retention is an expiry, and
expiry is silent"* and assumed ten days of hourly recovery points. That is not
the shape. **Backup IDs are chains** - an incremental or differential names the
full it is rooted in (`<FULL>_<CHILD>`) and is **not independently restorable**.
**The recovery horizon is bounded by the oldest *full* backup still present, not
by the oldest listed ID.**
The silence clause survives: nothing warns that a recovery point has aged out,
and `fly mpg backup list <CLUSTER_ID> --all` is the only way to know. Without
`--all` it shows 24 hours.

**B-6a - OPEN ITEM, dated.** Whether a full's children expire with it is
**unverified**. `20260922-192041F` should age out around 2026-10-02; running
`fly mpg backup list d1zj5omk443ryqkv --all` on **2026-10-03** answers it for the
cost of one read-only command. Tracked as **testplan OPEN-7**. Flagged rather than
claimed, because this is the class of thing discovered while you need it.

**B-7 - Off-platform copies are not required today, and the condition that
requires them is written down.** Everything in `stockgrader` is rebuildable by
re-running the loader. The first write that is not - anything user-owned,
anything whose loss is not fixed by a re-run - makes an off-platform dump
mandatory. Same tripwire that ends the credential deferral.

**B-8 - `stockgrader_scratch` is never a reason to restore.**
**REWRITTEN 2026-09-23.** The original said scratch was *"explicitly out of
scope... not backed up on purpose."* **That claimed a platform behaviour that
does not exist.** Backups are **cluster-scoped**; scratch lives on the cluster
and is therefore backed up, and nothing in the listing distinguishes the two
databases. The intent survives unchanged - scratch carries the canary, which
marks it disposable, and it is never a reason to restore anything - but the
wording must not assert an exclusion the platform does not offer.

**B-8a - A cluster restore brings scratch across, canary included.** This is the
good direction: the disposability marker travels with the database it marks, so
`postgres_probe` behaves identically on the restored cluster. Drill step 5
therefore **expects** scratch to be present; its absence is the surprise.

**B-9 - APPROVED 2026-09-23 (owner ruling 3): measure the PITR window while it is free.**
`--pitr-time` requires a recovery window no command reports
(F-next/pitr-available-window-invisible; testplan OPEN-8) - a guess validated only by attempting
it, which is F-015's shape. **An invisible property can be made visible by one
experiment:** a PITR restore at a chosen timestamp either succeeds or is refused,
and **the refusal names the boundary.** Against a cluster holding nothing, on a
day nothing is at stake, that is a cheap measurement.
**Cost, stated:** a restored cluster is provisioned asynchronously and billed
separately - real money for as long as it exists - and is destroyed immediately
after the answer is recorded.
**APPROVED.** Runs *after* the drill completes, **never interleaved**. The
measured boundary is the finding - *a refusal names it as usefully as a success.*
**CONDITION, hardened 2026-09-23 from an agreement into a gate:** **B-9 does not
start unless there is time to finish it, destroy included.** The probe cluster is
created, the window recorded, and the cluster **destroyed in the same sitting**,
by the owner, before the session ends. **If the session cannot hold all three,
B-9 does not begin.**
**The reason is two clusters away and already running.** The instinct that says
*leave it, it costs little* is visibly what produced the PharmFoldMDK orphans -
one of them a restore of a restore, five weeks apart, named by timestamps the
platform chose (`F-next/orphaned-restore-clusters-already-exist`). OPEN-6 marks
those out of scope and that remains true; **it does not make the pattern someone
else's.**

**Platform mechanics established 2026-09-23 (read-only, §3):** `fly mpg backup`
exposes only `create` and `list`. There is **no command to configure cadence or
retention** - confirmed against the binary, not just the docs. `fly mpg restore`
supports both `--backup-id` and `--pitr-time`, plus `-n/--name`. `fly mpg destroy`
takes `-y`. See F-next/pitr-available-window-invisible and
F-next/restore-name-flag.


---

## Owner rulings, 2026-09-23 - data and model

**Source:** `RULING-RECORD-2026-09-23-StockGraderMDK-owner-rulings.md`,
**revision of 07:32** (delivered as `... (1).md`), which supersedes the 07:29
version. Thirteen rulings: **twelve ruled**, one recorded as a deferral rather
than an answer - *which is itself the owner's ruling on how that question is
handled.* Rulings 11 and 13 were pending in the 07:29 version and are ruled here.
Drill and infrastructure rulings (1, 2, 3, 6) are applied in place above; the
data and model rulings are recorded here.

### D-next/cutover-and-stay - Ruling 1: cutover-and-stay. RULED.
`stockgrader-db-r1` becomes the live cluster and today's ticker load goes onto
it. The amended §4 runs as written.

### D-next/sourcing-policy - Ruling 4: SEC is one source among several. RULED.
The TDD's §2 goal 1 (*"from SEC filings only"*) and §5.1's single-source framing
are **corrected in v4**. Data is taken where it is available.
**This is a ruling on sourcing policy, not a vendor selection.** The price vendor
is **still unchosen**, and the deciding question is **delisted coverage** - a
vendor that drops dead names **reintroduces survivorship bias through a door the
universe fix (ruling 5) just closed.** Tiingo and EODHD both need that question
put to them directly before either is picked. Tracked as **testplan OPEN-9**.

### D-next/universe-from-filings - Ruling 5: universe derived from filing history. RULED.
The historical universe comes from **the fact store's own filing record**, not
from `company_tickers.json`. The ticker files serve as the **current-day
identifier crosswalk only.**
**Constrains the first migration:** the fact store carries **filing dates and
accessions from the start** - which §5.1 already required for a different reason.
This is the same class of constraint as D-010's point-in-time requirement:
unaffordable to retrofit.

### D-next/wacc-flat-v1 - Ruling 9: §11.3 WACC flat rate for v1. RULED.
**Condition, binding:** the ROIC-WACC spread is **never surfaced as an absolute
figure** while the flat rate is in force. It is defensible for a **relative
ranking** and indefensible as an absolute number, and the condition is what keeps
the two apart.

### D-next/size-tilt-default-off - Ruling 10: §11.4 size tilt available, default off. RULED.
Enabling it is a **deliberate act** rather than a hidden thumb on the scale.

### D-next/rd-capitalization - Ruling 12: §11.1 R&D capitalization. DEFERRED, NOT RULED.
The owner agreed it warrants a dedicated session. **§11.1 therefore remains an
open question, and §5.4 with it.** §13 continues to refuse the TDD for build on
those two grounds.
**Recorded as a deferral, not an answer, deliberately** - so that no later reader
mistakes agreement-to-defer for a ruling. The deferral **is** the owner's ruling
on how the question is handled.
**Obligation attached by the owner:** the deferral carries forward into a
**closeout and prework document** for its dedicated session, **not into memory.**
That document names what §11.1 has to decide - capitalize or unadjusted GAAP;
if capitalized, what useful life - what it would reorder, and what evidence would
settle it, **so the session opens on a prepared question rather than on a
re-derivation of why the question is hard.**

### D-next/altman-z-prime - Ruling 11: Altman variant. RULED: Z'.
**Z'** - the private-firm form, **book value of equity in the fourth term.**
The disqualifier does not move with the share price.
**Reason recorded, per the owner's instruction:** TDD §3 names price and
technical signals a non-goal on the grounds that including them **quietly
converts a hold model into a trading model.** An integrity gate built on market
value of equity would disqualify a company on a day its fundamentals did not
change - **that failure in its least visible form, inside a gate rather than
inside a block.**
**Chosen for that reason and not for sourcing.** Ruling 4 means market equity is
available, so this is a design choice made **with the alternative in hand**,
which is the only kind worth recording.

### D-next/sector-archetypes - Ruling 13: §11.2 sector granularity. RULED: option (c).
**Lynch-style archetypes with per-archetype metric sets**, with an explicit
fallback. Two consequences carry into v4, **neither of them objections**:

**1. Archetype assignment becomes its own computed thing.** Fast growers,
stalwarts, cyclicals, turnarounds and asset plays are **not derivable from SIC** -
SIC says what industry a company is *in*, not which of Lynch's five it *behaves
like*. The classifier needs its own definition, its own `insufficient_data` path
for companies fitting none cleanly, and **its own place in the output**: a reader
who cannot see which archetype was assigned cannot evaluate the sector-relative
rank that followed from it.

**2. It is partly circular, and the circularity needs stating rather than
solving.** Classification draws on growth stability, margin behaviour and asset
intensity - **the same fundamentals the blocks then score.** Tolerable if the
classifier is **specified independently and frozen before scoring runs**; a quiet
disaster if it is **tuned until the rankings look right.**

**Fallback, made operational.** The owner's *"if we find we need to change that
later, we can"* **only fires if something is watching for it.** §11.2 falls back
to **SIC-as-is** if either holds:
- the archetype classifier is still unspecified when **every other §13 condition
  has cleared**, or
- a hand-check finds it assigns archetypes the owner **disagrees with more often
  than agrees**.

Recorded as **testplan OPEN-11** so the fallback has a trigger rather than a hope.

### D-next/delivery-manifest - One manifest per delivery, numbered; continuity is the guard
**Status:** ADOPTED 2026-09-23, **AMENDED the same day** by
`RULING-Planner-2026-09-23-...-manifest-scheme-and-pr6.md` §2.
**Choice:** every Planner delivery carries a manifest, and the Builder
**reconciles what arrived against it before applying anything.**
- A document **not on the manifest was not issued by the Planner.**
- A manifest entry with **nothing beside it is a loss**, detected at delivery
  rather than at citation.
- **A revision gets a new filename and says so in the body**, naming what it
  supersedes and what changed.

**Naming: `MANIFEST-Planner-<date>-D<n>.md`, one per delivery, numbered by
delivery and never revised by date.** The r/r2 chain was already awkward and
**would have become the same-name problem again by the third revision of a single
day's manifest** - the control reproducing the defect it was written to catch.

**Each manifest carries:**
- the documents in **its own delivery** only
- the **previous manifest as an entry, by name**
- a **document count** for the delivery
- issue times where recorded, and the words *not recorded* where not - *a blank
  reads as an absence of the document rather than of the timestamp*

**Continuity is the guard, not self-reference.** A manifest that lists itself
still **cannot report its own absence if it never arrives.** Each manifest naming
the previous one means a missing manifest appears as a **gap in the next**. The
document count is cheap redundancy alongside it.
**Counting rule - SETTLED 2026-09-23 (P-6, P-7), the Builder's reading adopted:**
count new documents in the delivery **including the manifest**, **excluding** the
carried-forward previous-manifest entry. Cumulative figures count every manifest.
*The manifest is a document that can be lost - D4 proved it is the loss that
matters most, because it takes the record of everything else with it. A count
excluding it would disagree with the disk for precisely the artifact whose
absence is hardest to detect.*
Without this the cumulative **inflates by one per delivery** - an error that
grows rather than staying constant, which is the version that eventually
persuades someone. See `F-next/manifest-count-double-counts` and P-6.

**Re-sends - sub-rule added 2026-09-23 (D6).** A re-sent document is **listed and
marked as a re-send, not counted as newly issued** - it was counted when first
issued, and counting it again would inflate the issued figure and **break the
comparison with the disk count that just located D4.**
Re-sends **keep their original filename and content.** This is **not** a
`same-name-revision` defect: that was a *changed* document reusing an identity.
**An unchanged document keeping its identity is what identity is for.**

**Forced by:** three relay defects in two days by three distinct mechanisms -
F-020 (lost both directions), `F-next/relay-loss-recurrence` (lost, detected only
by a later citation), `F-next/same-name-revision` (silently superseded under the
same filename). **D-033's sequence numbers catch the first. Nothing caught the
third, because nothing was absent.**
**Relationship to D-033:** complementary, not a replacement. D-033 numbers
documents so a gap is visible; the manifest makes it visible **at delivery**.
Both stay.
**Reciprocal, Builder-adopted:** Code deliveries carry a manifest too. D-033
already numbers both directions, and both F-020 losses went one way each - **a
rule that guards one direction guards whichever direction failed most recently.**
**Today's deliveries:** D1 (first manifest), D2 (its r2), D3. Retroactive, and
**nothing is renamed** - the mapping is stated in D3.
**Reconciliations to date:** D1 7 entries, D2 9, D3 3. One predicted absence,
confirmed three times. Nothing unaccounted. See `F-next/manifest-adopted`.
