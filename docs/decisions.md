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
**Status:** PROPOSED
**Choice:** Versioned paths (`/v1`). A single shared key in the `X-API-Key`
header, compared in constant time, failing closed (503 if the server key is
unset). GET for single-item lookups (cacheable); POST for batch scoring and
multi-fund overlap (list bodies). The OpenAPI schema is committed as a
snapshot, and the gate fails on drift.
**Rejected:** unversioned paths (the first breaking change strands the
consumer); OAuth (overkill for one machine consumer); no contract test (KEEL:
a spec naming a producer and consumer names the test between them).

### D-004 — Test-DB safety is two-factor positive identity; hostname is never consulted
**Status:** PROPOSED. **Owner ruling needed on the residual.**
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
**Status:** PROPOSED
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
**Status:** PROPOSED
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
**Status:** PROPOSED
**Choice:** Add `-SuiteOnly`: skip venv creation and install, verify `.venv`
exists and is 3.12, then run pytest. Hard error if either check fails. Delivered
as the **first real PR after branch protection** is on, so it goes through the
gate.
**Rejected:** changing `setup.ps1` inside the artifact before the first commit.
That churns code in an artifact the Builder has already verified, for a
convenience the manual sequence in testplan OPEN-3 covers today.
**Forced by:** F-004.

### D-013 — .ps1 files are pure ASCII AND carry a UTF-8 BOM, enforced by test
**Status:** PROPOSED. Applied in v4 because Step 3 is blocked without a fix.
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
**Status:** PROPOSED. Deliver as a PR after branch protection, alongside
D-012.
**Choice:** Add a `windows-latest` job that runs `.\setup.ps1` with
`shell: powershell` (5.1, not pwsh).
**Rejected:** relying on G-9 alone. G-9 closes this encoding class, but only
executing the sanctioned entry point proves that the entry point works.
**Depends on:** A-008.
