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
**Condition, binding:** GQS v3's own header says it is a draft with **five open
questions in its §17 requiring owner ratification before a build order**. Those
five are ratified, or **the build order for scoring does not issue**. Adopting a
draft without answering the questions its own author flagged is how a draft
becomes doctrine by accident.
**Rejected:** the Planner's first-turn placeholder component list, which was a
sketch and is superseded.
**Consequence:** A-007 becomes load-bearing. Point-in-time integrity constrains
the **first migration**, so the schema must carry it from Phase 1 whether or not
scoring is built yet -- it is unaffordable to retrofit.
**Blocking:** see **A-016**. The Planner has not read GQS v3 or
`docs/finance/growth-model-lineage.md`; everything above is taken from the
Builder's summary, and a summary is not knowing (P8). GQS covers businesses, not
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

### D-019 - `windows-setup` stays non-required until 10 consecutive green runs
**Status:** RULED 2026-09-22
**Choice:** the D-014 job runs on every PR but is **not** a required check.
Promotion is an owner ruling once it has been green on **10 consecutive runs**,
counted in `testplan.md`.
**Rejected:** promoting it now. Two green runs was a sample of two, and a
Windows-runner outage would block every merge on a job that guards one script.
**What protects the entry point meanwhile:** the required `.ps1` byte guard
(G-9 / D-013), which runs inside the required `test` job.

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

## Backup strategy - B-1 to B-8

**Source:** `HANDOVER-Planner-2026-09-23-...-backup-strategy-restore-drill.md` §2,
received 2026-09-23. **Status: PROPOSED.** Recorded here verbatim in substance so
the register holds them; the `B-n` labels are the Planner's and numbers are the
Planner's to assign (D-032 note). Builder annotations are marked **[Builder]**.

**B-1 - Automatic backups are the floor, not the plan.** The rolling schedule
covers ordinary operation. Everything below is what the schedule does not do.
**[Builder, F-next/backup-cadence-observable]** the floor is higher than assumed:
hourly incrementals, 6-hourly differentials, daily fulls, observed on this
cluster.

**B-2 - A manual full backup before any deliberate act that could destroy data.**
Before a migration, a bulk load, a cutover, a destroy.
`fly mpg backup create <CLUSTER_ID> --type full`.
**[Builder]** rationale amended: the schedule's worst case is ~60 minutes, not
"unknown". B-2 stands on deliberateness - a checkpoint you took is a recovery
point you can name - not on the schedule's absence.

**B-3 - A manual full backup immediately after a cutover.** Restore builds a new
cluster and backup history does not follow it. A restored cluster has no lineage
until one is made or the schedule fires.

**B-4 - A backup that exists is not a backup that restores.** Recovery table row
4 stays **Never** until a restore is driven end to end including cutover. Re-run
after the ticker load, when row counts make the data half meaningful.

**B-5 - Recovery is not finished when the data comes back.** It is finished when
the app points at the new cluster and a live request proves it: `fly mpg attach`,
**then** `fly secrets deploy`, then verify. F-015 is the scar.

**B-6 - 10-day retention is an expiry, and expiry is silent.** Nothing warns that
a recovery point has aged out. `fly mpg backup list <CLUSTER_ID> --all` is the
only way to know; without `--all` it shows 24 hours.
**[Builder]** backup IDs are **chains** (`<FULL>_<CHILD>`), so expiry of a full
plausibly expires its dependents. Unverified. Retention is "chains with a living
root," not "10 days of hourly points."

**B-7 - Off-platform copies are not required today, and the condition that
requires them is written down.** Everything in `stockgrader` is rebuildable by
re-running the loader. The first write that is not - anything user-owned,
anything whose loss is not fixed by a re-run - makes an off-platform dump
mandatory. Same tripwire that ends the credential deferral.

**B-8 - `stockgrader_scratch` is explicitly out of scope.** It carries the canary,
which marks it disposable. Not backed up on purpose; not a reason to restore.

**Platform mechanics established 2026-09-23 (read-only, §3):** `fly mpg backup`
exposes only `create` and `list`. There is **no command to configure cadence or
retention** - confirmed against the binary, not just the docs. `fly mpg restore`
supports both `--backup-id` and `--pitr-time`, plus `-n/--name`. `fly mpg destroy`
takes `-y`. See F-next/pitr-available-window-invisible and
F-next/restore-name-flag.
