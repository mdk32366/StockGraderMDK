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

### D-008 — Universe
**Status:** OPEN. US only? Include ETFs? ETFs file N-PORT, so overlap extends to
them nearly for free.

### D-009 — Fly Postgres flavor (managed vs unmanaged)
**Status:** OPEN. Decides the backup-list command and the recovery-credential
procedure (architecture.md, Recovery access).

### D-010 — Score framing and pre-registration
**Status:** OPEN. The output is a score, not a recommendation. Before any score
runs on real data, write down: the components and weights; what the score
predicts, over what horizon; the result that would mean it does not work; and
how survivorship bias is handled (dead funds and delisted stocks included).
**Candidate:** the owner's *Growth Quality Score TDD v3* (2026-09-09, status
"draft, not ready to build", five open questions in its §17) appears to already
contain the stock-side pre-registration. The Builder found it on the workstation
(preflight report §5). The Planner has not read it. Its declared axiom source,
`docs/finance/growth-model-lineage.md`, has not been located. GQS covers
businesses, not funds, so the fund score stays a separate design either way.
If adopted, A-007 becomes load-bearing and constrains the first migration.

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
**Status:** RULED 2026-09-22 (owner ruling)
**Choice:** `StockGraderMDK` remains public for the whole build, connected to
the Planner. It goes private when the application has **completed
development**.
**Rejected:** going private on the first live credential, first real user data,
or first live deploy -- the wording in KEEL-2 Step 17 and KEEL-3 line 17. That
wording is superseded (F-013).
**Forced by:** the owner's standing rule, which matches KEEL-1 Principle 10's
body ("private once the project is production-stable") and contradicts the two
checklists.
**Consequences, recorded so nobody re-derives them:**
- The Planner keeps direct repo access for the whole build. No snapshot
  hand-carrying.
- The repo must stay free of real credentials and real user data for **months,
  not days**. The hygiene secret scan is therefore load-bearing for the whole
  build, not a day-one formality.
- When the database arrives (D-009), the connection string, the recovery
  credential, and any cached filing data all land while the repo is public.
  None of them may touch the tree.
**Open, [OWNER]:** "completed development" is a sentence, not a mechanism. Where
a specification names a stopping point, it must name the thing that stops. The
observable is not yet named. Candidates, none ruled: the first real
(non-synthetic) API user other than the owner; the first stored data that cannot
be rebuilt from public sources; or an owner declaration recorded as a dated
D-entry.

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

