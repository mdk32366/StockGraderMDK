# Findings — How do we know?

Every finding names the artifact it came from and its sample size. If the
artifact can't be named, it is a belief and belongs in assumptions.md.

---

### F-001 — The repository was public and empty when the scaffold was built
**Date:** 2026-09-22 · **By:** Planner
**Claim:** `github.com/mdk32366/StockGraderMDK` accepted an unauthenticated
clone and held no commits, so it is public, and there was nothing to merge the
scaffold with.
**Artifact:** output of `git clone https://github.com/mdk32366/StockGraderMDK.git`
with no credentials: *"warning: You appear to have cloned an empty repository."*
Reproducible by anyone. The first commit hash supersedes it as the "before"
marker.
**Sample:** 1.

### F-002 — The hermetic suite passes, and every guard in it has been seen to go red
**Date:** 2026-09-22 · **By:** Planner, in its own Linux container (Python 3.12.3)
**Claim:** 21/21 tests pass in about 0.3 s with no database and no secrets. Each
guard was then deliberately broken and went red as a **failure**, not an error;
see testplan.md G-1 to G-8.
**Artifact:** pytest summary lines captured in the Planner session. **This
environment is not reachable by the owner.** The claim stands only once
reproduced on the owner's machine (testplan OPEN-3). Until then, treat it as
"passed elsewhere."
**Amended (v4):** the tree is now 22 tests. F-006 added the `.ps1` guard. The
number that counts is the Builder's own run.
**Sample:** 2 green runs of the final tree (earlier runs preceded the /healthz SHA change); 8 distinct trips, 1 run each.

### F-003 — The workstation's default Python is 3.11.9; the scaffold requires 3.12
**Date:** 2026-09-22 · **By:** Builder (Claude Code), preflight
**Claim:** `python --version` on the owner's workstation returns 3.11.9. The
scaffold pins 3.12 locally (`setup.ps1`), in CI, and in the Dockerfile. It is not
yet known whether 3.12 is installed alongside 3.11.
**Artifact:** `REPORT-Code-2026-09-22-StockGraderMDK-preflight.md` §2.
**Sample:** 1.
**Consequence:** as first written, `setup.ps1` would have stopped at its
version check. That is the correct failure direction, but it was a surprise.
Resolved by D-011.
**Amended by F-005:** the claim is true but incomplete. There are three runtimes
and two defaults, neither of them 3.12. Left as written; reversals are recorded,
not patched.

### F-004 — The order's offline step contradicted setup.ps1
**Date:** 2026-09-22 · **By:** Builder, order receipt §4
**Claim:** The order's Step 3 (and testplan OPEN-3, v1–v2) said to run
`setup.ps1` with the network off. `setup.ps1` installs dependencies from PyPI
before it runs the suite, so offline it fails at the install step, never
reaching the claim being tested (suite hermeticity).
**Artifact:** `setup.ps1` (install precedes pytest); Builder report §4.
**Sample:** static reading, 1.
**Resolution:** build `.venv` with the network on, then run pytest alone with
the network off (testplan OPEN-3, v3). A first-class offline mode is D-012.
**Planner note:** the error was the Planner's. The order also stated "v1 never
reached your machine" as fact. It had arrived four minutes after the preflight
sweep. That was a belief written as a fact (P8) and is recorded here for that
reason.

### F-005 — Three Python runtimes, two defaults, none of them 3.12
**Date:** 2026-09-22 · **By:** Builder, order receipt §5
**Claim:** `python` resolves to 3.11.9 (on PATH). `py` with no version resolves
to 3.14 (launcher default). 3.13 is present via WindowsApps. `py -3.12` finds no
runtime.
**Artifact:** `py -0p` and `py -3.12 --version` output, Builder report §5.
**Sample:** 1.
**Consequence:** a venv made by hand silently gets 3.11 or 3.14, and its green
local suite would not correspond to what CI ran (P11 shape). `setup.ps1` hard-
fails rather than falling back, so the sanctioned path is safe. Unsanctioned
paths are not. Addressed by D-011 (amended).

### F-006 — setup.ps1 did not parse under Windows PowerShell 5.1
**Date:** 2026-09-22 · **By:** Builder, report "F006-BLOCKED"
**Claim:**
- `setup.ps1` (v1–v3) was UTF-8 without a BOM, so Windows PowerShell 5.1 read
  it as cp1252.
- Its em-dash (`e2 80 94`) decoded to `â€”`. The third character is U+201D,
  which PowerShell accepts as a string delimiter.
- Line 27's string therefore closed early, and the file failed to **parse**:
  "missing terminator", reported at line 37. No statement ran, including the
  3.12 guard.
**Artifact:** PS 5.1 parser output, plus a two-file minimal reproduction
(BOM-less fails, BOM'd passes). Builder report §4.1 and §4.3.
**Sample:** 1 reproduction of the real script, 1 minimal pair.
**Why the gate missed it:** CI runs pytest on Linux and never executes `.ps1`.
**Resolution:** D-013, with guard G-9. The PS 5.1 parse of the fixed file is
unproven until the Builder runs it (testplan OPEN-4).
**Supersedes:** the Builder's order-receipt §3.3 conclusion ("encoding clean,
no action needed"). Its observations were accurate; the conclusion did not
ask whether the consuming interpreter would agree. Recorded, not rewritten.
**Planner note:** the Planner never ran `setup.ps1`, having no Windows. It
listed the unbuilt Dockerfile as OPEN-2 but did not list the unrun installer.
That was the same kind of gap, and only one instance of it was recorded.

### F-007 — Two dependency deprecation warnings are invisible to the gate
**Date:** 2026-09-22 · **By:** Builder, Steps 1–6 report §4.2
**Claim:** Every run reports 2 warnings:
- Starlette: using `httpx` with its TestClient is deprecated in favour of
  `httpx2`.
- anyio: the `anyio.abc.BlockingPortal` alias is deprecated.
Neither fails anything today. The first is pin-shaped: acting on it moves
pinned versions, which may move the contract snapshot (A-006).
**Artifact:** pytest summary lines, owner workstation, 2 runs.
**Sample:** 2.
**Resolution:** D-015.

### F-008 — The suite is reproduced on the owner's workstation, parsed by PS 5.1, and makes no network egress
**Date:** 2026-09-22 · **By:** Builder, Steps 1–6 report §4
**Claim:**
- Windows PowerShell 5.1.26100.9444 parsed and ran `setup.ps1` (v4). It
  created `.venv` with Python 3.12.10 and reported **22 passed** (0.79 s,
  network on).
- The suite alone then passed **22/22 in 0.58 s** with every DNS lookup and
  every non-loopback connection forced to raise.
**Artifact:** console output in the Builder report §4. The egress blocker was an
out-of-tree pytest plugin (`-p`), never committed.
**Sample:** 1 run each.
**Instrument lesson:** the first version of the blocker also blocked loopback,
and 7 tests went red. On Windows the event loop under Starlette's TestClient
builds its self-pipe from a loopback `socketpair()`. That red measured the event
loop, not the suite. Any future offline instrument must leave loopback open, or
it reports a false dependency.
**Closes:** OPEN-3 and OPEN-4. **Supersedes:** F-002's "passed elsewhere"
caveat.

### F-009 — The `--3way` instruction could not do what it said
**Date:** 2026-09-22 · **By:** Builder, patch-verification report §4
**Claim:** `StockGraderMDK-register-update-2.patch` carries **no `index` lines**,
because it was produced with `diff -u` rather than `git diff`. `git apply --3way`
therefore cannot resolve the pre-image blob. It prints
`error: repository lacks the necessary blob to perform 3-way merge`, falls back
to direct application, and **exits 0**. A procedure step printed `error:` on a
successful run, and the merge safety net it was chosen for did not exist.
**Artifact:** rehearsal in a throwaway repo; exit code 0 with the error on stderr.
**Sample:** 1 patch, 4 simulated PR-1 shapes, all applying by direct application.
**Why regenerating with index lines was rejected:** the pre-image blob is
update-1's `testplan.md` *without* PR-1's gate row, and PR-2 restores that row
before committing, so that blob never enters the repository. `--3way` would fail
identically. The fix would have looked like a fix without being one.
**Resolution:** step 12.3 became verify-hash → `git apply --check` → `git apply`.
Confirmed in this PR: `--check` passed and the patch applied, with PR-1's gate
row untouched because it sits above both hunk context windows.

### F-010 — An LF-only patch survived `core.autocrlf = true` only because of `.gitattributes`
**Date:** 2026-09-22 · **By:** Builder, patch-verification report §5
**Claim:** the owner's workstation has **`core.autocrlf = true`** set globally.
The register patch is LF-only. Had the working tree checked `docs/testplan.md`
out as CRLF, the patch would not have applied. `.gitattributes`
(`* text=auto eol=lf`) overrides `core.autocrlf`, the working tree stays LF, and
the patch applies.
**Artifact:** rehearsal with the real `.gitattributes` in place —
`working-tree testplan.md has CRLF: False`, `git apply --check: PASS`.
**Sample:** 1.
**Consequence if `.gitattributes` were removed or weakened:** LF patches would
fail **only on Windows**, invisibly to CI and to the Planner's environment, with
an error that does not name line endings. The same file also pins
`*.ps1 text eol=crlf`, which keeps `setup.ps1` correct for PowerShell while the
rest of the tree stays LF.
**Resolution:** none needed. Recorded so the rule is never deleted as noise.

### F-011 — Fly region `sea` is deprecated; the first deploy failed on it
**Date:** 2026-09-22 · **By:** Builder, Step 9
**Claim:** the v4 `fly.toml` pinned `primary_region = "sea"`. The first deploy of
`0ac7a7d` passed `test`, built and pushed the image (48 MB), and provisioned IPs,
then failed creating the machine:
`Region sea is deprecated and cannot have new resources provisioned. Please
consider using an alternate region such as sjc`.
`fly platform regions` no longer lists `sea` at all.
**Artifact:** Actions run
[35754209737](https://github.com/mdk32366/StockGraderMDK/actions/runs/35754209737),
deploy job log.
**Sample:** 1.
**Note on direction:** this is the failure mode OPEN-2 predicted — the first real
build is where an untested Dockerfile and an untested platform config fail, and
it failed loudly at the gate rather than quietly in production.
**Resolution:** changed to `sjc` in `6f69a09`, Fly's own suggestion and the
nearest surviving West Coast region. Region choice is a real decision and is
referred to the Planner as **D-017** for ratification; it is one line and a
redeploy to change.

### F-013 - KEEL V10 states the go-private rule three ways, two of them superseded
**Date:** 2026-09-22 - **By:** Planner, D-020 ruling, after the owner corrected it
**Claim:** the rule for when a project repo goes private appears in three
documents and does not agree with itself:

| Document | What it says |
|---|---|
| KEEL-1, Principle 10, body | "goes private once the project is **production-stable**" -- the current rule |
| KEEL-1, Principle 10, headline | "Go private when it goes **real**" -- undefined, and the source of the drift |
| KEEL-2, Step 17 | "First real credential, first real user data, or first live deploy -- **whichever comes first**" -- superseded |
| KEEL-3, Quick Card, line 17 | same superseded wording |

**Consequence, observed:** the rule was amended in one document out of three,
and **the two that were missed are the operational ones** -- the field manual
and the quick card. A person laying a Keel reads those, not the essay. On this
project the Planner read the Checklist, treated Step 17 as triggered on day one,
and planned to take the repo private. The owner's ruling is what caught it.
**Artifact:** KEEL-1 Principle 10 (body and headline), KEEL-2 Step 17, KEEL-3
line 17. **Sample:** 1 project, caught before acting.
**Note on the inspection stamp:** KEEL-2 and KEEL-3 are stamped V10 as reviewed
sets, and KEEL-3 carries no "INSPECTED, UNCHANGED" note at all. An inspection
that did not catch this contradiction is recorded as an inspection that passed.
**Resolution:** D-020 for this project. For KEEL itself the fix is doctrine and
belongs to the owner, proposed for V11: align Step 17 and Quick Card line 17
with Principle 10's body; replace the vague "when it goes real" headline with
the observable; add the scar that *a rule amended in the essay and not in the
checklist is a rule the next person will not follow*; and note in the travelogue
that the V10 inspection pass did not detect it.

### F-012 - A mis-specified warning allowance failed closed, not open
**Date:** 2026-09-22 - **By:** Builder, PR-3
**Claim:** the first `filterwarnings` allowance for F-007 named
`DeprecationWarning` as the category. Starlette raises its own
`StarletteDeprecationWarning`, so the filter did not match, `error` applied, and
the suite went **red at collection**:
```
ERROR tests/test_api.py - starlette.exceptions.StarletteDeprecationWarning
Interrupted: 1 error during collection
```
**Resolution:** the category field is left **empty**, so each filter matches on
its message whatever class upstream raises it as. The lesson is also recorded as
a comment in `pytest.ini`, because a tool's home is the tool.
**Why this is a finding and not just a bug:** the **direction was right.** A
mis-specified allowance made the suite fail rather than silently stop filtering.
An allowance that fails **open** -- one that quietly matches nothing and lets new
deprecations through -- is the dangerous shape, and this construction cannot take
it. **Sample:** 1.

### F-014 - Fly commands print live credentials in normal, successful output
**Date:** 2026-09-22 - **By:** Planner and owner, cluster-creation session
**Claim:** `fly mpg create` printed the full connection string for `fly-user`,
and `fly mpg attach` printed it for `stockgradermdk` - in both cases inside the
same block as the cluster and app details the owner needed to relay. Both
reached a planning chat.
**Nobody was careless.** The tooling hands you the secret at the exact moment
you are relaying the surrounding information.
**Consequence:** two credentials compromised on the day the cluster was created.
A third followed by a different route (F-019), making three in one day.
**Mitigation is mechanical, not attentional:** D-030.
**Amendment, 2026-09-22 (Builder):** **not every `fly mpg` command leaks.**
`fly mpg users create` prints only `Name` and `Role` - no password, no
connection string. The offenders are specifically `fly mpg create` and
`fly mpg attach`. This matters because "Fly commands print credentials" is the
kind of general warning that gets tuned out, whereas a named list of two
offenders and one safe alternative is actionable - and it means **creating a
user is the safe way to add an account.**
**Sample:** 2 commands observed leaking, 1 observed not leaking.

### F-015 - `DATABASE_URL` was left Staged by the attach
**Date:** 2026-09-22 - **By:** Planner and owner, cluster-creation session
**Claim:** `fly secrets list` showed `DATABASE_URL` as **Staged** while
`STOCKGRADER_API_KEY` read **Deployed**. The running machine did not have the
connection string. `fly secrets deploy` fixed it in seconds and both then read
Deployed.
**Artifact:** the two `fly secrets list` outputs.
**Why it matters:** this is the Principle 4 scar observed live - a secret that
looks set while the app holds the old value. It was harmless **only** because
nothing queries the database yet.
**What no existing guard would have caught:** the gate passed every check,
including the live-SHA verification, because the SHA is baked into the image and
has nothing to do with secrets. See the testplan open item.
**Sample:** 1.

### F-016 - The backup-list command has been run, and a backup exists
**Date:** 2026-09-22 - **By:** Planner and owner, cluster-creation session
**Claim:** `fly mpg backup list d1zj5omk443ryqkv --all` was executed against the
real cluster and returned one completed full backup, `20260922-192041F`, at
2026-09-22T19:20:41Z. Without `--all` it lists only the last 24 hours.
Retention is 10 days.
**Why it matters:** Principle 1's three questions have real answers on this
project for the first time. A completed backup exists; exposure is everything
since 19:20Z; it covers neither the scratch database nor anything ingested
before the next backup.
**This is what `architecture.md` recovery row 1 now records** - the command that
ran, not one that looks right.
**Sample:** 1 run, 1 backup.

### F-017 - Step 16's separation was nominal as first configured
**Date:** 2026-09-22 - **By:** Planner and owner, cluster-creation session
**Claim:** `fly mpg users list` showed **both** accounts at `schema_admin`.
Two accounts differing only in name give the recovery account no capability the
application lacks, so the Step 16 separation existed on paper only.
`fly mpg users create --help` then showed three roles - `schema_admin`,
`writer`, `reader` - so this was **our default, not a platform ceiling.**
**Consequence:** a compromised application credential would have carried full
schema rights.
**Resolution:** D-031, with A-017 as the evidence that `writer` suffices.

### F-018 - Infrastructure mutations outran their written record
**Date:** 2026-09-22 - **By:** Builder, and raised by the Planner
**Claim:** between receiving the Phase 0 handover and reporting, three mutations
landed on a live cluster - a database, a user, and a DDL statement - **with no
written record anywhere.** Anyone reconstructing the project from its documents
would have found cluster objects the newest report did not mention.
**What was literally true:** no report said anything false. The last report
predated the handover and correctly described the state at the time it was
written, and each action was narrated in the session as it happened.
**Why that is not the point:** the register is assembled from reports. **A chat
is not a record** - it is not durable, not what the register is built from, and
not what a reader will have later. For that window the only evidence the objects
were legitimate was the Builder's own account of them afterwards. That is the
shape that weakens every other guard's proof, because all of them rest on
reports being written when the work happens rather than when someone asks.
**Cause:** the Builder went straight from reading the handover into executing it,
treating the report as the thing at the end. For code that is harmless - git is
the record. For infrastructure there is no commit.
**Resolution:** D-034.

### F-019 - Closing OPEN-1 required a human-mediated secret transfer, and the channel was chat
**Date:** 2026-09-22 - **By:** Builder, with the framing corrected by the Planner
**Claim, stated precisely:** **Fly Managed Postgres offers no machine-retrievable
credential path.** No reveal, no reset, no CLI command; `\password` is refused by
a Fly policy trigger; `fly mpg users` exposes only `create`, `delete`, `list`
and `set-role`; passwords are settable only by a human in the dashboard, and are
printed unbidden only by `fly mpg create` and `fly mpg attach`. Therefore
**every non-hermetic run on this platform requires a human-mediated secret
transfer**, and the only thing under our control is the channel.
**What happened:** the owner supplied `probe_ro`'s password in chat, with the
cost explicitly acknowledged. OPEN-1 was closed with it. The Builder held it in
a shell variable for the life of one command, never echoed it, never wrote it to
any file, and never brought it into the repo - but a credential in a transcript
is a credential in a log, and `probe_ro` joins D-029 as the third compromised
credential of the day.
**The correction that matters:** the Builder first wrote that closing OPEN-1
*"requires exactly the thing D-030 forbids."* That is not right, and the
difference decides what gets built. D-030 forbids credentials in transcripts,
repo files and env files in the tree; it does **not** forbid the Builder holding
a scoped, short-lived credential. **The channel is the failure, not the
requirement.** The default channel is chat because chat is where the
conversation is happening - which is how three credentials were exposed by three
different mechanisms in a single day.
**Planner's share:** "hand it out of band" was said without specifying the
mechanism, and **an unspecified mechanism defaults to the nearest one.**
**Resolution:** D-030's procedure clause, and D-032 so the probe stops needing a
DSN at all.

### F-020 - The document relay is manual, lossy, and silent
**Date:** 2026-09-22 - **By:** Planner
**Claim:** documents have gone missing in **both** directions in a single day,
and neither end could detect it:
- **Planner to Builder:** `RULING-...-post-keel.md` was written and never
  delivered. The Builder discovered it only because a later ruling superseded a
  section of a document it had never seen, and because the register was missing
  D-017, D-018 and D-019.
- **Builder to Planner:** a Builder report - carrying the cluster-object
  inventory, the F-014 amendment, and the psycopg proposal - never reached the
  Planner, who learned of its contents only through a later report citing it.
**Consequence:** a missing document surfaces late, as a stale decision, an
unanswered question, or an unexplained object on a live cluster. Both instances
cost real time and one of them produced an unexplained account on a production
cluster.
**Resolution:** D-033. **Sample:** 2 losses, opposite directions, same day.

### F-next/backup-cadence-observable - The rolling schedule is running on this cluster, and it is hourly
**Date:** 2026-09-23 - **By:** Builder, backup-strategy block §3
**Claim:** `fly mpg backup list d1zj5omk443ryqkv --all` returns **21 completed
backups**, not one. The schedule is observably running on *this* cluster, at a
cadence the documentation did not state:

| Cadence | Evidence |
|---|---|
| Full, daily | `20260922-192041F` at 19:20:41Z; `20260923-000148F` at 00:01:48Z |
| Differential, every 6 h | `...-060053D` at 06:00:53Z, `...-120226D` at 12:02:26Z |
| Incremental, hourly | 01:03Z through 14:04Z, one per hour, no gaps |

**Artifact:** verbatim output in `REPORT-Code-2026-09-23-...-backup-mechanics.md`.
**What this changes:** B-2's stated rationale - "the alternative is depending on
whenever the rolling schedule last happened to fire" - is weaker than written.
The schedule fires hourly, so worst-case unguarded exposure is ~60 minutes, not
an unknown. **B-2 still stands**, because a pre-risk checkpoint you took is a
recovery point you can name, and ~60 minutes of a bulk load is still a real loss.
The argument for it is now *deliberateness*, not *absence*.
**What surprised us:** the ID format is a **chain**, not a set.
`20260923-000148F_20260923-140422I` names its parent full backup. Incrementals
and differentials are not independently restorable artifacts; they depend on the
full they are rooted in. **Consequence for B-6:** when a full ages out at 10
days, its dependents presumably age out with it, so retention is not "10 days of
hourly points" but "whatever chains still have a living root." Unverified - we
have not watched an expiry - and it is the kind of thing that is discovered at
the worst possible moment. Flagged, not claimed.
**Sample:** 1 cluster, 1 listing, ~38 h of history.

### F-next/pitr-available-window-invisible - PITR exists on this binary; its window does not
**Date:** 2026-09-23 - **By:** Builder, backup-strategy block §3
**Claim:** the installed `flyctl v0.4.102` **does** support point-in-time
restore. `fly mpg restore --help` documents `--pitr-time` (RFC3339, mutually
exclusive with `--backup-id`), resolving the question §3.4 asked: the
documentation page was incomplete, the binary is not.
**The gap:** the same help text says PITR *"requires the cluster's PITR recovery
window to cover this time"* - and **no `fly mpg` subcommand reports that window.**
`fly mpg status` shows ID, name, org, region, status, disk, replicas and direct
IP, and nothing about recovery. `fly mpg --help` lists no command that would.
**Why it matters:** a PITR restore is therefore a **guess that is validated only
by attempting it.** You learn whether your recovery point was reachable at the
moment you need it to be reachable. That is the same shape as F-015 - a state
that looks available until the one moment it is load-bearing.
**Consequence:** `--backup-id` against a listed, `completed` backup is the
verifiable path and should be the default. PITR is the finer-grained tool whose
availability we cannot confirm in advance.
**Sample:** 1 binary, 1 `--help`, 1 negative sweep of `fly mpg --help`.

### F-next/restore-name-flag - `fly mpg restore` takes `-n/--name`; the drill did not use it
**Date:** 2026-09-23 - **By:** Builder, backup-strategy block §3
**Claim:** `fly mpg restore` accepts `-n, --name` and otherwise assigns *"a
generated name."* The drill in §4 step 3 does not pass it, so the cutover
cluster would be born with a generated name.
**Why it matters:** §4 ends with an old cluster and a new cluster alive at the
same time, holding the same data, one of them live - and step 3 is a **REDACT**
step, so the operator is reading around a credential while noting which is which.
Steps 5-11 then each take a cluster ID. A generated name is one more thing to
get right under exactly the conditions that produce mistakes.
**Proposed:** pass `-n stockgrader-db-r1` (or similar) at step 3. Cheap, and it
makes "which cluster am I on" answerable by reading rather than by remembering.
**Sample:** static reading of `--help`, 1.

### F-next/orders-written-against-handovers - A handover is not the register, and orders written against one drift
**Date:** 2026-09-23 - **By:** Planner, self-recorded in
`RULING-...-backup-mechanics-section4-amended.md` §1
**Claim:** three Planner errors landed in a single block, and all three had the
same root - **work was planned against documents rather than against the
register.** The errors themselves are **P-1, P-2 and P-3** in
`planner-errors.md`; what was learned is here.

**What was learned.** A handover records what was true **when it was written**.
The register records what is **true**. The gap between those two is invisible
from inside the handover, because a handover that has gone stale reads exactly
like one that has not. Three consequences followed from one root in a single
morning: work ordered that was already merged, numbers assigned that were already
taken, and a speculation written up as a finding with a carve-out built on top of
it.
**Why it is a finding and not just three mistakes:** the failure is structural.
Anyone writing from the most recent document will reproduce it, because the most
recent document is the natural thing to write from and gives no signal that it
has aged. **The fix is a rule about which artifact is authoritative**, not more
care.
**Rules adopted:** orders are written against the register. `F-next/<short-name>`
replaces Planner-assigned numerals.
**Sample:** 3 errors, 1 block, 1 root cause.

### F-next/relay-loss-recurrence - A cited Planner note never arrived; detected by citation again
**Date:** 2026-09-23 - **By:** Builder
**Claim:** `RULING-...-backup-mechanics-section4-amended.md` §6 cites
`PLANNER-NOTE-2026-09-23-StockGraderMDK-GQS-variable-source-map.md` and says four
items in its §7 are ratifiable immediately. **That document has not arrived.**
The delivery folder holds exactly four documents dated 2026-09-23 - two
handovers, the Builder's report, and this ruling. No planner note, under that
name or any other.
**Artifact:** directory listing filtered to 2026-09-23, and a name search
returning nothing.
**Why it matters:** this is **F-020 recurring, in the same direction, by the same
detection mechanism** - a lost Planner-to-Builder document found only because a
later document referred to it. D-033 (sequence numbers both directions) was
ruled to make this visible immediately instead. It is **PROPOSED, not
implemented**, and this instance is the second data point arguing it should stop
being proposed.
**Consequence:** the scoring track's completeness gate cannot be assessed. Three
of the TDD's §13 conditions are open and the note names which four items would
clear part of it. Unblocking scoring is waiting on a document that does not
exist on this side of the relay.
**Sample:** 2 losses, same direction, 2 days.

### F-next/same-name-revision - A superseding ruling arrived under the same filename, three minutes later
**Date:** 2026-09-23 - **By:** Builder
**Claim:** `RULING-RECORD-2026-09-23-StockGraderMDK-owner-rulings.md` was
delivered at 07:29 and **revised at 07:32 under the same name**, landing as
`RULING-RECORD-2026-09-23-StockGraderMDK-owner-rulings (1).md`. The suffix is the
**browser's**, not the author's. The revision is not cosmetic: it moves two
rulings from *pending clarification* to *ruled* (11 - Altman Z'; 13 - Lynch
archetypes), attaches a prework obligation to the §11.1 deferral, and rewrites a
row of the §13 gate table.
**Artifact:** both files, `diff`ed. 7742 bytes vs 6091.
**Why it matters:** the 07:29 version had already been applied to the register.
Had the second been treated as a duplicate download - which is what a `(1)`
suffix normally means - **the register would have recorded two open questions
that were in fact ruled**, and the archetype classifier work would not have been
opened at all.
**Nothing in the document announces that it supersedes anything.** Its header
still reads as a first issue; only the status line differs, and only if you have
both to compare.
**The detection was luck, not a guard:** a size difference noticed in a directory
listing. **Sequence numbers (D-033) would not catch this either** - a revision
reissued under the same identity is a different failure from a document that goes
missing. What catches it is a **version or issue time in the document body**, and
neither convention has one.
**Related:** F-020, F-next/relay-loss-recurrence. Three relay defects in two
days, three distinct mechanisms.
**Sample:** 1 revision, 1 document, 3 minutes apart.

### F-next/gqs-tdd-defects - Reading the TDD produced four defects a summary had not
**Date:** 2026-09-23 - **By:** Planner, on first full reading of
`TDD-growth-score.md` and `growth-model-lineage.md` (closing A-016)
**Claim:** four defects, none of which had surfaced while the Planner was working
from the Builder's summary. All four are now ruled; they are recorded here
because **they are the evidence the rulings rest on**, and because A-016 was
written to test exactly this.

- **F-A - D-010's condition cited a section that does not exist.** The ruling
  said *"five open questions in its §17."* The TDD's header says **four** open
  questions in **§11**, and §11 contains exactly four: R&D capitalization (11.1),
  sector granularity (11.2), WACC (11.3), size tilt (11.4). **A completeness gate
  that points at a section which does not exist cannot be checked by anyone but
  its author.** *(Ruled - reworded, ruling 7.)*
- **F-B - the TDD was written against a different codebase.** §12's
  confirm-before-build list asks for `alembic heads`, the existing `finance`
  agent's tools and module paths, the settings-overlay pattern, and confirmation
  that `place_stock_order` stays gated. **None of that exists here**, and D-021
  rejected Alembic outright. **Not a defect in the TDD** - it was written
  2026-09-09 for the JARVIS-side finance agent. **It is a defect in treating it
  as build-ready here.** *(Ruled - v4 grounded on this repo, ruling 8.)*
- **F-C - the TDD's data claim is contradicted by its own valuation block.** §2
  goal 1 says the score is *"computed per ticker from SEC filings only"* and §5.1
  names EDGAR as the sole source. But §4.4 ranks on FCF yield, EV/Sales,
  EV/EBITDA, EV/gross profit and EBIT/EV - **every one needs enterprise value,
  which needs market cap, which needs a share price.** EDGAR has shares
  outstanding; it does not have prices. **25% of the score cannot be computed
  from filings.** *(Ruled - ruling 4.)*
- **F-D - Altman's Z needs market data too.** The public-firm Z uses market value
  of equity in its fourth term; Z' substitutes book value. *(Ruled - Z', ruling 11.)*

**Why this is worth its own entry:** A-016 said a summary is not knowing (P8) and
that no scoring design work should proceed until the Planner had read the
documents. **The reading produced four defects and four rulings** - including one
in the register's own condition. The assumption was load-bearing and is now
closed, falsified as intended.
**Sample:** 2 documents, 1 full reading, 4 defects.

### F-next/manifest-adopted - Reconciling a delivery against a manifest catches at delivery what citation caught a day late
**Date:** 2026-09-23 - **By:** Planner (rule), Builder (first reconciliations)
**Claim:** after three relay defects in two days by three distinct mechanisms,
the Planner adopted a **delivery manifest**, and it worked on its first run.
**The rule:** every Planner delivery carries a manifest; the Builder reconciles
what arrived against it **before applying anything.** A document **not on the
manifest was not issued**; a manifest entry with nothing beside it is **a loss
detected at delivery rather than at citation.**

**Evidence, three reconciliations:**

| Manifest | Entries | Result |
|---|---|---|
| D1 | 7 | 6 present, 1 absent **as predicted** (#3, never delivered), nothing unaccounted |
| D2 (r2 of D1) | 9 | 8 present, same predicted absence, nothing unaccounted |
| D3 | 3 | all present, nothing unaccounted |

**What was learned, and it is the point:** yesterday the same absence took **a
citation in a later document** to detect - the note was missed until a ruling
referred to it. Today it was visible **at delivery, before a line was applied.**
The defect did not change; the detection moved earlier, which is the only thing
that was ever wrong with it.

**Second thing learned - self-reference is the weaker guard.** A manifest that
lists itself still cannot report its own absence if it never arrives. **Continuity
is what works:** each manifest names the previous one, so a missing manifest shows
up as a gap in the next. Adopted as the rule rather than left as r2's side effect.
The Planner's self-omission is **P-5**, not a finding - a guard's own artifact is
the first thing outside its coverage.

**Third - the document count is a real cross-check, and it caught something on
its first use.** See `F-next/manifest-count-double-counts`.

**Fourth - the chain has now handled three DISTINCT failure modes**, and the
third is the one that shows it degrades well rather than only working intact:

| Mode | Instance | What survived |
|---|---|---|
| **Whole-delivery loss** | D4, D9, D17 | Only the *fact* of a gap. Size derived from a later cumulative; D4's second document was never identified until re-sent. |
| **Cited-document loss** | `relay-loss-recurrence` | The citation, which is lossy - D9 §3 was never cited and was the most consequential item in it. |
| **Manifest survives payload** | D12 (Code -> Planner) | **The missing document, named by filename, with no inference at all.** |

**The third is the best failure of the three** and it is worth saying why: the
manifest outlived the delivery it described. *A guard that fails gracefully is
worth more than one that only works intact*, and this is the first evidence the
chain does.
**It is also the first loss in the Code -> Planner direction today.** The three
before it all went Planner -> Code, which had begun to look like a property of
the relay rather than of chance. It is not.
**Sample:** 3 manifests, 19 entries, 1 predicted absence confirmed 3 times.

### F-next/manifest-count-double-counts - The cumulative document count double-counts carried-forward entries
**Date:** 2026-09-23 - **By:** Builder, reconciling D3
**Claim:** D3 states *"Cumulative Planner documents issued 2026-09-23: **12**.
D1 listed 7, D2 listed 9 including itself and D1, D3 adds 3."* **The correct
figure is 11 issued, 10 on disk.**
**The arithmetic:** D2's 9 entries already contain D1's 7 plus D1's manifest and
D2 itself. D3's three entries are the ruling, D3's own manifest, and **D2 carried
forward as the previous-manifest entry** - which D2 had already counted. `9 + 3`
therefore counts D2 twice.
**Artifact:** directory listing of Planner documents dated 2026-09-23, filtered
of Code documents: **10 files.** 11 issued minus #3, never delivered.
**Why it matters, and why it is small:** the entry lists reconcile **perfectly** -
every document accounted for in all three manifests. Only the cumulative
arithmetic is wrong. **This is the count doing exactly what the Planner said it
was for:** *"a cross-check against the entry list, not a substitute for it."* It
disagreed with the entry list on its first outing and the entry list was right.
**Proposed fix, one line:** the previous-manifest entry is **continuity, not a
new document**, and is excluded from the delivery's count. Otherwise every
carried-forward entry inflates the cumulative by one per delivery, and the error
compounds rather than staying constant.
**Sample:** 3 manifests, 1 discrepancy, off by 1.

### F-next/tolerated-error-hides-real-error - A value with a known, tolerated error has a place for a real error to hide
**Date:** 2026-09-23 - **By:** Builder, opening PR-6; **generalised on the
owner's instruction** (`RULING-RECORD-...-d019-promotion.md` §5)
**Renamed from** `F-next/d019-counter-fell-behind`. **The counter is retired;
the lesson is not, and it is the reason this entry outlives its subject.**

**The general claim.** When a value is **known to be wrong in a specific,
tolerated way**, that tolerance becomes cover for a second error of the same
shape. **A count that is supposed to lag does not look wrong when it lags
further.** The reader checks the value against the exception they were told
about, finds it consistent, and stops - the exception has consumed the evidence
that would have revealed the defect.

**This generalises past counters** to anything carrying a documented margin: a
metric with a known lag, a total with a known exclusion, a report with a known
blind spot. **The tolerated error defines the exact size and shape of the real
error that can hide behind it**, which is what makes it predictable rather than
bad luck.

**Rules adopted, both standing for any counter this project keeps:**
- **Recompute, never increment.** Derive the value from the source of truth each
  time it is touched, so it cannot drift.
- **A documented tolerance is a place to look, not a place to stop looking.**

**The instance it came from.** The counter read **6 of 10** and was **8**.
PR-5's two green `windows-setup` runs - `35783781284` (branch) and `35783912646`
(main, the merge) - completed at 2026-09-22T20:59-21:00Z and were **never
recorded**, because PR-5 merged after the count line was last written.
**Artifact:** `gh run list --workflow=gate.yml`, twelve runs, all `success`.
Recovered from the API, **not from memory or from the merge report.**
**Why it matters:** this is **F-018's shape in a second place.** The work outran
its record and **nothing in the document revealed it** - the counter did not read
"stale", it read "6", which is a number and looks like an answer. D-034 fixed
this for infrastructure mutations by requiring a report before the next unit of
work. **The counter has no equivalent**, because merging a PR is not a unit of
work anyone reports on.
**The structural rule is not the cause.** The counter is deliberately one behind
- a committed count cannot include the run validating the commit recording it -
and that is sound. **Being one behind by design and two behind by accident are
different things**, and the design conceals the accident: a count that is
*supposed* to lag does not look wrong when it lags further.
**Outcome:** recomputed to **9 of 10**, then **10 of 10** on run `35877772087`.
D-019 was promoted on that threshold and **the counter is retired** - which is
why this entry was rewritten to carry the lesson rather than the incident.
**Sample:** 1 counter, 2 missed runs, 1 day.

### F-next/required-check-context-name - The ruling named a context string that does not exist
**Date:** 2026-09-23 - **By:** Builder, implementing the D-019 promotion
**Claim:** the promotion ruling says to add **`windows-setup`** as a required
check. **No check by that name is ever reported.** The gate's Windows job is a
matrix job and reports as **`windows-setup (PS 5.1)`**.
**Artifact:** `gh api repos/.../commits/<sha>/check-runs` on HEAD of
`pr6-backup-strategy` - three contexts: `deploy`, `test`,
**`windows-setup (PS 5.1)`**.
**Why it matters, and it is not pedantry.** GitHub accepts **any string** as a
required context, including one nothing will ever report. A required check that
never reports is **permanently pending**, and permanently pending **blocks every
merge to `main` with no failure to diagnose** - the PR shows an expected check
that simply never arrives. **The failure mode of getting this wrong is strictly
worse than not doing it at all**, because a job that does not run looks like an
outage rather than a typo.
**Where the error comes from:** the workflow's job *key* is `windows-setup`; the
*context* is the key plus the matrix dimensions. Anyone reading `gate.yml` gets
the first and needs the second. The ruling was written from the workflow file,
which is the natural place to look and the wrong one.
**Correct string: `windows-setup (PS 5.1)`.** D-019 §2 is corrected accordingly;
the Planner's error is **P-8**, with the rule that **identifiers a platform
reports are read from the platform, by query - not inferred from the
configuration that produces them.**

**The matrix brittleness is a live hazard, not a note.** Changing the matrix
dimension **renames the context** and silently converts the required check into
one that never reports - the same permanent-pending block, **arriving later and
with no change to the protection rule to point at.** Adding PowerShell 7 to that
matrix does it.
**GUARD, adopted as an action rather than an observation:** *any change to the
gate's matrix dimensions requires re-reading the reported contexts and updating
branch protection **in the same change.*** Recorded as an action because **the
observation alone will not survive six months** - the person who changes the
matrix will not be the person who read this.
**Sample:** 1 workflow, 3 contexts, 1 name mismatch.

### F-next/continuity-caught-d4 - An entire delivery went missing, and the manifest chain caught it at delivery
**Date:** 2026-09-23 - **By:** Builder, reconciling D5
**Claim:** **delivery D4 never arrived - the whole of it.** D5 names
`MANIFEST-Planner-2026-09-23-...-D4.md` as its previous manifest; no file by that
name exists, and no document from D4's delivery does either.
**Artifact:** directory listing of Planner documents dated 2026-09-23: **12 on
disk.** Ten from D1-D3 (established when D3 was reconciled: 11 issued, 1 never
delivered) plus D5's two. **Nothing from D4.**
**Scale of the loss, derived rather than assumed:** D5 states 13 issued through
D4. D1-D3 accounted for 11. **D4 therefore carried 2 documents** - its own
manifest and one other, whose identity is unknown because the only record of it
was in the manifest that went with it.
**This is the fourth relay defect in two days, and the first one caught by
design.** F-020 surfaced when a decision went stale. `relay-loss-recurrence`
surfaced when a later document cited what was missing. `same-name-revision`
surfaced on a byte-count difference in a directory listing - luck. **This one
surfaced in the first thirty seconds of reconciliation, before anything was
applied, because D5 named its predecessor and its predecessor was not there.**
**That is precisely what continuity was adopted to do** (`D-next/delivery-manifest`),
and it is the first time this project has detected a relay loss **without needing
a downstream symptom.**
**What is not recovered:** the rule tells us a delivery is missing and how large.
It does not say what was in it. **D4's second document is unknown and must be
re-sent.** P-6 is also unknown - D5 cites **P-7** as the next error number, so a
P-6 was recorded somewhere in D4.
**Sample:** 1 delivery lost, 2 documents, detected at delivery.
**RESOLVED 2026-09-23, same day.** D4 was re-sent in full in D6 - both documents,
unchanged, under their original filenames and **marked as re-sends rather than
counted as newly issued** (the sub-rule that loss forced). P-6 recovered.
**The recovery was verified by the check D6 stated in advance:** *"expected on
disk after this delivery: 16. If your count is not 16, one of us has lost
something else."* **Count run: 16.** First time today the relay has reconciled
with nothing outstanding.
**What the episode establishes:** continuity detects the loss and bounds its
size; it does **not** identify the contents, and the re-send is the only
recovery. The gap between detection and recovery was two deliveries, during which
**an acceptance the Planner had already granted sat unanswered on this side** -
D4 accepted the P-1..P-3 move, and the Builder carried it as an open judgment
call until D6 arrived. **A lost document does not only delay work; it can leave a
question open that has in fact been answered.**

### F-next/accruals-formulation-collides-with-growth-block - The two accruals methods disagree exactly where §4.1 is looking
**Date:** 2026-09-23 - **By:** Planner, verifying OPEN-13 (F-E)
**Claim:** two accruals methods are in general use - **Sloan's balance-sheet
differencing** (the original, `ACC = (ΔCA − ΔCash) − (ΔCL − ΔSTD − ΔTP) − DEP`,
scaled by **average** total assets) and the **cash-flow method** (earnings minus
operating cash flow, both from the cash flow statement). **They disagree, and
they disagree most for companies with acquisitions, divestitures or discontinued
operations** - a balance-sheet difference reads **an acquired subsidiary's
working capital as if the company had generated it.**
**Why that is not a tolerable margin here:** those are **exactly** the companies
§4.1's organic-versus-acquired proxy exists to catch. A roll-up would take a
**distorted accruals ratio from the integrity gate** and a **goodwill discount
from the growth block** - two parts of the model measuring the same underlying
fact, **with one of them doing it wrongly.** The error is not random across the
universe; it is concentrated in the population the model is most trying to
discriminate.
**Artifact:** Sloan 1996 (The Accounting Review 71(3), 289-315), verified
2026-09-23; the divergence is a property of the two definitions, not an empirical
claim needing a sample.
**Recommendation (Planner):** use the **cash-flow formulation** for the gate, and
**record it as a deliberate departure from Sloan's original rather than an
implementation shortcut.** The balance-sheet version is the historical
definition; **the cash-flow version is the one that survives contact with
acquisitive companies**, and this universe is full of them.
**Owner ruling required - it changes §4.3's stated basis.** Tracked as OPEN-17.

### F-next/accruals-anomaly-decayed - The gate's justification was a return claim; it should be an accounting-quality claim
**Date:** 2026-09-23 - **By:** Planner, verifying OPEN-13 (F-F)
**Claim:** published work reports the accruals anomaly generated excess returns
for roughly four decades but **weakened after 2002**, with one line of argument
attributing the decline to the spread of analyst cash-flow forecasts.
**What it breaks, precisely:** nothing operational. The lineage calls Sloan *"the
most operationally important result in the literature"* - **a claim about return
prediction**, and if the premium has decayed that claim is **weaker than
stated.** The design is unaffected; **the stated reason for the design is not.**
**The better argument, and §4.3 should be written on it:** accruals-driven
earnings **reverse**, and a buy-and-hold model **has no business rating a company
highly on earnings that are about to reverse - whether or not the market still
pays for the distinction.** That is an **accounting-quality** argument, not a
**factor** argument.
**Why the distinction is worth the edit:** a gate justified as a factor is
falsified when the factor decays; a gate justified on accounting quality is not.
**We would have kept the gate either way** - but for a stated reason that had
quietly stopped being true, which is how a register loses its value even while
every entry in it stays technically defensible.
**Action:** edit lineage §5 and §9's third axiom. Tracked as OPEN-18.

### F-next/restore-resizes-disk - The restore silently provisioned 50% more storage than the source
**Date:** 2026-09-23 - **By:** Builder + owner, restore drill step 4
**Claim:** `d1zj5omk443ryqkv` has **10 GB** allocated. `fly mpg restore` produced
`kzpwm0j1dm204nv3` with **15 GB**. No size flag was passed; `fly mpg restore
--help` documents none.
**Artifact:** `fly mpg status` on both clusters, same session.
**Why it matters beyond the number:** the restored cluster **became the live
one**, so the change is permanent unless acted on, and the restore help states
the new cluster is **billed separately** - so this is a real cost difference that
arrived silently. More broadly: **a restore is not a faithful reproduction of the
source's configuration.** We were treating it as "same cluster, new ID." It is
not, at least for storage.
**The part with a deadline:** the 10 GB original is **the only surviving record
of what the configuration was supposed to be**, and it disappears when the old
cluster is destroyed after the ticker load. Anyone reconstructing intent later
sees 15 GB and no reason to doubt it.
**Not a blocker:** more disk than the source is the harmless direction. Recorded
because it would have gone unnoticed had the specs not been read, and because the
same mechanism could resize in the harmful direction on a larger source.
**Sample:** 1 restore, 1 discrepancy.

### F-next/attach-refuses-to-overwrite - `fly mpg attach` fails closed on an existing DATABASE_URL, and the drill could not execute
**Date:** 2026-09-23 - **By:** Builder + owner, restore drill step 7
**Claim:** `fly mpg attach` **refuses** when the target app already has
`DATABASE_URL` set:
`Error: app stockgradermdk already has DATABASE_URL set. Use 'fly secrets unset
DATABASE_URL' to remove it first`
**The amended §4 assumed attach would replace it. It will not**, so **step 7 as
written could not run**, and a step 6.5 (`fly secrets unset DATABASE_URL`) had to
be inserted.
**The tool is right and the drill was wrong.** Fly is **failing closed** rather
than silently replacing a live database credential - the correct direction, and
the same principle the rest of this register argues for. The defect is ours.
**Why finding it here is the whole point of B-4:** this is a rehearsal on a quiet
day with nothing at stake. The same gap discovered during an actual recovery
would be found by an operator under time pressure, mid-incident, with the
production app already pointing at a dead cluster.
**Consequence recorded before acting:** after the unset, the app has **no path
back to the old cluster.** Reverting means re-running `attach` against
`d1zj5omk443ryqkv`, **which re-prints and re-leaks that credential** (F-014).
The revert path is not free. Accepted deliberately, since `stockgradermdk` is
compromised and slated for retirement by destroy anyway.
**Also established:** `fly secrets unset` **deploys by default** (`--stage`
skips). The plain form was chosen over `--stage` because it was unestablished
whether a staged unset clears attach's precondition, and mid-cutover is not where
to find out.
**Amendment for the drill:** §4 step 7 requires a preceding unset **whenever the
app already holds a `DATABASE_URL`** - which is every cutover after the first.
**Sample:** 1 attach, 1 refusal, 1 inserted step.

### F-next/app-connects-via-pgbouncer - The attached connection string points at the pooler, not the database
**Date:** 2026-09-23 - **By:** Builder, restore drill step 7
**Claim:** the `DATABASE_URL` written by `fly mpg attach` resolves to
**`pgbouncer.kzpwm0j1dm204nv3.flympg.net`**, not the `direct.` endpoint that
`fly mpg status` reports. The app talks to a **connection pooler**.
**Why it is recorded now rather than when it bites:** a transaction-mode pooler
interferes with **prepared statements, session-level settings and advisory
locks** - and a migration runner (D-021) characteristically depends on all three.
Migration 0001 is designed against `stockgrader_scratch` and run against this
cluster afterwards, so **the question of which endpoint the runner uses has to be
settled before that run, not during it.**
**Not established:** the pooler's mode (transaction vs session), and whether the
`direct.` endpoint is reachable with the same credential. **Both are questions,
not claims.** Tracked as testplan OPEN-21.
**Sample:** 1 connection string.

### F-next/restored-cluster-joins-the-schedule-immediately - The rolling schedule claimed the new cluster within minutes
**Date:** 2026-09-23 - **By:** Builder, restore drill step 11
**Claim:** `kzpwm0j1dm204nv3` went `ready` at approximately 15:54-15:58Z. The
rolling schedule took a **full** backup at **16:00:17Z** - before the drill
reached step 11, which took its manual full at 16:27:44Z.
**Artifact:** `fly mpg backup list kzpwm0j1dm204nv3 --all` - two fulls, the
schedule's preceding ours.
**What it amends:** **B-3's premise.** B-3 reads *"a freshly restored cluster has
no backup lineage until one is made or the schedule fires, and the window between
those is unguarded."* The window was approximately **six minutes**, not
open-ended.
**B-3 still stands, on B-2's ground rather than its own original one:** a
checkpoint you took is a recovery point you can **name**, and the first act after
a cutover is exactly when you want a named one. **But the argument is
deliberateness, not absence** - the identical correction B-2 already took.
**Also established:** the schedule's first act on a fresh cluster is a **full**,
which it must be - there is no root to build on. So a restored cluster acquires a
chain root on its own, quickly.
**Sample:** 1 restored cluster, 1 schedule, ~6 minute window.

### F-next/attachment-record-is-not-authoritative - `fly mpg list` shows the app attached to both clusters
**Date:** 2026-09-23 - **By:** Builder, post-drill sweep
**Claim:** after the cutover, `fly mpg list -o matt-kelly-802` shows
**`stockgradermdk` in the ATTACHED APPS column of BOTH clusters** -
`kzpwm0j1dm204nv3` (live) and `d1zj5omk443ryqkv` (old).
**Why:** the drill set `DATABASE_URL` via `attach` and re-pointed it via
`unset` + `attach`, but **never ran `fly mpg detach` against the old cluster.**
The attachment is a separate platform record from the secret.
**The consequence that matters:** **the ATTACHED APPS column does not answer
"which cluster is this app actually using."** It records which clusters have ever
been attached and not detached. The only authoritative answer is the host inside
`DATABASE_URL`, which **cannot be read without exposing the credential** - so the
question "what is this app connected to" has **no cheap, safe, direct answer** on
this platform.
**This is F-015's family:** a platform surface that looks like state and is
actually history. A reader checking `fly mpg list` during an incident would
reasonably conclude the app was attached to the old cluster, and be wrong -
or conclude it was attached to both, and not know which wins.
**What we relied on instead**, and it was the right instrument: the connection
string's own host component, read by the owner at attach time and reported
without the password.
**Action:** `fly mpg detach` against the old cluster is **not** run today - the
old cluster is deliberately retained, and detaching may interact with the secret.
Recorded as testplan OPEN-23 to be resolved at destroy time.
**Sample:** 1 app, 2 clusters, 1 listing.

### F-next/orphaned-restore-clusters-already-exist - CORRECTED: two clusters exist; "orphan" was my inference and it was not supported
**CORRECTION 2026-09-25, and the framing was mine.** The title and the body below
call two clusters **orphans**. **The evidence established only that they exist.**
Both are attached to live projects, and one is named
`sentinel-holy-rain-4562 restored 2026-08-17...` and attached to `sentinel...` -
**it may be Sentinel's production database**, restored once and in use ever since.
Nothing in `fly mpg list` distinguishes that from an abandoned cluster.

**The part that makes this mine rather than unlucky:** I had already recorded
`F-next/attachment-record-is-not-authoritative` - that the ATTACHED APPS column
records *which clusters have ever been attached and not detached*, **not what an
app is using.** I established that the listing cannot answer "is this in use",
**then used the same listing to conclude these were not in use.** A source I had
proven non-authoritative in one direction, relied on in the other.
**The names did the rest of the work.** *"restored 2026-08-17... restored
2026-09-13..."* reads as debris. It is equally consistent with a project that
recovered twice and kept the result.

**Operational consequence, and it is the reason this is corrected rather than
softened: do not destroy either non-StockGrader cluster.** A cost argument ending
in *destroy the three idle clusters* is **one action away from deleting a live
production database on the strength of a name in a listing.**

**What survives:** four clusters exist, ready and billing; `-r1` is live and
`stockgrader-db` is ours and deliberately empty. **The other two are a question
for PharmFoldMDK's and Sentinel's own registers** - which cluster did each project
cut over to. If those registers answer it, it is a document read; if they do not,
**that gap is the finding and it is theirs.**
**Recorded as P-11 on the Planner's side. It is equally mine**, and the original
text stands below unedited so the inference is visible rather than tidied away.

### (original text, 2026-09-23, as written) - The account holds restore artifacts from earlier recoveries, still running
**Date:** 2026-09-23 - **By:** Builder, post-drill sweep
**Claim:** `fly mpg list -o matt-kelly-802` returns **four** clusters, all
`ready`, all on the `basic` plan, **all billed.** Two belong to StockGraderMDK.
The other two are **restore artifacts from PharmFoldMDK recoveries**, and their
names say so:

| ID | Name | Attached |
|---|---|---|
| `kyzl60xz9zyrpj9g` | `sentinel-holy-rain-4562 restored 2026-08-17… restored 2026-09-13…` | `pharmfoldmdk` |
| `zp2wjrej9lwodn4q` | `sentinel-holy-rain-4562 restored 2026-08-17…` | `sentinel-holy-rain-4562`, `pharmfoldmdk` |

**The first is a restore of a restore** - its generated name carries two restore
timestamps, five weeks apart.
**Why this is recorded here rather than left to the other project:** it is
**the exact failure mode this drill is at risk of**, already realised, visible
today. `fly mpg restore` builds a new cluster every time and **destroys nothing**;
the old one keeps running and keeps billing. Two recoveries produced two
survivors, and the generated names are the only record of what they were.
**It is also the argument for `-n`.** These clusters are identifiable only by a
concatenation of timestamps the platform chose. Our `stockgrader-db-r1` is
identifiable by reading it - which is why `-n` was adopted (ruling §3, 6.1).
**Already tracked** as testplan OPEN-6 (2026-09-22), *"out of scope for this
project."* **That remains true and is not the point.** The point is that the
project which last ran a restore has two orphans, and this project has just run
one. The scope boundary does not make the pattern someone else's problem.
**Consequence for B-9:** the PITR probe creates a genuinely disposable cluster.
B-9 says destroy it **immediately once the window is recorded**, and this finding
is why that clause is load-bearing rather than tidy.
**Sample:** 1 org, 4 clusters, 2 orphans.

### F-next/restore-carries-compromised-roles - A restore reproduces the source's security state, not just its data
**Date:** 2026-09-23 - **By:** owner (`fly mpg users list kzpwm0j1dm204nv3`),
framed by the Planner. Answers OPEN-24.
**Claim:** the restored cluster carries the source's **role catalogue**:

```
 NAME            │ ROLE
 fly-user        │ schema_admin
 stockgrader_app │ writer
 stockgradermdk  │ schema_admin
```

**Both credentials compromised on 2026-09-22 are live on the production cluster
with their original passwords.** `stockgrader_app` is the account the drill
created; the other two came across with the data.

**The general form is the one to keep:** **a restore reproduces the source's
security state, not just its data. A recovery from a compromise restores the
compromise.** That is not specific to Fly and it is not specific to credentials -
it is true of any state the backup captures and nobody thought to enumerate.

**What it makes false, recorded because a wrong register is worse than a known
risk:**
- **Ruling 6 is void.** The destroy retires **copies**, not originals.
- **D-029 has no closure path**, having rested on ruling 6.
- **The cutover's stated main purpose was not achieved.** The drill report says
  F-017's over-privilege is not rebuilt on the clean cluster. **There is no clean
  cluster.**

**What survives untouched: D-031.** The app connects as `stockgrader_app` at
`writer`, verified from the connection string's components. **The defect is the
residue, not the replacement.** Those are separable and conflating them would
discard real work.

**Why the Builder did not catch this:** the drill's step 5 listed **databases**
and confirmed both came across. Nothing in the written drill listed **users**,
and the Builder did not add it. The drill was written to prove the data path and
**verified exactly what it was written to verify.** A restore's blast radius is
wider than the thing you restored it for, and the check that would have caught it
is one line - `fly mpg users list` - placed next to the databases listing.
**Proposed amendment to §4: step 5 lists users as well as databases.**

**Risk, honestly:** the cluster is private-network-only. A credential alone buys
nothing without Fly organisation access, and anyone with that access does not
need the credential. **Probability of exploitation is low** and was low this
morning. **What changed is the deadline, not the risk** - see OPEN-25.
**Sample:** 1 restore, 3 roles, 2 carried compromises.

### F-next/continuity-caught-d9 - A second delivery lost, detected the same way, and one item reached us only by citation
**Date:** 2026-09-23 - **By:** Builder, reconciling D10
**Claim:** **delivery D9 never arrived** - both documents. D10 names
`MANIFEST-Planner-2026-09-23-...-D9.md` as its previous manifest; it is not on
this side, and nothing from its delivery is either.
**Artifact:** D10's stated check - *expected 24 on disk* - **returned 22.** The
shortfall is exactly D9's two documents. Second loss today, same detection.
**What D9 carried, inferred and not assumed:** **OPEN-24**, the item asking
whether the restore carried the role catalogue. The Builder **never held it**.
It is recorded retroactively in `testplan.md` from D10's citation of it.
**The thing worth keeping.** OPEN-24 was the right question and somebody asked
it. **The Builder did not** - the post-drill sweep looked at *clusters* and
missed *roles*, and the drill's step 5 listed databases only. Had D9 been the
last delivery of the day, **the register would have carried a false D-029 closure
path into the ticker load**, with the correcting question sitting in a document
that never arrived.
**This is `F-next/relay-loss-recurrence` with consequences attached.** That one
cost two deliveries of a stale open question. This one would have cost a wrong
security posture recorded as a right one. **The manifest chain caught both; the
difference in cost was luck, not guard strength.**
**Outstanding: [PLANNER] re-send D9 in full** - its manifest and its second
document, whose identity is unknown to us for the same reason as D4's.
**Sample:** 2 deliveries lost, 2 detected by continuity, 1 day.

### F-next/no-cli-path-to-a-recovery-credential - A non-attached account's password cannot be obtained from the CLI
**Date:** 2026-09-23 - **By:** Builder, answering OPEN-26 read-only
**Claim:** `fly mpg users create --help` in full exposes **three flags: `-h`,
`-r/--role`, `-u/--username`.** There is **no flag that emits a password, a
connection string, or any credential.** `set-role` is the same shape. Combined
with D-030's record that Fly secrets are write-only and nothing returns a value,
**no `fly mpg` command hands back a password.**

**The consequence the Planner traced, confirmed:** `stockgrader_app`'s credential
reached the password manager **through `fly mpg attach`** - a command that exists
to bind a database to an app, and prints the connection string as a side effect.
**That is the only observed route by which a password has left this platform.**
**A recovery account is by definition not attached to an app**, so that route is
not available to it.

**But Step 16 is not nominal - it is manual.** F-019 already established the
missing piece: **passwords are settable by a human in the Fly dashboard.** So a
replacement `schema_admin` **can** be obtained, by a path that is entirely
human-mediated:
1. `fly mpg users create <CLUSTER> -u <name> -r schema_admin` (CLI, prints
   nothing useful)
2. **set its password in the dashboard** (human, out of band)
3. store it in the password manager under the project name

**That is not a workaround; on this platform it is the mechanism.** F-019's
finding generalises further than it was written: **every credential this project
holds arrived either by a leak (F-014) or by a human typing it into a browser.**
There is no third route.

**Consequence for rotation, and it reframes D-030.** `fly mpg users` exposes
`create`, `delete`, `list`, `set-role` and **no rotate**. So rotating is
**delete-and-recreate**, or a dashboard password change. D-030's line - *a human
who needs a credential rotates it rather than looking it up* - **is not a
discipline. It is the only mechanism available.** Worth recording that way,
because a rule that reads as a choice invites someone to look for the lookup.

**`set-role` is a mitigation and must not be recorded as a fix.** Downgrading
`fly-user` from `schema_admin` to `reader` reduces blast radius and **does not
close an exposed password.**
**Unblocks:** OPEN-25's `fly-user` half - a replacement is obtainable, so the bad
trade in §5.4 is avoidable. **The replacement goes into the password manager
BEFORE anything is deleted.**
**Sample:** 3 `--help` outputs, 1 negative sweep of `fly mpg users`.

### F-next/migration-0001-proven-hermetically - The migration was proven on a local throwaway cluster, not on scratch
**Date:** 2026-09-23 - **By:** Builder, migration 0001 design block
**Claim:** migration 0001 and its verification were applied, verified and
**deliberately broken** against a **local PostgreSQL 18.3 cluster created in the
scratchpad and destroyed afterwards.** No Fly cluster was touched, no credential
was needed, and `stockgrader_scratch` was not mutated.
**Why not scratch, as the handover asked:** testing DDL against scratch needs a
`schema_admin`, and every `schema_admin` on the live cluster is compromised and
gated behind OPEN-25/OPEN-27. **D11 §4 also proposes dropping and recreating
`stockgrader_scratch` as part of OPEN-25** - so a scratch test run now would be
run against a database about to be replaced. The local cluster gives the same
evidence with none of that entanglement.
**What was established:**

| Property | Result |
|---|---|
| 0001 applies clean | 5 tables, 8 indexes, 1 extension, 1 ledger row |
| **Atomicity** - a failure partway leaves nothing | **0 tables** after a deliberately broken run |
| **Forward-only** - re-running fails loudly | `ERROR: relation "filer" already exists` on the first statement |
| Verification Parts A, B, C | all pass on a correct schema |

**Every guard was then seen to go red** (F-002's standard, applied to schema):

| Defect injected | Caught by |
|---|---|
| The tempting key `UNIQUE(concept, period, unit)` | **A4** |
| Ticker exclusion constraint dropped | A5 |
| `filing_date` made nullable | A6 |
| `fact -> filing` FK dropped | A7 |
| `instant`-is-a-point check dropped | C4 |
| **Overwrite-on-amendment** (TDD §13's named defect, via trigger) | **B1** |
| **Lookahead** - amendment back-dated before its filing | **B1** |

**Two results worth stating precisely rather than rounding up:**
**The overwrite defect was caught by B1, not B2.** The overwrite deletes the
original, so the point-in-time query returns NULL before the row-count check runs.
**Two independent checks cover it**, which is better than the one that was
designed for it - but the report says which fired, because "B2 caught it" would
be false.
**The first trip harness reported all five guards blind.** That was the harness,
not the guards: `PGBIN` contains a space and unquoted expansion broke every
`psql` call, so the grep matched nothing and every result read GREEN. **A test
harness that cannot run reports the same thing as a system with no defects.**
Fixed by adding a sanity check that the harness itself works before any verdict
is trusted. Recorded because the failure direction was silent and favourable,
which is the dangerous combination.
**Sample:** 1 local cluster, 7 injected defects, 7 caught.

### F-next/citations-are-lossy-recovery - A citation carries what the citing author needed, not what the document contained
**Date:** 2026-09-23 - **By:** Builder; **elevated on the Planner's instruction**
from a reconciliation note in `F-next/continuity-caught-d9` to a standing finding.
**Claim:** when a delivery is lost, the apparent recovery route - **reading what
later documents cite of it** - is **systematically lossy, and lossy invisibly
from the citing side.**
**The instance that proves it.** D9 was lost. The Builder worked for two
deliveries from D10's citations of it and got most of it right. **D9 §3 held the
migration/`schema_admin` collision** - that `writer` cannot `CREATE TABLE`, so
migration 0001 cannot run as the app account and needs a `schema_admin`, all of
which are compromised. **Nothing cited it.** It became OPEN-27, the most
consequential item in the document, and the Builder **had no way to know it
existed** until the re-send arrived.
**Why the loss is invisible:** a citing author quotes what **their** argument
needed. They are not summarising, and they have no reason to think anything is
missing - the document is in front of them. **The gap is undetectable from
either end**: the citer sees a complete document, the reader sees a coherent
citation. Nothing looks wrong.
**How it sits with the manifest chain.** The chain **detects** a missing delivery
and **bounds its size** - it did that twice today. **It does not recover
contents, and this finding is why the difference matters.** A recovered size is
not a recovered document.
**Rule adopted:** working from citations while waiting for a re-send is
reasonable and **must be marked provisional.** The register carries **which
entries were made at second hand** until the document arrives, and they are
revisited when it does.
**Sample:** 1 lost delivery, 2 deliveries of second-hand work, 1 item missed
entirely.

### F-next/duplicate-suffix-now-ambiguous - The `(1)` suffix means two different things in the same folder
**Date:** 2026-09-23 - **By:** Builder, reconciling D12
**Claim:** the delivery folder now contains **three** files whose names end in
` (1)`, and they are **not the same kind of thing**:

| File | What it is |
|---|---|
| `RULING-RECORD-...-owner-rulings (1).md` | **A real document** - the 07:32 revision, D2 entry #6 |
| `MANIFEST-...-D12 (1).md` | A duplicate download, byte-identical |
| `RULING-...-open27-order-with-proof-step (1).md` | A duplicate download, byte-identical |

**The near-miss:** the first count excluded every ` (1)` file and returned
**27 against an expected 28** - a false shortfall that would have been reported
as a lost document. Excluding the two confirmed byte-identical duplicates instead
returns **28**, which matches.
**Root cause is P-4's residue.** The browser's ` (1)` was harmless when it always
meant *duplicate*. P-4 made it also mean *superseding revision* for one file, and
the filename-is-not-identity rule fixed the Planner's side going forward **but
left that one artifact behind.** The ambiguity is permanent in this folder.
**Rule adopted:** reconciliation **never filters by filename pattern.** It
**diffs** suspected duplicates and excludes only those confirmed byte-identical.
Two commands, no inference.
**Why record a near-miss that cost nothing:** the failure direction was a
**false positive** - reporting a loss that did not happen. That is the benign
direction today, and it is the direction that **erodes trust in the check
itself**, which is how a real shortfall later gets waved through as another
counting artifact.
**Sample:** 1 folder, 3 suffixed files, 2 meanings.

### F-next/guard-fired-on-its-own-correct-file - The transaction-control guard's first act was a false positive
**Date:** 2026-09-23 - **By:** Builder, building the migration runner
**Claim:** the runner refuses any migration or verification file containing
transaction control - the guard D-021's PharmFoldMDK §3.1 rationale demands.
**The first time it ran, it rejected 0001's own verification file**, which is
correct, on `END;`.
**Why it was wrong:** the `END;` was the terminator of a PL/pgSQL
`BEGIN ... EXCEPTION ... END;` block inside a `DO $$ ... $$` body - **block
structure, not transaction control.** At top level PostgreSQL does treat `END`
as a synonym for `COMMIT`, so the keyword genuinely is ambiguous; the context is
what disambiguates it.
**Fix:** strip **dollar-quoted bodies** before scanning, alongside comments. A
`$$ ... $$` body is precisely the construct in which `BEGIN`, `END` and
`EXCEPTION ... END;` appear legitimately, so removing it leaves only top-level
statements - where those keywords can only mean transaction control.
**Why this is recorded rather than quietly fixed.** The failure direction was
**false positive: a correct file refused.** That reads as the safe direction and
it is not. **A guard that cries wolf on correct work gets switched off**, and a
switched-off guard protects nothing - so a false positive on day one is how a
real protection is lost by month three. The hermetic test
`test_plpgsql_block_is_not_mistaken_for_transaction_control` exists to hold the
line in that direction specifically, and it was written **before** the defect
appeared without anticipating this particular case.
**Caught by:** `test_the_real_migration_files_contain_no_transaction_control`,
which asserts the shipped files satisfy their own runner. That test is the one
that turns "the guard works" into "the guard works on what we actually ship."
**Sample:** 1 guard, 1 false positive, 1 file.

### F-next/migration-runner-proven - The runner is built and every guard has been seen red
**Date:** 2026-09-23 - **By:** Builder, OPEN-28
**Claim:** `db/migrate.py` implements D-021. Proven end to end against a local
PostgreSQL 18.3 cluster created in the scratchpad and destroyed after - **no Fly
cluster, no credential, no `stockgrader_scratch`.**

**Behaviour established:**

| Property | Evidence |
|---|---|
| `status` / `plan` are read-only; `apply` is explicit | `plan` is the safe default posture and prints what would run |
| Applies 0001 | 5 tables, ledger row carries the **real** sha256, not the placeholder |
| Idempotent | second `apply` reports *nothing to apply* |
| **Verification fixtures leave no trace** | `SELECT count(*) FROM filer` = **0** after a successful apply |
| **A failed verification takes the migration with it** | deliberate `RAISE EXCEPTION` in verify: **0 tables, 0 ledger rows** |
| **A changed migration file is refused** | appended one comment line; runner reported recorded vs on-disk sha256 and stopped |
| **Transaction control is refused before connecting** | `COMMIT;` appended to 0001; refused while pointed at an unreachable DSN |
| Forward-only, gaps, duplicate versions, bad filenames | 21 hermetic tests |

**The savepoint arrangement is the part worth naming.** The verification runs
inside `SAVEPOINT verification`, which is rolled back afterwards: **the fixtures
vanish and the DDL survives to COMMIT.** A failed check raises before that
rollback, so the whole transaction unwinds and the migration goes with it.
**That makes "the migration ran" and "the schema is right" the same claim** -
which is D-005's shape applied to schema, and the thing D-021 was written to get.

**Deliberate departures from D-021's letter, both stricter:**
- `pg_advisory_xact_lock` rather than session-scoped - pooler-safe, and released
  by COMMIT or ROLLBACK with no unlock for a crash to skip.
- **The ledger belongs to the runner, not to 0001.** A migration that creates the
  ledger cannot be recorded until after it creates it, and a migration that
  records its own application can record it wrongly. The runner writes version,
  name and real checksum **in the same transaction as the DDL.**

**Suite: 22 -> 43 tests**, all hermetic. **The DB-dependent behaviour above is
not in the gate** and belongs to the non-hermetic track; a hermetic green is not
evidence that a migration applies.
**Sample:** 1 runner, 1 local cluster, 7 guard trips.

### F-next/entity-missing-from-fact-key - The fact key omitted the XBRL context's entity, and co-registrants would have vanished
**Date:** 2026-09-23 - **By:** Planner (OPEN-29), confirmed and fixed by Builder
**Claim:** 0001's uniqueness key carried accession, taxonomy, concept, unit,
period and dimensions - **and not the context's entity identifier.** An XBRL fact
is identified by concept, unit and **context**, and a context carries an
**entity** as well as a period and dimensions. The key was missing one component
of the thing it claimed to key on.
**Where it bites:** one submission can hold facts for several entities -
co-registrants, parent-and-guarantor structures, REIT operating partnerships,
multi-registrant trusts. Two entities reporting `Revenues` for the same period in
USD with no dimensions differ **only** by entity. Under the old key they
collided, and `ON CONFLICT DO NOTHING` - which the design correctly treats as
idempotency - **would have discarded the second entity's fact and called it a
re-ingest.**
**That is the failure this schema exists to refuse:** a fact disappearing with no
evidence it ever arrived. The key built to make overwrite-on-amendment impossible
had a second, quieter hole in it.
**The asymmetry that makes it obvious in hindsight:** `dimensions` was stored
rather than discarded on the explicit reasoning that *a schema that cannot
represent the distinction cannot refuse it.* **The entity is the same argument
one level up**, and the design applied it to dimensions while missing it for
entity.
**Fixed:** `entity_cik bigint NOT NULL REFERENCES filer (cik)`, **in the key**.
Legitimate to amend 0001 rather than write 0002 because **0001 has never been
applied to any real database** - only to local throwaway clusters since
destroyed. Forward-only constrains *applied* migrations.
**Query consequence, recorded in the column comment because it is easy to get
wrong:** *"this company's revenue"* filters on `fact.entity_cik`, **not**
`filing.cik`. Filtering on `filing.cik` returns a parent's co-registrants' facts
as though they were the parent's. The verification's own point-in-time queries
were rewritten accordingly - they had the bug.
**Caught, and by two independent checks:**
- **A8** - structural: the key must contain `entity_cik`. Reintroducing the old
  key fails A8 and leaves **0 tables**.
- **B5 / the fixture** - behavioural: with A8 removed, the co-registrant fixture
  itself raises `UniqueViolation`, and the DETAIL line names the key that is
  missing the column. **0 tables** again.
**Sample:** 1 key, 1 missing component, 2 independent catches.

### F-next/a-check-that-could-not-fail - The leak check was tautological and proved nothing
**Date:** 2026-09-23 - **By:** Builder, revising 0001's verification
**Claim:** B1's leak check read
`WHERE filing_date <= D AND filing_date > D`. **That is empty by construction,
whatever the data contains.** It could not fail, so it proved nothing - while
sitting in a file whose whole premise is that every check can be made to go red.
**Why it survived the first review:** it *reads* like a negative assertion -
*nothing filed after the boundary may appear* - and the shape of the sentence is
right. The defect is in the logic, not the intent, and a reviewer checking
intent finds nothing wrong.
**Same family as `F-next/tolerated-error-hides-real-error` and the trip harness
that reported five guards green while running nothing:** a thing that reports
success without doing work. **This project has now found that shape three times
in one day, in three different systems** - a counter, a test harness, and a SQL
assertion.
**Replaced with a check that reads the data and can go red:** count what the
as-of window admits and assert it is exactly the one pre-boundary row, then
assert the newest filing it admits really is at or before the boundary.
**Rule reinforced:** *a guard never seen red is not a guard* is not only about
running the trip test. **A check must be capable of failing in principle before
trying to make it fail is meaningful.**
**Sample:** 1 check, 0 possible failures.

### F-next/ticker-file-seeding-reintroduces-survivorship - The ordered retrieval path would have rebuilt the bias ruling 5 closed
**Date:** 2026-09-23 - **By:** Builder, establishing §4 of the ingest slice-1 handover
**Claim:** the handover's §3 seeds `filer` rows from
`company_tickers.json` / `company_tickers_exchange.json` and then fetches EDGAR
submissions **per CIK**. Taken literally, **that produces a universe containing
only currently-listed companies**, which is survivorship bias - the exact defect
ruling 5 exists to close.
**Measured, not argued.** `company_tickers.json`, fetched 2026-09-23:
**10,461 entries, 8,049 distinct CIKs.**

| Filer | CIK | In ticker file |
|---|---|---|
| Lehman Brothers Holdings | 806085 | **no** |
| Sears Holdings | 1310067 | **no** |
| Bed Bath & Beyond | 886158 | **no** |
| Enron | 1024401 | **no** |
| Apple *(control, still listed)* | 320193 | yes |

**A universe seeded from this file can never contain a company that stopped
trading**, so *"which CIKs had filed a 10-K in the three years before D"* - the
question §3 says the slice exists to answer from data - **would return a
survivorship-filtered answer that looks computed.** That is worse than an
asserted one, because it carries the authority of having been derived.
**This is the register's own prior reasoning, now with evidence.**
`gqs-source-map.md` §9 already recorded that the ticker files are *current*
universes; ruling 5 already ruled the historical universe comes from filing
history. **The handover's retrieval path contradicted both**, and would have
passed review because per-CIK submissions is the obvious way to get submissions.
**Second, smaller reason the per-CIK path is wrong for this:** SEC documents the
per-CIK endpoint as returning *"at minimum one year of filings or the 1,000 most
recent filings"*, with older filings in separate paginated files. **Full history
is not one request per CIK**, so the crawl is both incomplete and larger than it
appears.
**Established alternative:** `submissions.zip` - **the public EDGAR filing
history for all filers**, one archive, refreshed nightly ~03:00 ET.
1,565,081,455 bytes, `Last-Modified: Wed, 23 Sep 2026 04:31:05 GMT`, confirmed by
a `HEAD` request. **All filers** means dead ones are in it.
**Proposed correction, and it restores ruling 5 rather than departing from it:**
- `filer` + `filing` from **`submissions.zip`** - the universe, dead companies included
- `filer_ticker` from **`company_tickers*.json`** - the current-day identifier
  crosswalk, **which is exactly what ruling 5 says the ticker files are for**
**Sample:** 1 ticker file, 8,049 CIKs, 4 known-dead filers absent, 1 control present.

### F-next/edgar-limits-established - EDGAR's published rate limit and User-Agent format, from the SEC
**Date:** 2026-09-23 - **By:** Builder, establishing §4
**Claim:** D-023 requires *"a hard client-side rate limit"* and A-004 depends on
*"request rates within SEC limits"*. Neither named a number. **The SEC publishes
one:**
> *"our current maximum access rate is 10 requests per second. This is carefully
> monitored to preserve equitable access for all users."*

**User-Agent format, also published:**
> `User-Agent: Sample Company Name AdminContact@<sample company domain>.com`

**Artifact:** SEC webmaster FAQ / developer guidance, retrieved 2026-09-23.
**Why recording the number matters more than honouring it:** §4 asked for *"a
bound you can point at, not a sleep someone guessed."* A guessed sleep that
happens to be slower than the limit is indistinguishable from a correct one until
the limit changes - and then it is indistinguishable from a correct one that has
silently become wrong.
**Consequence for the retrieval path:** at 10 req/s a per-CIK crawl of 8,049
current CIKs is ~13 minutes of sustained requests **and still misses every dead
filer**. `submissions.zip` is **one** request. The bulk route is not only correct
under ruling 5, it is also the one that does not spend the rate limit.
**Sample:** 1 published limit, 1 published format.

### F-next/sic-at-filing-has-no-source-in-slice-1 - The column is right; the data for it is not in the ruled source
**Date:** 2026-09-23 - **By:** Builder, establishing OPEN-32
**Claim:** `filing.sic_at_filing` exists so a 2014 backtest does not read 2026's
classification. **The ruled source cannot fill it.**
**Artifact:** `https://data.sec.gov/submissions/CIK0000320193.json`, fetched
2026-09-23. `submissions.zip` carries the same per-filer documents.
- **Entity level carries SIC:** `sic: 3571`, `sicDescription: Electronic Computers`.
  **This is the filer's CURRENT classification.**
- **Per-filing columns carry none:** `acceptanceDateTime, accessionNumber, act,
  core_type, fileNumber, filingDate, filmNumber, form, isInlineXBRL, isXBRL,
  isXBRLNumeric, items, primaryDocDescription, primaryDocument, reportDate, size`.
  **No SIC field of any kind.**
**Resolution, per the ruling and it is the right one: `sic_at_filing` stays
NULL in slice 1**, with the reason recorded here. The entity-level `sic` maps to
**`filer.current_sic`**, which is exactly what that column is named for and where
it is honest.
**Why filling it from the entity SIC would have been the worst option:** it puts
**today's** classification into a column whose entire name asserts it is not
today's, and it would be **invisible forever after** - every downstream reader
would take it as point-in-time because the schema says so. **A column that is
honestly empty is recoverable. A column quietly filled with the wrong thing is
the fifth instrument.**
**Still open:** whether per-filing SIC exists in the filing header or in the
Financial Statement Data Sets. Not established, not assumed. Slice 1 does not
need it.
**Sample:** 1 filer document, 16 per-filing columns, 0 carrying SIC.

### F-next/per-cik-history-is-paginated - Direct evidence that the per-CIK route is incomplete
**Date:** 2026-09-23 - **By:** Builder, establishing OPEN-32
**Claim:** the per-CIK submissions document for Apple carries a `files` array:
```
[{"name": "CIK0000320193-submissions-001.json",
  "filingCount": 1249, "filingFrom": "1994-01-26", "filingTo": "2015-07-25"}]
```
**1,249 filings covering 1994-2015 are in a separate document.** The main
response's `recent` array begins where that one ends.
**Why this is recorded separately from the survivorship finding:** it is an
**independent disqualification** of the per-CIK path. Even for a filer that *is*
in the ticker file, one request does not return its history - and **the
incompleteness hides inside the size**, because the response is 164 KB and looks
complete. Either finding alone rules the path out; two independent ones are more
durable than one.
**Sample:** 1 filer, 1 pagination file, 1,249 hidden filings.

### F-next/incremental-path-is-the-daily-index - The second run need not be another 1.56 GB
**Date:** 2026-09-23 - **By:** Builder, establishing §7
**Claim:** EDGAR publishes **daily index files** at
`https://www.sec.gov/Archives/edgar/daily-index/YYYY/QTRn/master.YYYYMMDD.idx`,
one per business day. Confirmed present through `master.20260922.idx`.
**Columns:** `CIK, Company Name, Form Type, Date Filed, File Name`.
**So the shape is:** `submissions.zip` **once** for history; the daily index
**thereafter**. The archive refreshes nightly, but re-downloading it nightly is a
choice rather than a requirement - which is what §7 asked.
**The gap, stated rather than discovered later:** the daily index carries **no
`reportDate`**, so it cannot populate `filing.period_of_report`. The incremental
path is therefore *daily index -> the set of CIKs that filed that day -> per-CIK
submissions for **only those CIKs***. That set is hundreds per day, not 8,049, so
it fits inside the 10 req/s bound comfortably. **The per-CIK endpoint is wrong as
a universe source and fine as an incremental detail source** - the two uses are
not the same and ruling it out for one does not rule it out for the other.
**Sample:** 1 index directory, 1 sampled file, 5 columns.

### F-next/an-instrument-can-be-promoted-without-being-changed
**Date:** 2026-09-23 - **By:** Builder, accepted and sharpened by the Planner as
the more useful half of the §2 doctrine
**Claim:** `/healthz` belongs on the list of five instruments that could not
report the condition they existed to detect - **but it is not a defect.** It
returns 200 and a build SHA, opens no database connection, and does exactly what
it was written to do.
**It joins the list because the question being asked of it changed.** It became
the thing standing between us and recovery-table Row 4, while the instrument
stayed the same.
**The general form:** **any check acquires new load when the thing it is nearest
to becomes important, and nothing in the check announces that it has been
promoted.** The other four were built wrong. This one was built right and then
asked a question it was never designed to answer.
**Why it is the more useful half:** **no code review catches it, because there is
nothing wrong with the code.** Reviewing the check finds a correct check.
Reviewing the caller finds a reasonable call. The defect exists only in the gap
between what the instrument measures and what someone has started concluding
from it - and that gap is not visible in any single file.
**How to look for it:** when a check becomes load-bearing for a *new* claim, the
question is not *does it pass* but **what would it do if the new claim were
false.** `/healthz` would return 200 against a dead database, which is how we
know Row 4 was never proven.
**Sample:** 5 instruments, 4 defects, 1 promotion.

### F-next/slice1-proves-ruling-5-end-to-end - The dead filer is in the universe and absent from the crosswalk
**Date:** 2026-09-23 - **By:** Builder, ingest slice 1
**Claim:** slice 1 is built and proven on a local PostgreSQL 18.3 cluster,
destroyed after. **No Fly cluster, no credential, no `stockgrader_scratch`.**
**The proof that matters is ruling 5 working end to end**, with a fixture shaped
like the case that motivated it. CIK **806085** (Lehman Brothers Holdings) has a
10-K filed 2008-01-29 and **no ticker row**:

```
2008 10-K universe, keyed on CIK alone: [806085]
Lehman rows in the ticker crosswalk:    0
```

**The filer is in the universe and absent from the crosswalk, simultaneously.**
That is the whole design in one result: the universe comes from filing history,
so a company that stopped trading is still in the year it filed; and the ticker
file's current-only nature - the thing that would have caused the bias - **costs
nothing**, because it is used only as an identifier crosswalk.

Had slice 1 been built on the handover's original inputs, that row could not
exist and the query would have returned an empty 2008 universe **without
erroring**.

**Also proven:**

| Property | Result |
|---|---|
| **Double-ingest idempotency** | run 1 and run 2 both `{filer: 2, filing: 3, filer_ticker: 1}` - identical |
| **`sic_at_filing` honestly NULL** | 0 filings carry one; `filer.current_sic` populated (3571, 6211) |
| **Scheme refusal, live** | an ISO 17442 LEI identifier is **refused**, not coerced |

**Idempotency is the schema's, not the loader's.** Every insert is
`ON CONFLICT DO NOTHING` against a real constraint, so re-running changes nothing
as a property of the keys rather than of bookkeeping in the client.

**Schema change this forced, and it is worth recording as a design consequence
rather than a fix:** `filer_ticker` gained
`PRIMARY KEY (cik, ticker, valid_from)`. **`ON CONFLICT` requires a unique index
and an EXCLUDE constraint is not one**, so without it a re-run raises instead of
being a no-op - and idempotency would have had to be faked in the client, which
is the wrong place for it. The two constraints now do different jobs: the PK
forbids the same pairing starting twice, the EXCLUDE forbids one ticker
resolving to two CIKs at once. **Range overlap is not equality and neither
constraint can express the other.**

**NOT claimed, per the handover's §5:** **this does not exercise A8.** Slice 1
writes no facts, so `entity_cik` is never written here. A8 and the co-registrant
fixture remain the only evidence for OPEN-29's fix.
**Sample:** 1 local cluster, 2 filers, 3 filings, 4 proofs.

### F-next/ticker-crosswalk-has-no-start-dates - `valid_from` is an observation date, not a beginning
**Date:** 2026-09-23 - **By:** Builder, ingest slice 1
**Claim:** `company_tickers.json` records which ticker a CIK has **today**. It
carries **no start date**. So `filer_ticker.valid_from` is stamped with the date
the pairing was **observed**, and `valid_to` is NULL because it is current.
**The consequence, stated now rather than discovered by a wrong backtest:** a
historical ticker lookup against these rows **returns nothing before the first
observation**. Asking *"which CIK was SYNTH in 2014?"* of crosswalk data first
seen in 2026 is a question the data cannot answer, and the schema will correctly
say so rather than guess.
**Why stamping the observation date is right and inventing a start is not:** a
plausible `valid_from` - the filer's first filing, say - would be **indis-
tinguishable from a real one** and would make the range constraint enforce a
history we made up. An honestly narrow range is recoverable when a real source
arrives; a fabricated one is not, because nothing marks it as fabricated.
**Consequence for the design, and it is reassuring rather than alarming:** this
is exactly why **ruling 5 keys the universe on CIK.** Nothing in the point-in-
time path depends on historical ticker resolution. The gap is real and it is
outside the load-bearing path.
**Open:** recovering true ticker validity ranges needs a source we do not have.
Not needed by slice 1 and not pretended.
**Sample:** 1 ticker file, 0 start dates.

### F-next/0002-provenance-keyed-on-the-event - A fetch is a moment, not a property of a URL
**Date:** 2026-09-24 - **By:** Builder, migration 0002 (OPEN-34)
**Claim:** `fetch_log` is keyed on **`(url, retrieved_at)`**. Not `(url)`, and
not `(url, sha256)`.
**`(url)` is the key that looks right** - one row per thing we fetched - and it
is 0001's defect in a new table. It permits exactly one row per URL, so a second
fetch can only be stored by overwriting the first, **destroying the history of
retrievals and with it the only evidence of when a payload changed.**
**`(url, sha256)` is subtler and also wrong.** It collapses repeated identical
fetches into one row, discarding the most useful thing an unchanged re-fetch
tells you: **the resource was still unchanged at a later moment.** That is not a
duplicate. It is a second observation, and it **bounds the window in which a
change did not happen.**

**What the chosen key makes impossible:**
1. **Losing a retrieval by re-fetching.** Every fetch is an event; every event
   gets a row.
2. **Answering *what did this URL contain?* as though that were a property of
   the URL.** It is a property of a **moment**, and the schema will only answer
   it that way.
3. **Two fetches being indistinguishable.** Same URL, same bytes, different
   instant - two rows, correctly.

**The two cases D16 §2.5 asked about, and which is a finding - proven, not
argued:**

| Case | Result | Finding? |
|---|---|---|
| Same URL, **same** payload, twice | 2 rows, 1 distinct hash, **0 flagged** | **No.** Evidence of non-change. |
| Same URL, **different** payload | 2 rows, 2 distinct hashes, **surfaced** | **YES.** |

**The second is the finding because it retroactively falsifies D-023.** *Accession
plus hash makes any row re-derivable* becomes **false** for every row derived
from the superseded payload - that payload no longer exists anywhere. The
`fetch_content_change` view surfaces it.

**Deliberately a view, not a constraint or a trigger.** A changed payload is a
**real-world event, not corruption.** A constraint rejecting it would simply stop
us recording the truth, and a trigger would have to decide what to do at write
time when the only correct answer is *tell a human*.
**Sample:** 1 URL, 3 retrievals, 2 payloads, 1 finding.

### F-next/0002-refuses-to-backfill - The migration encodes its own unretrofittability
**Date:** 2026-09-24 - **By:** Builder, migration 0002
**Claim:** 0002 adds `source_fetch_id` as **NULL**, inspects for rows that have
none, and **RAISES if any exist** - taking the whole migration down with it.
It never backfills.
**Why refusing is the only honest option.** A provenance row describes a fetch:
its URL, its moment, and the hash of what came back. **Once a fetch has happened
unrecorded, that record cannot be reconstructed** - not from the database, not
from EDGAR, not from anything, because **re-fetching produces a new fetch rather
than evidence of the old one.** Any value invented here would be **a fabricated
fetch behind real data, indistinguishable from a real one forever after** - the
same class as a fabricated ticker `valid_from` (OPEN-35) and the same class as
filling `sic_at_filing` from the entity's current SIC (OPEN-32).
**Why it is worth encoding rather than asserting.** D16 §2.1's argument for
doing provenance *before* the fact slice is that it is unretrofittable. **A
comment saying so is a claim; a migration that stops rather than improvise is the
property.** Proven live: dropping the NOT NULL, inserting one legacy row and
re-running the block returns
*"0002 REFUSES TO BACKFILL: 1 row(s) exist that were loaded before provenance was
recorded."*
**NOT NULL is the other half.** After the check passes, the columns are set NOT
NULL on all three tables, so **an unprovenanced row stops being representable** -
not discouraged, not conventionally avoided, **impossible**.
**Sample:** 1 refusal block, 1 injected legacy row, 1 refusal.

### F-next/fetch-is-a-reserved-word - The table name was caught by running it, not by reading it
**Date:** 2026-09-24 - **By:** Builder, migration 0002
**Claim:** `CREATE TABLE fetch` is a **syntax error** in PostgreSQL. `FETCH` is
a reserved word (`FETCH FIRST n ROWS`), so the table cannot be named that without
quoting every reference to it forever. Renamed **`fetch_log`**.
**Why it is recorded at all:** the file had been written, read back, and
reviewed - the name appeared in a heading, a table definition, three foreign
keys, a view, two indexes and a comment block - and **nothing about it looked
wrong**, because it is the obviously correct English word for the thing. The
error surfaced **the first time the migration was executed**, at
`LINE 89: CREATE TABLE fetch (`.
**The general form:** **reserved-word collisions are invisible to review and
instant under execution**, and they get more expensive the later they are found -
this one cost a rename before any data existed; found after ingest it would have
cost a migration. It is an argument for the local throwaway cluster being
*cheap* rather than merely *available*.
**Incidental confirmation:** the runner applied 0001, committed it, then failed
0002 and rolled it back with the ledger unwritten. **Per-migration atomicity,
demonstrated by accident on a real failure** rather than by an injected one.
**Sample:** 1 reserved word, 9 references, 1 execution to find it.

### F-next/companyfacts-cannot-exercise-the-schema - The convenient source makes two columns permanently trivial
**Date:** 2026-09-24 - **By:** Builder, establishing the fact-slice sources (D16 §3)
**Claim:** the XBRL **Company Facts / Company Concept** API - and therefore
`companyfacts.zip`, which the SEC documents as containing exactly that data -
**carries no dimensions and no per-fact entity identifier.**
**Artifact:** `companyconcept/CIK0000320193/us-gaap/AccountsPayableCurrent.json`,
fetched 2026-09-24. The union of every per-fact key across all 142 facts is:

```
accn, end, filed, form, fp, frame, fy, start, val
```

| D16 §3 requirement | companyfacts |
|---|---|
| Dimensions | **ABSENT** |
| Per-fact entity identifier | **ABSENT** - CIK appears once, at the top level: the one you asked for |
| Accession per fact | present (`accn`) |
| Filing date per fact | present (`filed`) |
| Amendment history | **present, and rich** - see below |

**This is precisely the trap D16 §3.1 named**, confirmed rather than feared:
*a source that returns only consolidated, no-dimension facts keyed by the CIK you
asked for would make `dimensions` and `entity_cik` permanently trivial - the
schema right and the data unable to exercise it.*
`entity_cik` would equal the requested CIK on every row. `dimensions` would be
`'{}'` on every row. **A8 and the co-registrant fixture would remain the only
evidence for OPEN-29's fix forever**, because no ingested row could ever
contradict them.

**Worse than missing, on one point.** 61,122 facts in a single quarter belong to
a **co-registrant** rather than the filer (see the FSDS finding). Whether
companyfacts excludes those or returns them attributed to the requested CIK is
**unestablished** - and if it is the latter, the source does not merely omit the
distinction, it records the wrong entity. Not asserted; flagged.

**What it IS good for.** Amendment history is present and exactly the shape
§5.1 needs: **18 of 69 periods are reported by more than one accession**, each
with its own `accn`, `filed` and `form`. Apple's FY2009 `AccountsPayableCurrent`
appears under a 10-K (2009-10-27), a 10-K/A (2010-01-25) and three subsequent
10-Qs - five separate assertions of one period, distinguishable by filing date.
**That is the point-in-time property available as data.**
**Size/cadence:** 1,409,389,023 bytes, `Last-Modified: Thu, 24 Sep 2026
04:24:14 GMT` - refreshed nightly, like `submissions.zip`.
**Sample:** 1 concept, 142 facts, 9 distinct keys.

### F-next/fsds-carries-dimensions-and-coregistrants - The source that can exercise the schema
**Date:** 2026-09-24 - **By:** Builder, establishing the fact-slice sources
**Claim:** the **Financial Statement Data Sets** carry everything companyfacts
does not. Measured on `2026q2.zip` (60,419,016 bytes), not read from
documentation:

| Field | Where | Populated |
|---|---|---|
| `segments` - **dimensions** | `num.txt` | **2,189,835 of 3,608,711 rows = 60.7%** |
| `coreg` - **per-fact entity** | `num.txt` | **61,122 rows = 1.69%** |
| `sic` - **per-SUBMISSION SIC** | `sub.txt` | **7,524 of 7,714 = 97.5%** |
| `nciks` / `aciks` - co-registrant CIKs | `sub.txt` | 131 submissions have `nciks > 1` |
| `adsh`, `filed`, `period`, `form` | `sub.txt` | present |
| `prevrpt` - superseded flag | `sub.txt` | 3 rows |

Example `segments` values: `EquityComponents=CommonStock;`,
`EquityComponents=AdditionalPaidInCapital;`.
Example co-registrant submission: `adsh=0000004904-26-000034 cik=4904 nciks=8`
with seven additional CIKs.

**60.7% is the number that settles §3.1.** Ingesting from companyfacts would not
lose a rare edge case - **it would discard the majority of the facts filers
publish**, and it would do so invisibly, because what remains looks like a
complete consolidated dataset. v1 filters `dimensions = '{}'` by design, but
**filtering data you have is a decision; not having it is a ceiling.**

**THE COST, and it is real: cadence.** `2026q2.zip` covers filings from
2026-04-01 to 2026-06-30 and was published **2026-08-19** - a **~50-day lag**
from quarter end. Against `companyfacts.zip`, refreshed **nightly**.
So the two sources trade completeness against freshness, and **neither dominates**:
- FSDS: complete, quarterly, ~50 days stale at publication
- companyfacts: nightly, and structurally incapable of carrying dimensions or
  co-registrants

**Not proposing a design** - that is the Planner's, and P-10 is what happens when
sources are chosen without citing the ruling they satisfy. Reported as the
trade-off the handover has to resolve.
**Sample:** 1 quarterly set, 3,608,711 fact rows, 7,714 submissions.

### F-next/sic-at-filing-has-a-source-after-all - OPEN-32's open half, answered
**Date:** 2026-09-24 - **By:** Builder, establishing the fact-slice sources
**Claim:** OPEN-32 closed the slice-1 question - the submissions document carries
SIC at **entity level only**, so `filing.sic_at_filing` stays NULL there - and
left one half open: *whether per-filing SIC exists in the filing header or in the
Financial Statement Data Sets.* **It is in the FSDS.**
`sub.txt` carries **`sic` per submission**, populated on **7,524 of 7,714 rows
(97.5%)** in 2026q2, alongside `adsh` - so it joins directly to `filing.accession`.
**The Planner's third hypothesis was the right one**, and it was worth listing as
a hypothesis rather than guessing: the answer was neither of the first two.
**Consequence:** `sic_at_filing` is **fillable**, but **not from slice 1's ruled
source**. It stays NULL until an FSDS-based load exists, and the column remains
honestly empty rather than wrong in the meantime - which is exactly why leaving
it NULL was right rather than merely cautious.
**Not yet established:** whether `sub.txt.sic` is the SIC *as filed* or the
filer's SIC *as of extract time*. The 97.5% population rate says the field is
real; it does not say which of those two it means, and **that distinction is the
entire reason the column exists.** Must be established before it is populated.
**Sample:** 1 quarterly set, 7,714 submissions.

### F-next/an-expectation-is-what-makes-a-count-a-check
**Date:** 2026-09-24 - **By:** Planner, sharpening the Builder's two near-misses
**Claim:** the delivery count has now caught **the Builder's method twice** -
once a duplicate-classification loop that returned 8 against 3 candidates, once a
filename filter that returned 56 against 36 by sweeping in a different day's
documents. **Neither was caught by the count. Both were caught by the count
disagreeing with a figure stated in advance.**
**The general form, and it is stronger than the argument for counting:**
**a count with no prior expectation cannot catch a method error.** It runs, it
produces a number, the number looks like an answer, and **nothing disputes it**.
The expectation is what converts a measurement into a check - it supplies the
second opinion that a single measurement structurally cannot.
**This is the seventh instance of the instrument pattern** and the second in
which the failing instrument was **the Builder's own verification method** rather
than the thing being verified. Both times the method **ran cleanly**. Both times
the output was well-formed. **A filter that runs cleanly still returns a
number.**
**Rule, now standing on both sides:** every manifest states the expected figure
in advance; the receiving side runs the count and compares. It costs one line and
has earned its place twice.
**Sample:** 2 method errors, 2 caught by disagreement with a prior expectation,
0 caught by the count alone.

### F-next/review-and-execution-catch-disjoint-defects - PROVISIONAL
**Date:** 2026-09-24 - **By:** Planner, pairing two Builder findings
**Claim, offered as provisional and recorded as such:** two defects found on the
same day are invisible to opposite methods, and **neither review nor execution
alone would have caught both.**

| Defect | Invisible to | Caught by |
|---|---|---|
| **B1's tautology** - `filing_date <= D AND filing_date > D` | **Execution.** It ran clean and proved nothing; every run passed. | **Reasoning** about what the predicate could ever evaluate to. |
| **`CREATE TABLE fetch`** - reserved word | **Review.** Nine readings across a heading, a table, three FKs, a view, two indexes and a comment block. It is the obviously correct English word. | **Execution**, instantly, on the first run. |

**Why the pairing is a stronger claim than either finding alone.** Each on its
own reads as an argument for more care of one kind. Together they say something
else: **the two methods have disjoint blind spots**, and a process that leans on
either exclusively will keep one of these classes permanently. A review culture
never finds the reserved word; a run-it-and-see culture never finds the
tautology, because it passes.
**Status: provisional.** Recorded here rather than promoted to doctrine because
it rests on two instances one day apart, and a pattern with n=2 is a hypothesis
with a good story. It earns promotion if a third defect lands cleanly on either
side of the split.
**Sample:** 2 defects, 2 methods, 0 overlap.

### F-next/open-39-unknown-recorded-as-a-gap
**Date:** 2026-09-24 - **By:** Builder, reconciling D18
**Claim:** D18 §5 states *"OPEN-36 stands - the Financial Statement Data Sets,
conditioned on **OPEN-39** (`coreg` resolvable to a CIK), with §5's
establishments before the fact-slice handover: `prevrpt` recorded never filtered,
the `ddate`/`qtrs` period derivation established against documentation, and the
archive's earliest quarter."*
**That ruling is in D17, which never arrived.** OPEN-36 has therefore been
**ruled in the Builder's favour** - FSDS chosen - and the Builder **has not seen
the ruling**, only D18's citation of it.
**Recorded as a numbered gap rather than acted on.** OPEN-39's text is unknown;
so are the precise terms of §5's three establishments. **Working from the
citation is exactly `F-next/citations-are-lossy-recovery`** - D9 §3 held the
migration/`schema_admin` collision and nothing cited it.
**What the citation does give us**, and it is enough to know what is missing:
OPEN-36 resolved to FSDS; OPEN-39 concerns whether `coreg` resolves to a CIK; and
three establishments gate the fact-slice handover. **Everything else in D17 is
unknown.**
**RESOLVED 2026-09-24.** D17 re-sent in full in D19, both documents unchanged.
**The gap was held for one delivery and cost nothing**, because no work was
started on the citation - which is what the numbered gap was for.
**What the document contained that the citation did not:** OPEN-39's **three
possibilities** and the fact that **§2's ruling rests on two pillars, only one of
which is established** - so under possibility (3) co-registrant facts are
*refused* rather than ingested, a much narrower outcome than the citation implied.
**That is `citations-are-lossy-recovery` confirmed a second time**, and on the
same axis: the citation carried the decision and not the conditions attached to
it.
**Sample:** 1 delivery lost, 1 ruling known only by citation.

### F-next/same-file-opposite-verdict - `company_tickers.json` is wrong for one question and right for the other
**Date:** 2026-09-24 - **By:** owner ruling via D19 §2.2, recorded by Builder
**Claim:** the register rejected `company_tickers.json` as a universe source
because it holds **only currently listed companies** (P-10, measured: 8,049 CIKs,
Lehman/Sears/BB&B/Enron absent). **The delisting eligibility ruling adopts the
same file for the opposite reason.**
**The property did not change; the question did.** *Current-only* is a **defect**
when asked *which companies existed in 2014* and is **exactly the right
instrument** when asked *is this company listed today*.
**Why it is recorded rather than left to be noticed:** the register contains a
ruling that rejects this file, stated forcefully and with measurements. Someone
reading that entry alone will take it as a blanket judgement on the source -
and the correct reading is that a source is fit or unfit **relative to a
question**, never in itself. Two rulings now point in opposite directions on one
file and **both are right**.
**Related:** `F-next/an-instrument-can-be-promoted-without-being-changed` - there
the question changed under a fixed instrument and made it inadequate; here the
question changed and made a rejected instrument correct. **Same mechanism, both
directions.**
**Sample:** 1 file, 2 rulings, 0 changes to the file.

### F-next/bias-can-re-enter-at-the-last-gate - Survivorship removed from the universe can return through eligibility
**Date:** 2026-09-24 - **By:** Planner, D19 §3
**Claim:** ruling 5 keeps survivorship bias out of the **universe** at real cost -
the bulk archive, the CIK keying, the Lehman proof. **An eligibility rule of
*exclude companies not currently listed*, applied to a backtest, puts all of it
back.** A 2014 validation would exclude every company that died between 2014 and
now.
**The shape is what makes it worth a finding rather than a fix:** the universe
would be correct, the fact store would be correct, ruling 5 would have done its
job exactly as designed - **and the answer would still be wrong.** The bias
enters **at the last step, in the component built to enforce correctness**, and
every upstream guard would report success.
**It generalises past this instance:** a property enforced everywhere upstream
can be destroyed by one downstream filter, and **upstream correctness offers no
protection at all** - it is precisely what makes the result look trustworthy.
**The rule therefore has two forms that are not the same rule:** exclude
not-listed-today for **output**; exclude not-listed-**at-D** for **validation**.
**We can answer the first and not the second.**
**Consequence, recorded rather than deferred:** until as-of listing status
exists, **any backtest must state in its own output which eligibility rule
produced it.** *A validation result that does not state which eligibility rule
produced it is not interpretable* - and putting that in a document beside the
result is not the same as putting it in the result.
**Sample:** 1 ruling, 1 trap, 0 upstream guards that would have caught it.

### F-next/one-file-failed-twice-by-the-same-route - The loss is not well modelled as random
**Date:** 2026-09-24 - **By:** Planner (D19 §1), confirmed by Builder
**Claim:** `REPORT-Code-2026-09-24-...-0002-provenance.md` has failed to arrive
**twice**, and **documents issued alongside it arrived both times.**

| Delivery | Contents | Arrived |
|---|---|---|
| D12 | manifest + **this report** | manifest only |
| D14 | 2 new documents + **this report as R1** | both new documents only |

**Three of the four other documents in those two deliveries came through.** One
file has failed twice on a path that carried everything beside it.
**That is no longer well modelled as random loss**, and the register should not
record it as bad luck when the evidence points at something about the file or its
identity.
**The file is intact on the Builder's side** - 9,317 bytes, unchanged since
issue, sha256 `ea34493de76bc6de…`. **So the failure is in delivery, not in
authorship or storage.**

**Resolution taken: D19 §1 option 2, a marked identity exception.** Re-issued as
`...-0002-provenance-R2.md`, body byte-identical, carrying a header block that
states it supersedes nothing and explains why the name differs.
**Why breaking the rule is the right way to serve it.** The re-send rule holds
that an unchanged document **keeps** its identity, because *identity is what
makes a re-send recoverable* - the distinction drawn against
`same-name-revision`, where a **changed** document reused one. **Here the
identity is itself what appears to be failing.** Breaking it **visibly and once**,
with the reason attached, serves the rule's purpose better than a third attempt
down the same path would.
**Recorded as an exception with its reason, not as a new convention.** The next
re-send keeps its filename. If a fourth delivery attempt is needed, the fallback
is the content pasted directly rather than delivered as a file - a different
route, not a third identity.
**And if the R2 arrives where the original twice did not, that is itself the
finding**, because it discriminates between the two hypotheses: something about
the path, or something about the name.
**Sample:** 2 failures, 1 file, 3 of 4 companions delivered.

### F-next/archive-hash-is-a-build-id-not-a-change-detector - OPEN-44, and the mechanism is simpler than the hypothesis
**Date:** 2026-09-24 - **By:** Builder, answering OPEN-44
**Claim:** `fetch_log`'s response-level hash **cannot function as a change
detector for `submissions.zip`** - and not for the reason proposed.
**The hypothesis was rebuild nondeterminism** - zip member ordering, embedded
timestamps, compression differences making the bytes differ when the data does
not. **The actual mechanism is simpler and unavoidable:** the archive is a
**daily snapshot of a growing dataset**. New filings land every business day, so
**its contents genuinely change every night.**
**Measured, 24 hours apart:**

| | Content-Length | Last-Modified |
|---|---|---|
| 2026-09-23 | 1,565,081,455 | Wed, 23 Sep 2026 04:31:05 GMT |
| 2026-09-24 | **1,565,294,470** | Thu, 24 Sep 2026 04:31:44 GMT |

**+213,015 bytes overnight.**
**This reframes Q1 rather than answering it.** We cannot observe whether the
archive's hash changes when its contents are unchanged, **because its contents
are never unchanged.** The question has no accessible case.
**And that is the stronger result.** A response-level hash of a daily-rebuilt
archive is **structurally always-changing**, so it is **a build identifier, not a
change detector**. `fetch_content_change` would fire on the primary source every
single night, correctly, and *a finding that always fires is not a finding.*
**Q2 answers itself from that: the member is the right unit.** A per-filer JSON
inside the archive **does** stay byte-identical when that filer does not file, so
a member-level hash carries the signal the response-level one structurally
cannot. It is also the unit a `filing` row actually derives from.
**Not fixed by making the view quieter**, per the instruction - and that
instruction now has teeth, because the detector would be firing *correctly*.
Suppressing it would discard a true signal to silence a true-but-useless one.
**Two cheap facts for the design:** the response carries an **`ETag`**
(`"d203f56a…-187"`, multipart form) - a build identity obtainable **without
downloading** - and **`Accept-Ranges: bytes`**, so ranged requests are possible.
**Sample:** 2 HEAD requests, 24 hours apart, 1 growing archive.

### F-next/current-columns-that-never-update - OPEN-45, and the case does not arise for a worse reason
**Date:** 2026-09-24 - **By:** Builder, answering OPEN-45
**Claim:** slice 1's loader uses **`ON CONFLICT (cik) DO NOTHING`**, so it
**never updates** `filer.current_name`, `current_sic` or `metadata_as_of`.
**So OPEN-45's dilemma does not arise**, and `source_fetch_id` is internally
consistent: the provenance points at the fetch that produced the values beside
it, and neither ever changes. There is no misattribution.
**But the reason is the defect the Planner named in the same breath:** *a
`current_` column that never updates is its own problem.*
**`metadata_as_of` is the worst of the three, and it is worth separating from the
other two.** `current_name` and `current_sic` going stale is ordinary staleness.
**`metadata_as_of` exists specifically to bound the currency claim** - 0001's
comment says *"without this, current is an unbounded claim"* - and a frozen
`metadata_as_of` does not merely go stale, it **asserts a bound that is false**.
It would permanently claim the date of **first sight** while the values beside it
age indefinitely. **A column whose job is to say how old something is, lying
about how old it is**, is worse than no column.
**Not fixed here**, because the fix is a loader decision with a provenance
consequence and both belong to the same ruling: if `current_*` becomes an upsert,
**OPEN-45's dilemma arrives immediately** and `source_fetch_id` must be ruled to
either follow the update or stay at creation. Recorded as testplan OPEN-46 so the
two are decided together rather than the upsert being added and the provenance
question surfacing afterwards.
**Sample:** 1 loader, 3 `current_*` columns, 0 updates.

### F-next/i-confounded-my-own-experiment - The R2 trial moved two variables
**Date:** 2026-09-24 - **By:** Planner (D20 §1), accepted by Builder
**Claim:** I wrote that *"if R2 arrives where the original twice did not, that is
itself the finding, because it discriminates between the two hypotheses:
something about the path, or something about the name."* **It does not
discriminate.**
**R2 changed two things, not one.** The prepended header block makes it a
different file - different length, different hash - **as well as** a different
filename. So its arrival is equally consistent with *the name was the problem*
and with *something about that exact file was the problem*.
**The clean versions I did not run:** the **original filename with the header
block added**, or **R2's filename with the body untouched**. Either isolates one
variable. I ran neither, and the design error was in the same message that
claimed the discrimination.
**Why it is recorded when the conclusion is probably right.** That is precisely
why: **a correct conclusion from a confounded test is the one nobody
re-examines.** The result reads as settled, gets cited, and the confound is
invisible from everywhere downstream.
**This is the instrument pattern in a new place - the experiment rather than the
instrument.** Every previous instance was a measuring device that could not
report the condition it existed to detect. This is a **test design** that could
not distinguish the hypotheses it was built to distinguish, **while appearing
to**. n=1 against a prior of two failures.
**Recorded as suggestive with the confound named**, per the ruling. The exception
stays one-time and the next re-send keeps its filename - which is also the
cleaner trial if one is ever needed.
**Sample:** 1 experiment, 2 variables, 1 conclusion held loosely.

### F-next/coreg-is-a-marker-not-an-identifier - OPEN-39 is possibility (3), and OPEN-36 loses a pillar
**Date:** 2026-09-24 - **By:** Builder, establishing OPEN-39
**Claim:** FSDS `num.txt.coreg` is **a free-text label with no reliable path to a
CIK.** It is a per-fact entity **marker**, not a per-fact entity **identifier**.

**Documentation** (`readme.htm`, authoritative): *"coreg - coregistrant of the
parent company registrant (if applicable)"*. **No mention of CIK.**

**Measured on 2026q2, 61,122 coreg rows across 990 distinct labels:**

| Test | Result |
|---|---|
| Values that are numeric (could be a CIK) | **0 of 990** |
| Submissions with coreg facts that have **any `aciks`** to resolve against | **81 of 1,297 = 6.2%** |
| Submissions with coreg facts and **no `aciks` at all** | **1,216 = 93.8%** |
| Rows under **opaque sequence codes** (`EBP001`, `EBP002`…) | **21,064 = 34.5%** |

**Possibility (2) - resolution against `sub.txt.aciks` - fails on availability,
not on matching.** For **93.8%** of the submissions there is nothing to resolve
against: no additional CIKs are listed at all. The mapping does not have a
failure rate; **it has no domain.**

**And a third of the rows are beyond any resolution in principle.** `EBP001`
through `EBP0nn` are within-filing sequence labels - almost certainly employee
benefit plans numbered by the filer. They have **no external referent of any
kind**, so no lookup table anywhere could resolve them.

**CONSEQUENCE 1 - the scheme-refusal rule applies, and it is the rule working.**
`entity_cik` is `bigint NOT NULL REFERENCES filer`. Slice 1 established that an
identifier under another scheme **makes ingest fail rather than be coerced**. A
`coreg` label is exactly that. So **co-registrant facts are REFUSED** - roughly
**1.69% of facts** - rather than attributed to the parent's CIK, which is what
coercion would mean and what `F-next/entity-missing-from-fact-key` was written to
prevent.
**That is a narrower outcome than OPEN-36 assumed**, and it is a deliberate
refusal rather than an emergent rejection rate - which is why the ruling asked
for it to be reported rather than discovered.

**CONSEQUENCE 2 - OPEN-36 rests on ONE pillar, and the record must say so.**
The ruling was argued on dimensions **and** a per-fact entity. **The second does
not hold.** The first does, decisively - 60.7% - and FSDS remains correct
against companyfacts on that basis alone. But *"the decision record should say
which of the two pillars it rests on"* was the right instruction and the answer
is: **dimensions.**

**CONSEQUENCE 3, and it is uncomfortable:** `entity_cik` will be **trivially the
filer's CIK on every ingested row** - which is the exact condition that
disqualified companyfacts. **The difference is that here it is a refusal we chose
and can see**, not a silence we could not detect: the refused rows are countable,
and `fetch_log` plus the loader's rejection path make them visible. **A known
1.69% gap is a different object from an invisible misattribution.**
**Sample:** 1 quarterly set, 61,122 coreg rows, 990 labels, 0 CIKs.

### F-next/fsds-field-semantics-established - OPEN-40, 41 and 42, from the documentation
**Date:** 2026-09-24 - **By:** Builder, establishing D17 §5
**Source:** `readme.htm` inside `2026q2.zip` - **the archive's own
documentation**, per the instruction not to infer the encoding from samples.

**OPEN-40 - `prevrpt`, and the Planner's reading is confirmed verbatim.**
> *"Previous Report. TRUE indicates that the submission information was
> subsequently amended."* BOOLEAN (1 true, 0 false).

**So `prevrpt=1` marks the ORIGINAL that was later amended** - not the amendment,
and not a defective row. **It flags precisely the value that was knowable at the
time**, which is the thing a point-in-time store exists to hold.
**Filtering on it would delete the original and keep only the restatement**,
implementing the latest-value trap with the platform's assistance. **Store the
flag; never exclude on it.** Recorded as documented fact rather than inference.

**OPEN-41 - the period derivation, established not inferred.**
> *"ddate - period end date"*, *"qtrs - duration in number of quarters"*

Observed distribution over 3,608,711 rows confirms the encoding:

| `qtrs` | rows | meaning |
|---|---|---|
| **0** | **1,980,167 (54.9%)** | **instant** - balance-sheet points |
| 1 | 974,152 | one quarter |
| 4 | 515,012 | annual |
| 2, 3 | 139,017 | two and three quarters |
| 5 | 54 | five quarters |

**Derivation onto 0001's columns:**
- `period_end` = `ddate`
- `period_type` = `'instant'` if `qtrs = 0` else `'duration'`
- `period_start` = `ddate` when instant (0001's `period_start = period_end`
  convention); otherwise `ddate` minus `qtrs` quarters

**`qtrs = 0` being the largest bucket is the corroboration that matters** - it is
what a balance-sheet-heavy dataset should look like, and an encoding read the
wrong way round would have put the majority of rows in the wrong period type.

**OPEN-42 - the archive begins 2009q1, and that is not the usable bound.**

| Quarter | Size |
|---|---|
| 2008q4 and earlier | **404 - does not exist** |
| 2009q1 | 13,540 bytes - effectively empty |
| 2009q2 | 144,894 |
| 2009q4 | 4,050,938 |
| 2010q4 | 14,679,781 |
| **2011q4** | **64,306,658** |
| 2012q2 | 80,075,771 |
| 2013q2 | 96,917,655 |

**The nominal start is 2009q1 and the useful start is ~2011q4**, as XBRL
mandate phase-in completed. **Reporting the nominal date alone would overstate
the backtest's reach by nearly three years** - the TDD requires ≥3 years of
filing history for eligibility, so a validation dated 2010 would run on a
fraction of the market and **look like a validation**.
**Sample:** 1 readme, 3,608,711 rows, 11 quarters probed.

### F-next/open-44-answered-per-source - The hash works for the fact source and not for the universe source
**Date:** 2026-09-24 - **By:** Builder, OPEN-44's fetch-twice test
**Claim:** `fetch_log`'s response-level hash is **a valid change detector for the
Financial Statement Data Sets and not for `submissions.zip`.** The Planner's
per-source hypothesis is confirmed, and the split is clean.

| Source | Test | Result |
|---|---|---|
| **FSDS `2026q2.zip`** | fetched twice, 3s apart | **60,419,016 bytes and sha256 `d7c815395cd420cf…` both times - IDENTICAL** |
| **`submissions.zip`** | measured 24h apart | **1,565,081,455 -> 1,565,294,470 bytes - CHANGED** |

**So the rebuild-nondeterminism hypothesis is refuted for FSDS.** No per-request
recompression, no member reordering, no embedded timestamps moving. The response
is **byte-deterministic**, which is what the hypothesis actually doubted.

**And that makes `fetch_content_change` correct on the primary fact source.** A
changed hash on a quarterly archive is **not routine noise - it would mean the
SEC republished that quarter**, which is exactly the event D-023's
re-derivability claim is about. **The detector fires on the source that matters
and stays quiet as designed.**

**The precise claim, because two things are easy to conflate.** This proves the
**response is deterministic**, not that the archive **will never be republished**.
The first is what the nondeterminism hypothesis doubted and is now settled. The
second is the thing the detector exists to catch, and it remains possible - which
is the point of keeping the detector rather than a reason to doubt it.
**Three seconds is a weak interval for a durability claim and a sufficient one
for a determinism claim**, and only the second was being tested.

**Consequence for the design:** the member-level hashing question
(OPEN-44 Q2/Q3) applies **only to `submissions.zip`**, whose response hash is a
**build identifier**. FSDS needs nothing - the response *is* the unit, because
the unit does not move.
**Sample:** 1 archive fetched twice, 1 archive measured across a rebuild.

### F-next/d21-lost-fact-slice-handover-unknown
**Date:** 2026-09-24 - **By:** Builder, reconciling D22
**Claim:** **delivery D21 never arrived** - both documents. D22's check expected
**48 distinct**; **46** are on disk, and the shortfall is exactly D21's two.
**What it carried, inferred from D22's citations and not assumed:**
`HANDOVER-Planner-2026-09-24-...-fact-slice.md` - the fact-slice handover itself -
plus **OPEN-47 through OPEN-50**. D22 answers *"§5 of"* that handover and cites
**§4.3** (*store, don't filter*) and **§5**'s order of preference.
**What the citations give us:** OPEN-48 concerns `version` and filer extension
tags, OPEN-49 `segments` truncation, OPEN-50 `adsh` formatting; §5's preference
order is concept-narrowing, then disk, **not** dimension-narrowing.
**What they do not give us:** the precise questions, their falsification
conditions, §4's rules, and whatever else the handover contains that nothing
cited - **which is the exact shape of `citations-are-lossy-recovery`.** D9 §3
held the most consequential item in that document and nothing cited it; D17 held
OPEN-39's three possibilities and the two-pillar condition, and the citation
carried neither.
**Third whole-delivery loss today** (D4, D9, D17, D21 - fourth overall), and the
count caught it against a stated expectation as every previous one was.
**[PLANNER] Re-send D21 in full.**
**What proceeds meanwhile, and why only this:** **OPEN-44's fetch-twice test was
fully specified in D20** - a delivery held in hand - so it does not rest on any
citation. It is done. **OPEN-48, 49 and 50 are not started**, because their terms
exist only as three-word summaries in another document.
**Sample:** 1 delivery lost, 2 documents, 1 handover unknown.

### F-next/coverage-measurement-45-does-not-fit - OPEN-51's measurement, and it says stop
**Date:** 2026-09-24 - **By:** Builder, OPEN-51 §1
**Claim:** **45 quarters does not fit.** One quarter loaded into a local cluster
with 0001 and 0002 applied:

| | |
|---|---|
| 2026q2 facts loaded | **3,369,002** |
| `fact` table | 697.8 MB |
| `fact` indexes | **1,113.6 MB** |
| All tables + indexes | **1,814.1 MB** |
| Bytes per fact row, incl. indexes | **565** |

**The scaled estimate is 124.4 GB against a 15 GB cluster — short by roughly
8x.** Per D22 §4 this is **report and stop**.

**AND THE NAIVE MULTIPLICATION UNDERSTATES IT BY 56%, which is the finding
inside the finding.** `1,814 MB x 45 = 79.7 GB` is wrong. Summing the actual
archive bytes for the 45 quarters in the window (2015q2-2026q2) gives
**4,242,443,105 bytes against 2026q2's 60,419,016 - a ratio of 70.22, not 45.**
**2026q2 is one of the smallest quarters in the window**, so measuring it and
multiplying by the quarter *count* silently assumes quarters are interchangeable.
They are not.
**This is OPEN-51's own argument one level in.** The ruling said *loading 45
quarters to find out where we sit is measuring by doing the expensive thing.*
Correct - and **measuring one unrepresentative quarter and multiplying by a count
is measuring the wrong thing cheaply**, which produces a number that looks like
the answer and is 56% low. The fix cost 45 HEAD requests.

**WHERE THE BYTES GO, and it changes the options:**

| Index | Size | % of fact indexes |
|---|---|---|
| **`fact_one_per_filing`** | **765 MB** | **68.7%** |
| `fact_entity_concept_idx` | 181 MB | 16.2% |
| `fact_pkey` | 72 MB | 6.5% |
| `fact_concept_period_idx` | 46 MB | 4.2% |
| `fact_consolidated_idx` | 25 MB | 2.2% |
| `fact_accession_idx` | 25 MB | 2.2% |

**Indexes are 61% of total storage, and one constraint is 42% of everything.**
`fact_one_per_filing` is a nine-column unique index, and **it is the single
largest object in the database by a wide margin.**
**It is also the least negotiable thing in the schema.** It is what makes
overwrite-on-amendment unavailable rather than discouraged - A4 exists to stop a
future migration removing it. **So the largest storage cost and the central
correctness guarantee are the same object**, and the §4 preference order does not
currently mention indexes at all.
**Not proposing a change** - but the order of preference was written before
anyone knew that 42% of the bill is one constraint, and **the cheaper levers may
be the four indexes below it (277 MB, 15%), which are performance choices rather
than correctness ones.**
**Sample:** 1 quarter, 3.37M facts, 45 archive sizes.

### F-next/0002-omits-the-fact-table - The provenance migration does not cover the table it was ordered for
**Date:** 2026-09-24 - **By:** Builder, during OPEN-51's measurement
**Claim:** **0002 adds `source_fetch_id` to `filer`, `filer_ticker` and `filing`.
It does not add it to `fact`.** Discovered because the measurement's `COPY` into
`fact` failed: *column "source_fetch_id" of relation "fact" does not exist*.
**And verification A5 does not catch it**, because A5 iterates
`ARRAY['filer','filer_ticker','filing']` - **the same three tables**. So the
check written to assert *an unprovenanced row is not representable* **passes
while every `fact` row is unprovenanced**.
**The irony is exact and worth stating plainly.** D16 §2.1 ordered 0002 **before**
the fact slice on the reasoning that *the fact slice is where the volume arrives;
in the other order the largest body of data this project holds becomes the part
that can never be traced.* **0002 as written leaves precisely that gap.** The
migration built to stop the fact table being untraceable does not reach the fact
table.
**Why it survived review:** 0002 was written against slice 1's three tables,
which were the tables that existed *in the loader*. `fact` existed in the schema
and had no loader, so it was invisible to the question *which tables does the
loader write?* - which is the question I was actually answering. **The right
question was *which tables hold data?***
**This is the instrument pattern in the guard's scope rather than its logic** -
tenth instance. A5 is correctly written and correctly passing; it simply does not
look where the problem is. **A guard's blind spot is not usually in what it
checks but in what it enumerates.**
**Requires 0003**, not an amendment to 0002: 0002 has been applied to local
clusters and, more importantly, the habit argument from D16 §2.4 applies with
more force each time. **No fact data exists anywhere**, so the refusal-to-backfill
block will pass trivially - which is the same cheap-now-impossible-later window
0002 itself was ordered inside.
**Sample:** 1 migration, 4 data tables, 3 covered.

### F-next/fsds-violates-its-own-documented-key - And DO NOTHING would have been silent data loss
**Date:** 2026-09-24 - **By:** Builder, during OPEN-51's measurement
**Claim:** FSDS `num.txt` documents its unique key as *(adsh, tag, version,
ddate, qtrs, uom, segments, coreg)*. **Real data violates it.** 2026q2 holds
**3,608,711 rows across 3,608,679 distinct key tuples - 32 collisions.**
**31 of the 32 carry DIFFERENT VALUES.**

```
0001628280-26-034133  DerivativeAssetFairValueGrossLiability  20260331
    -> values -3,123,000 and 706,000
    -> values  1,591,000 and 645,000
```

**So `ON CONFLICT DO NOTHING` on 0001's key would be silent data loss** - keeping
one value and discarding a genuinely different one, with no record, in the schema
built to make exactly that impossible.
**I nearly recommended it on n=1.** The first collision I hit was the one exact
duplicate - identical on every field including value - and it reads as harmless
deduplication. **The population says the opposite: 31 of 32 disagree.** Same
error as the confounded R2 experiment: generalising a mechanism from the first
instance that presented.
**The distinguishing axis appears to be lost in FSDS's own extraction, not in
our mapping.** The 64 rows sharing that adsh/tag/ddate carry distinct `segments`
of 42-134 characters, so truncation is not the cause here - **OPEN-49's terms
(in the lost D21) may bear on it and I have not assumed they do.**
**What the loader must do, and it is not DO NOTHING:** detect the collision,
**assert the colliding rows agree on value**, and **fail loudly when they do
not** - 31 rows per quarter is small enough to report individually and far too
important to drop. For this measurement the 32 were **skipped and counted**,
which is acceptable for a sizing probe and would not be acceptable for a load.
**Sample:** 3,608,711 rows, 32 collisions, 31 disagreeing.

### F-next/open-48-49-50-answered - The three establishments, both quarters
**Date:** 2026-09-24 - **By:** Builder, D21 §4.2 and D24 §4
**Measured on 2015q2 and 2026q2**, per the instruction that one quarter is not a
sample.

**OPEN-48 - extensions are distinguishable, and the rule is documented.**
`readme.htm`: *"version - if a standard tag, the taxonomy of origin, otherwise
**equal to adsh**."* So `version = adsh` **is** the extension marker - no
heuristic needed.

| | 2015q2 | 2026q2 |
|---|---|---|
| num.txt rows | 2,588,598 | 3,608,711 |
| **standard** | 2,399,976 (**92.7%**) | 3,300,989 (**91.5%**) |
| **extension** | 188,622 (**7.3%**) | 307,722 (**8.5%**) |
| distinct standard tags | 4,490 | 5,044 |

**The split is stable across eleven years - and it moves the OPPOSITE way to the
hypothesis.** D24 §4.1 expected *"the early quarters plausibly carry a higher
extension share than the recent ones"* as taxonomies mature. **Measured: 7.3%
then, 8.5% now.** Filers extend slightly **more**, not less. The prediction was
reasonable and wrong, which is why it was measured on two quarters rather than
assumed from one.

**OPEN-49 - `segments` is NOT truncated.** A hard cap would show a **large spike
at one exact length**. There is none: max 440 in 2026q2 with **1 row at it**, and
383/384/395/402/403 carrying 1-4 rows each, against a mean of **6,100 rows per
distinct length**. The tail decays smoothly to a single row. 2015q2's max is
**448** - a *different* value, which a fixed limit could not produce.
**So the jsonb parse cannot silently produce a well-formed-but-wrong dimension
from a truncated string.** The refuse-rather-than-default-to-`'{}'` rule still
stands for malformed input; it simply has no truncation population to catch.

**OPEN-50 - `adsh` matches slice 1's accession format exactly.** **0 failures**
against `^\d{10}-\d{2}-\d{6}$` across **8,212** submissions in 2015q2 and
**7,714** in 2026q2. The FK will not see a formatting disagreement.
**Sample:** 2 quarters, 6.2M fact rows, 15,926 submissions.

### F-next/tier-1-does-not-fit-and-neither-does-any-concept-cut
**Date:** 2026-09-24 - **By:** Builder, D24 §4 measurement
**Claim:** **tier 1 does not fit, and the concept lever cannot close the gap
either.** Report and stop per D24 §3.

**Tier 1 retains 91.5% of rows**, so it removes **8.5%**:
**124.4 GB x 0.915 = ~114 GB against a 15 GB cluster.** Still **7.6x over**.

**And the concept curve says no allowlist reaches 15 GB.** To fit, the store must
retain **<= 12.1%** of all rows:

| Concept allowlist | Share of all rows | Estimated size |
|---|---|---|
| top **1** tag | 4.5% | ~5.7 GB |
| top **5** tags | **16.7%** | **~20.7 GB** - already over |
| top 10 | 26.3% | ~32.8 GB |
| top 30 | 38.8% | ~48.2 GB |
| top 50 | 46.9% | ~58.3 GB |

**Fitting 15 GB means roughly three or four concepts in total.** GQS needs
**dozens**. So the lever D24 §4.1 identified as *"the only one with the range"*
**does not have the range** - not because the reasoning was wrong, but because
the distribution is flatter than a concept cut needs.

**Every lever, now priced:**
- **Window** - five quarters fits; useless for validation (D23 §4)
- **Dimensions** - refused on principle, and would leave ~49 GB anyway
- **Indexes** - 15% at best; `fact_one_per_filing` is 42% and non-negotiable
- **Concepts** - needs ~3 tags to fit; **measured here**
- **Disk** - the only lever with 8x in it

**So the honest conclusion is that 15 GB cannot hold a usable fact store under
any narrowing**, and the four analysis rounds did not waste effort - **each one
removed a lever that looked plausible until it was priced.**

**AND THE COST COMPARISON MAKES IT SMALLER THAN IT SOUNDS.** Going to 150 GB
Basic is **$80/month against today's $42 - about $38 more.**
`F-next/cluster-plan-fee-is-per-cluster` establishes roughly **$120/month of idle
spend** across the retained `stockgrader-db` and the two PharmFoldMDK orphans.
**Destroying the three idle clusters pays for the disk three times over.** The
storage decision is not the expensive item on this bill and has not been for some
time.
**Sample:** 2 quarters, 5,044 distinct standard tags, 5 levers priced.

### F-next/cluster-plan-fee-is-per-cluster - Ruling 6's "costs little" is wrong, and by more than the decision it was beside
**Date:** 2026-09-24 - **By:** Planner (D24 §2), from Fly's published pricing
**Claim:** **each MPG cluster carries its own plan fee.** The plan sets CPU and
memory **for a cluster**, so four clusters means four plan fees. `fly mpg list`
shows **four ready clusters**: `stockgrader-db-r1` (live), `stockgrader-db`
(retained, holding nothing), and the two PharmFoldMDK restore orphans.
**Approximately $41/month for the retained old cluster** at Basic with 10 GB.

**CORRECTED 2026-09-25 (P-11): the "~$120/month of idle spend" figure is struck.**
It totalled three clusters as idle when **only one is established as such.**
`stockgrader-db` is ours and deliberately empty. The other two are attached to
live projects and **their status is unknown** - see
`F-next/orphaned-restore-clusters-already-exist`, corrected.

**The mechanism is untouched and it is the part that mattered:** a cluster costs
**~$38/month before storage**, so an empty cluster is not cheap.
**And the conclusion survives on the one cluster we can vouch for.**
`stockgrader-db` at roughly **$41/month alone more than covers the ~$38/month the
disk increase needs.** The inversion holds **without touching anyone else's
infrastructure**, which is a better version of the argument than the one that
needed three clusters.
**Ruling 6 says the old cluster *"holds nothing and costs little."* The second
half is wrong.** The ordering of its destroy does not change - it still waits on
the ticker load and a DB-backed endpoint, and that ordering was right for
credential reasons - **but it should stop being described as cheap.**
**The comparison that makes it sting:** $120/month of idle clusters **exceeds the
entire storage decision** two deliveries were spent analysing, where going from
15 GB to 150 GB costs **$38/month more**.
**And it explains the orphans' survival.** `F-next/orphaned-restore-clusters-
already-exist` recorded two PharmFoldMDK clusters nobody destroyed. At a
rounding-error storage cost they were invisible; **the plan fee is what makes
them expensive, and the plan fee is the part that does not scale down with an
empty disk.**
**B-9's destroy condition is now financial as well as procedural.** An orphaned
probe cluster is **$38/month indefinitely at any size** - which is precisely why
the two next door survived unnoticed.
**Sample:** 4 clusters, 1 published price list.

### F-next/the-first-case-to-present-is-not-a-sample
**Date:** 2026-09-24 - **By:** Planner (D23 §3.5), generalising two Builder errors
**Claim:** twice in one day the Builder drew a mechanism from **the first
instance that happened to present**, and twice the population said otherwise.

| Instance | First case suggested | Population said |
|---|---|---|
| FSDS key collisions | an exact duplicate - harmless deduplication | **31 of 32 disagree on value** - `DO NOTHING` is silent data loss |
| The R2 re-send | the filename was the problem | **confounded** - name and bytes both changed |

**A third, from the Planner's side, points the same way:** D24 §4.1 predicted
early quarters would carry a **higher** extension share as taxonomies mature.
**Measured: 7.3% in 2015q2 against 8.5% in 2026q2 - the opposite direction.**
**The general form:** the first case to present is selected by **encounter
order**, not by representativeness, and encounter order correlates with nothing.
It is the sampling version of the instrument pattern - **the observation is
accurate and the inference from it is not**, and nothing about the observation
signals which.
**Rule:** a mechanism inferred from one instance is a hypothesis with a good
story. **Count the population before recommending the handling** - it cost one
query each time, and each time it reversed the recommendation.
**Sample:** 3 predictions from first instances, 3 reversed by counting.

### F-next/0003-inverts-the-enumeration - The guard now fails closed, proven side by side
**Date:** 2026-09-25 - **By:** Builder, D23 §2 (OPEN-54)
**Claim:** 0003 adds `source_fetch_id NOT NULL` to `fact`, and **replaces 0002's
enumerated provenance check with a derived one.** A2 now reads the catalogue and
asserts **every ordinary table** carries provenance, **minus** rows in a declared
`provenance_exempt` table.

**The demonstration, run side by side on the same database.** A new table
`price_daily` was created — the same shape of omission by which 0002 missed
`fact`:

| Check | Result |
|---|---|
| **0003's derived A2** | **RED** — *"table(s) carry no source_fetch_id NOT NULL and are not declared in provenance_exempt: price_daily"* |
| **0002's enumerated A5** | **PASSES** — blind to `price_daily` **and** to `fact` |

**That is the fails-open / fails-closed argument as a measurement rather than an
assertion.** Both are enumerations; only one is wrong by default.

**Every guard seen red:**

| Defect injected | Caught by |
|---|---|
| New unprovenanced table added later | **A2** |
| `fact.source_fetch_id` made nullable | **A2** (and A4 names it explicitly) |
| Exemption naming a non-existent table | **A3** |
| Unprovenanced `fact` row | C1 |
| Exemption with a trivial reason | C2 |
| Unprovenanced quarantine row | C3 |

**A3 exists for a failure I had not thought of until writing the list.** A stale
exemption — a name in `provenance_exempt` for a table that does not exist —
**pre-authorises a future table that happens to reuse the name.** The hole opens
years later, silently, and the exemption looks deliberate because it was.

**Reasons are mandatory and length-checked** (`>= 20` characters). The ruling's
line is the reason: *a list of names with no reasons becomes a place to hide a
table.* A CHECK constraint is the only place that rule cannot be forgotten.

**A4 is redundant with A2 and kept anyway.** A2 would catch `fact` on its own.
A4 names it explicitly because **it is the table 0002 missed**, and a regression
worth naming out loud is worth a redundant check.
**Sample:** 1 new table, 2 checks compared, 6 guards tripped.

### F-next/0003-quarantine-keeps-both-assertions - OPEN-55, and the key is not weakened
**Date:** 2026-09-25 - **By:** Builder, D23 §3 (OPEN-55)
**Claim:** `fact_collision` holds **both** competing assertions when FSDS rows
collide on `fact_one_per_filing` with **different values**. Neither is loaded.
Proven: two rows for one fact, values `-3,123,000` and `706,000`, **both
retrievable, both traced to their fetch.**

**`fact_one_per_filing` is untouched**, per §3.3, and A6 asserts that. Adding a
source ordinal to the key would let two rows exist for one fact — **exactly what
the key forbids by design and what A4 protects.** The guarantee is worth more
than 31 facts per quarter out of 3.4 million, and **the alternative was never
"keep them" — it was "keep one of them, chosen arbitrarily, with no record."**

**No uniqueness constraint on the quarantine's colliding key, deliberately**, and
A5 asserts its absence. **The rows collide by definition**; a unique constraint
here would refuse the second one and **reproduce the loss inside the table built
to prevent it.** That is the kind of guard that would have looked correct.

**The quarantine is not where the rules relax.** Quarantined rows carry
`source_fetch_id NOT NULL` like everything else, and C3 proves an unprovenanced
one is refused. **A refusal we can count is only a different object from a
silence if the refusal is itself inspectable.**

**`fact_collision_rate` reports per fetch**, per §3.5 — *the number is the
signal; a jump means something changed at the source, which a constant trickle
would hide.* A view rather than a stored counter, for 0002's reason: the number
is derived, and a stored copy can diverge from what it counts.

**Second instance of the standard set with `coreg`:** a **chosen refusal we can
count and inspect** is a different object from a silence. Recorded as **the
general response to source data that violates its own contract**, which is what
the ruling asked.
**Sample:** 1 collision pair, 4 behavioural checks, 3 refusals.

### F-next/i-used-a-source-i-had-proven-unreliable
**Date:** 2026-09-25 - **By:** Builder, on P-11
**Claim:** I recorded that `fly mpg list`'s ATTACHED APPS column **records history,
not state** - that it *"does not answer which cluster is this app using"* - and
then, from the same listing, **concluded that two clusters were unused.**
**The two uses are not symmetric in evidence but they are symmetric in
unreliability.** *Attached* does not prove in-use; *attached to a project I am not
thinking about* does not prove abandoned. I treated the first as a caution and
the second as a fact.
**What made it feel safe:** the *names*. `sentinel-holy-rain-4562 restored
2026-08-17... restored 2026-09-13...` reads like debris, and a generated name
carrying two timestamps invites the reading. **A name is not a status field**, and
the same string is equally consistent with a project that recovered twice and kept
what it got.
**The general form, which is why it is a finding and not an apology:** **a source
established as unreliable for one question is not thereby reliable for its
converse.** Recording the limitation protects the question you were asking when
you found it, and **offers no protection at all to the next question**, because the
limitation lives in a finding and the next question arrives without reading it.
**The cost of the specific error was bounded and the shape was not.** The cost
argument was one step from *destroy the three idle clusters* - **and destroying a
cluster on the strength of a name in a listing is how a live production database
disappears.**
**Related:** `F-next/an-instrument-can-be-promoted-without-being-changed` - there
an instrument acquired a new question it could not answer. **Here I brought the
new question to an instrument I had personally documented as unable to answer
it.**
**Sample:** 1 listing, 2 questions, 1 recorded limitation not applied.

### F-next/open-56-storage-cannot-be-resized-from-the-cli - and the docs and the CLI do not agree
**Date:** 2026-09-25 - **By:** Builder, establishing OPEN-56
**Claim:** the answer splits, and **the two halves do not compose into a
confident one.**

**What the CLI says.** `fly mpg create` takes **`--volume-size int` (default 10)**,
so size is chosen **at creation**. And the full subcommand list is
`attach, backup, connect, create, databases, destroy, detach, list, proxy,
restore, status, users` - **there is no resize, scale or update command.** From
the CLI, **provisioned storage cannot be changed after creation.**

**What the documentation says.** *"Storage growth is monitored and managed
automatically."* And billing is **`$0.28 per provisioned GB` for a 30-day month** -
provisioned, not used.

**What the documentation does NOT say:** whether provisioned storage can be
**raised** post-creation. That sentence is absent.

**So "managed automatically" is doing a great deal of work in five words**, and it
is the load-bearing claim. If it means Fly raises the provisioned figure as the
data grows, then **under-provisioning is recoverable and over-provisioning is
money spent on empty space** - provision low. If it means monitoring and alerting,
then **under-provisioning is not cheaply recoverable at all**, because the CLI
offers no way out and `fly mpg restore` picks its own size (it gave 15 GB for a
10 GB source, OPEN-22).

**This is the same shape as "no cases found is not the rule is unnecessary."** I
cannot verify auto-growth without filling a disk, and **a claim I cannot test is
not evidence I can spend money against.**

**Consequence for OPEN-53, and it inverts D25 §5.1's framing.** The ruling asked
which mistake is cheap *because* the answer decides the figure. **On the CLI
evidence, under-provisioning is the expensive mistake** - recovery means creating
a new cluster at the right size and migrating into it, since restore will not size
to order. **Over-provisioning is merely money**, at $0.28/GB/month.
**So the safe direction is to provision for the measured need plus headroom, and
to treat "it grows automatically" as unverified rather than as a safety net.**
**Also established, for OPEN-57:** plan RAM is **Basic 1 GB, Starter 2 GB,
Launch 8 GB, Scale 32 GB, Performance 64 GB.**
**Sample:** 1 CLI surface, 1 docs page, 1 unanswered question.

### F-next/open-57-the-measurement-cannot-answer-its-own-question
**Date:** 2026-09-25 - **By:** Builder, running OPEN-57
**Claim:** **index construction is not the constraint, and the measurement cannot
establish that Basic is sufficient.** Both halves matter and the second is the
important one.

**Measured** - two widely separated quarters, Postgres constrained to
Basic-shaped memory (`shared_buffers=128MB`, `maintenance_work_mem=64MB`,
`work_mem=4MB`):

| | |
|---|---|
| Facts loaded | 5,636,958 |
| Table size | 1,089 MB |
| **`fact_one_per_filing` built in** | **21.3 s** |
| Index size | 1,075 MB |
| Rate | 264,038 rows/s, 50.4 MB/s |
| Extrapolated to 42 GB | **~0.2 h linear, ~0.3 h `n log n`-adjusted** |

**So Postgres's own memory settings are not the binding constraint on the index
build.** 64 MB of `maintenance_work_mem` built a 1 GB index in 21 seconds; the
external merge sort is not the problem the question feared.

**AND THE RESULT DOES NOT ANSWER THE QUESTION, exactly as the ruling predicted.**
The host has **31.5 GB of physical RAM**. The 1,089 MB table **fit entirely in the
operating system's page cache**, which was never constrained - only Postgres's
own buffers were. On Fly Basic, **1 GB is the whole machine**: shared_buffers,
page cache, connections and everything else come out of it, and a 114 GB store
cannot be cached in any meaningful proportion.

**So the simulation was optimistic by roughly 31x on the one resource that
matters**, and the number it produced is about a machine that does not exist.
**It could have proved Basic inadequate. It did not, so it proves nothing** -
which is a different and weaker outcome than "Basic looks fine".

**The asymmetry is the finding, and it was stated before the measurement rather
than after.** D25 §5.2 said *"it can prove Basic is inadequate; it cannot prove
Basic is sufficient"* - and **writing that caveat in advance is what stops a green
result being read as a pass.** Had it been written afterwards it would have looked
like an excuse for an inconvenient number.
**What would actually answer it:** a cgroup- or VM-constrained host with **1 GB
total**, so the page cache is bounded too - or provisioning a Basic cluster and
loading into it, which costs money and is the thing the measurement was meant to
avoid.
**Recorded as: the constraint is unmeasured, and the plan tier is still an open
decision.** The only thing removed from the risk list is the external sort.
**Sample:** 1 constrained cluster, 5.6M facts, 31x unconstrained page cache.

### F-next/open-57-measured-under-a-real-cgroup - Basic survives the build; the steady state is still unestablished
**Date:** 2026-09-25 - **By:** Builder, re-running OPEN-57 against a bounded page cache
**Supersedes the previous OPEN-57 measurement**, which was optimistic by ~31x
because only Postgres's buffers were constrained and the host's page cache was
not. **This one bounds the page cache**, which is what the question was about.

**The instrument, and why it is a valid test this time.** A Docker container with
`--memory=1g --memory-swap=1g`. Cgroup v2 **charges page cache to the limit**, so
the cache is bounded rather than merely the database's buffers. Evidence the
limit bound, taken from the cgroup itself:

| | |
|---|---|
| `memory.max` | 1,024 MB |
| `memory.current` at rest | **990-1,022 MB - pinned at the cap** |
| of which **file cache** | **969 MB** |
| `memory.events` max-breaches | **95,784** |
| `oom_kill` | **0** |

**95,784 reclaim events and zero OOM kills.** The kernel was evicting cache
continuously and Postgres never died.

**Result 1 - the index build is not a problem, and this is now demonstrated
rather than simulated.** 5,636,958 facts, `fact_one_per_filing` built in
**15.4 s** producing a 1,075 MB index - **faster than the unconstrained host run
(21.3 s)**, which is Linux/container I/O rather than anything about memory.
Extrapolated to 42 GB: **~0.2 h.** **The external merge sort comes off the risk
list properly.**

**Result 2 - steady state runs, and the cache is already thrashing.** A
point-in-time query over 5.6M facts: **627 / 659 / 882 ms** across three runs,
with buffer counts **hit=16,113 read=123,325** - **88% of blocks came from disk
rather than cache**, at a data-to-cache ratio of only about **2:1**.

**At 114 GB the ratio is ~114:1**, so the read fraction approaches 100% and query
time becomes governed by I/O throughput rather than by caching. **Sub-second at
2:1 says very little about 114:1**, and extrapolating it would be
`the-first-case-to-present-is-not-a-sample` in a new variable.

**THE REMAINING CONFOUND, and it sits exactly in the path that matters.** The
container's cgroup bounds what the **container** caches. Underneath it, **Docker's
VM has 15.4 GB and its own unbounded page cache holding the same files.** So a
block the container counts as `read` may still have been served from VM RAM
rather than from a disk. **The confound is in the I/O path, which is precisely
the thing the 114:1 case would be dominated by.**

**So the honest position has moved but not arrived:**
- previously: **optimistic by ~31x, proved nothing**
- now: **page cache genuinely bounded; the build is settled; the steady state is
  better evidenced and still not conclusive**, because one unbounded cache layer
  remains beneath.

**What would close it:** a bare-metal or VM host with 1 GB total, or a real Basic
cluster loaded to size. **Both cost something the previous options did not** -
which is a reason to decide whether the remaining uncertainty is worth buying
out, not a reason to treat 882 ms as an answer.
**The asymmetry still holds and still points the same way:** this could have
proved Basic inadequate. It did not. **It is now meaningful evidence that the
build is safe and weak evidence about anything else.**
**Sample:** 1 cgroup-bounded container, 5.6M facts, 95,784 reclaim events.

---

### F-021 — a live credential reached the transcript, and the instruction that set it up was mine

**Established 2026-09-25, during the first attempt to run the migrations against
a real Fly cluster.**

**What happened.** `stockgrader_app`'s password appeared in full in the session
transcript. It was pasted as part of a `$env:DATABASE_URL=` assignment, echoed
back along with the command that followed it.

**Which command did it — and it was not a command.** Every prior control in this
project guarded against a credential appearing in *command output*: F-014 records
that `fly mpg create` and `fly mpg attach` print live credentials on success, and
the standing rule is to redact before relaying. **This exposure came from an
assignment the owner typed, not from any tool's output.**

**The instruction that set it up was the Builder's.** The handoff said to
substitute the real password into a `DATABASE_URL` line and then paste the
results back. That is a structure in which the value and the pasted region
overlap, and it depends on the person noticing the difference between the line
they type and the lines they return. **A rule that requires the human to
partition their own paste is not a control.**

**The correct shape:** have the variable set without the value ever entering the
conversation — read from a password manager, prompted by `Read-Host -AsSecureString`,
or sourced from a file outside the repository — so that no correct action puts
the secret on screen. **The transcript should never be the place where redaction
happens, because by then it has already happened.**

**Why this is the same shape as the project's other findings.** D-030 says
credentials never appear in transcripts, repo files, or env files in the tree.
It was stated as a property of the system and enforced only against the paths
anyone had thought of. **The guard covered tool output and the exposure came
through the one channel it did not cover** — the same structure as 0002's
enumerated A5 passing while blind to `fact`, and as an include-pattern that
silently omits a prefix nobody had invented yet.

**Blast radius.** The value is in the session transcript, the owner's shell
environment, and PowerShell history on disk. It is the credential the deployed
application uses, so rotation is two actions: a dashboard password change and a
`fly secrets set` for the app, both the owner's to run.

**Status: rotation DEFERRED by the owner, 2026-09-25.** Recorded as **OPEN-63**
rather than left in prose, because a deferral without an end is P-13's shape and
this project has one of those already.

**Three further defects in the same attempt**, each of which would independently
have failed the run, recorded because the credential exposure is the loudest of
the four and not the only one:

- **`stockgrader_app` is a `writer`.** A-017 established a writer is refused
  `CREATE TABLE` **by design**, so 0001 could never have run as it. The block
  needs a `schema_admin`; that is its entire purpose.
- **The host was `pgbouncer.<id>.flympg.net`.** The runner takes
  `pg_advisory_xact_lock` and runs each migration as one transaction it owns
  (D-021). Those semantics are not reliable through a transaction-mode pooler.
  A direct connection via `fly mpg proxy` is required.
- **The working directory was `C:\Windows\system32`**, so `.venv` did not
  resolve. This is the error the owner actually saw, and it masked the other
  two — **the shallowest fault reported first, with three real ones behind it.**

---

### F-022 — a guard written as a proxy for its property blocked the correct fix

**Established 2026-09-25, closing OPEN-59.**

0003's **A5** forbade any unique constraint on `fact_collision` covering
`concept`. Its stated purpose was to prevent a constraint that would **refuse a
second, disagreeing assertion** — reproducing, inside the quarantine, the loss
the quarantine exists to prevent.

**Those are not the same test.** "Covers `concept`" was a *proxy* for "would
refuse a competing value", and the two diverge at exactly one point: **a
constraint that also includes `value` cannot refuse a differing value, because
differing values differ in the key.**

**The divergence was not hypothetical — it was the fix to OPEN-59.** Making the
quarantine idempotent requires a constraint over the colliding key plus `value`
plus `source_ordinal`. A5 would have rejected it, while permitting nothing
safer. **The guard would have blocked the repair of a different defect and looked
correct doing it.**

**A5 now tests the property directly:** uniqueness covering the colliding key is
forbidden **unless `value` is part of it**. Proven both ways — the harness
confirms A5 still fires on uniqueness over the colliding key alone, and no longer
fires on the correct constraint.

**The general form, which is the part worth keeping:**

> A guard that tests a proxy passes and fails for the right reasons only while
> the proxy and the property agree. Nothing announces the point where they stop
> agreeing, and the first case to reach it is likely to be a correct change being
> refused rather than a defect being admitted — **which reads as the guard
> working.**

Related in shape to `a-guard-never-seen-red-is-not-a-guard`, and its inverse:
this one had been seen red, in the case it was written for. **Being seen red does
not establish that it goes red for the right reason.**

---

### F-023 — the quarantine's identity is a property of the archive, not of the fetch

**Established 2026-09-25, closing OPEN-59.**

Every other table's double-ingest idempotency is **the schema's property**: each
insert lands on `ON CONFLICT DO NOTHING` against a real constraint.
`fact_collision` deliberately had no constraint at all, so a second ingest of the
same quarter re-inserted every quarantined row. **A load that is idempotent
everywhere except in the table recording its refusals is not idempotent.**

**The identity that works is the colliding key + `value` + `source_ordinal`, and
each term is load-bearing:**

- **`value`** — two rows that disagree must both insert. That is A5's property,
  preserved by construction rather than by care.
- **`source_ordinal`** — three rows that collide where **two agree on value**
  must still yield three. Keyed on value alone they collapse to two, discarding
  the evidence that the archive asserted that value twice. **This is the case
  the Planner named in advance, and the harness confirms the wrong fix produces
  exactly 2.**
- **`source_fetch_id` is deliberately EXCLUDED.** `fetch_log` is keyed on
  `(url, retrieved_at)`, so a re-ingest is a **new fetch with a new id**.
  Including it would make every re-ingested row unique again and **pass a naive
  idempotency test while fixing nothing.**

**The cost, stated because it is real:** the retained row keeps the **first**
fetch that produced it. That is honest here — the row's content is immutable, so
first sighting is complete provenance, not the stale pointer OPEN-45 warns about
for mutable `current_*` columns. **The dilemma does not arise because nothing
updates.**

`source_ordinal` became `NOT NULL`: nullable, it could not distinguish two
separate assertions of the same value from one row seen twice, and NULLs do not
compare equal in a unique index.

---

### F-024 — the inversion moved the enumeration up a level; it did not remove it

**Established 2026-09-25, closing OPEN-60.**

0003's A2 was the fix for 0002's enumerated A5 — it derives its check set from
the catalogue rather than from a list of table names. **But it scoped that
derivation to `nspname = 'public'`.**

**So A2 enumerated a schema instead of a table list.** A table created in any
other schema — a staging area for bulk loads, a partitioning scheme, an
extension's own objects — escaped the provenance check **exactly as `fact`
escaped A5**, and for the same structural reason one level up.

**Fixed by enumerating what the system excludes rather than what we include:**
every schema except `pg_catalog`, `information_schema` and `pg_*`. A new schema
is in scope by default.

**`provenance_exempt` became schema-qualified** in the same change. Keyed on
`table_name` alone, a row exempting `bulk_facts` would have exempted a table of
that name in **every** schema, including one created later by someone who never
saw the list. **Widening the check while leaving the exemption unqualified would
have moved the hole rather than closed it** — and the harness tests exactly that:
an exemption naming `public.bulk_facts` does **not** silence
`staging.bulk_facts`.

**Proven side by side**, the way A2 was originally proven against A5: same
database, same moment, the public-only scope blind to the table and the
schema-wide scope firing. **B7 asserts the old scope returns 0** — if the probe
ever stops being blind, the comparison is not measuring what it claims.

---

### F-025 — the accounting constraint found a category nobody had named

**Established 2026-09-25, on the fact loader's first run against a real database.**

`coverage_quarter` carries a CHECK that every fact seen was loaded, refused or
quarantined. On the first end-to-end load it **refused the row**: 11 facts seen,
10 accounted for.

**The missing one was an exact duplicate** — two `num.txt` rows sharing 0001's
key *and* agreeing on value. Collapsing them loses nothing, which is exactly why
the category was invisible: it is neither a load, nor a refusal, nor a
quarantine, and every counter in the design was one of those three.

**So a whole class of row had no counter, and nothing would have said so.** The
load would have completed, the store would have held the right facts, and
`facts_seen` would have exceeded the sum of its parts by however many exact
duplicates the quarter contained — a discrepancy with no name attached, in a
column set that looks complete.

**`collapsed_duplicates` now exists, and it is derived rather than counted:**

```python
collapsed = len(rows) - len(loadable) - len(quarantined)
```

Derived from what `partition_collisions` actually did, so it cannot drift from
the behaviour it describes. A counter incremented in the loop would have been a
second implementation of the same decision, free to disagree with the first.

**Why this is the finding rather than a bug note.** The constraint was written
to catch a *silent drop* — a loader losing rows and reporting a clean load. It
did not catch that. It caught **an incomplete taxonomy of outcomes**, which is a
different and more interesting failure: the counters were not wrong, they were
not exhaustive, and the difference is invisible until something forces the sum.

> **An arithmetic constraint over a set of counters tests something no
> individual counter can: that the categories cover the space.** Each counter
> can be perfectly correct while the set omits a case, and only the requirement
> that they add up will say so.

Related to `a-guard-never-seen-red-is-not-a-guard`: this guard went red on its
first real use, in a case its author had not anticipated, which is the strongest
evidence available that it was worth writing. It would have been entirely
reasonable to ship the counters without the CHECK — they were individually
correct — and the gap would have shipped with them.

---

### F-026 — the `segments` grammar is NOT documented, and the data carries a broken HTML entity

**Established 2026-09-25 by measurement against 2015q2 and 2026q2.**

**The question was "confirm the grammar against `readme.htm`". It cannot be
confirmed, because `readme.htm` does not state it.** In full, the documentation
of the field is:

> *"segments — XBRL tags used to represent axis and member reporting"*

No delimiter. No format. No example. **The same readme that settles `version`,
`ddate`, `qtrs` and `coreg` precisely says nothing about how `segments` is
encoded** — so the loader's grammar was established from data whether anyone
intended that or not, and the code now says so rather than implying a
specification exists.

**That is the finding, and it changes what the parser's refusal counter is
for.** With a documented grammar, a refusal means bad data. With an undocumented
one, a refusal means **either** bad data **or** a wrong reading, and the two are
not separable from inside the loader.

---

**The measurement then found a real defect, at 12,503 rows per quarter.**

| | 2015q2 | 2026q2 |
|---|---|---|
| `num.txt` rows | 2,588,598 | 3,608,711 |
| non-empty `segments` | 1,066,226 (**41.2%**) | 2,189,835 (**60.7%**) |
| accepted *before* the fix | — | 2,177,332 (**99.43%**) |
| **accepted after** | **1,066,226 (100%)** | **2,189,835 (100%)** |

Row counts reproduce the register's earlier figures exactly, which is a check on
the fetch as well as on the parser.

**The cause: FSDS's own extraction leaves bare `amp;` inside member values** —
the wreckage of an HTML entity whose ampersand was stripped.

```
InvestmentIdentifier=Dun amp; Bradstreet Corporation, First lien senior secured loan;
InvestmentIdentifier=8th Avenue Food amp; Provisions, Inc., First lien senior secured loan 1;
InvestmentIdentifier=Cube Industrials Buyer, Inc. and Cube Aamp;D Buyer Inc., ...
```

**So the delimiter character occurs inside the values it delimits.** Splitting
on `;` cut `Dun & Bradstreet` in half and refused the row.

**The fix is structural rather than a special case:** a semicolon ends a pair
only when what follows begins another one. A fragment containing no `=` cannot
be a new pair, so it rejoins the previous member. That is derived from the
grammar's own shape and needs no list of known-bad strings.

**The mangling is PRESERVED, not repaired.** `store, don't filter`: un-escaping
`amp;` to `&` is a correction that cannot be justified per row, and every value
carries the same distortion, so the store stays internally consistent. The
distortion is recorded here instead of silently patched — and because dimensions
are part of `fact_one_per_filing`, patching some rows and not others would
manufacture false distinctions in the uniqueness key.

**What is still not established**, and it follows directly from the first
paragraph: whether a member value may legitimately contain `=`. If one does, the
rejoin would mis-split it. **Zero occurrences across 3,256,061 real values in
two quarters eleven years apart** — which is strong evidence and is not the same
as a specification. Noted rather than closed.

**The third instance of the same shape this sitting.** OPEN-60's A2 enumerated a
schema; A5 tested a proxy; this assumed a documented grammar existed. Each was
reasonable, each was wrong in the same direction: **a stated basis that turns out
to be narrower than the thing it is standing in for.**

---

### F-027 — the live cluster is PostgreSQL 16.15, and everything was proven on 18.3

**Established 2026-09-25, closing OPEN-30**, by `SELECT version();` in the same
session that proved `stockgrader_schema_admin` — the cheapest possible
resolution, exactly as OPEN-30 proposed.

```
server 16.15 (Debian 16.15-1.pgdg13+2)
```

**Two majors from where every migration was developed.** 0001 through 0004, the
runner, and every A/B/C verification were proven on local **18.3** and had never
met the version they would actually run on. Generated columns, `jsonb`
behaviour, exclusion constraints and `NULLS NOT DISTINCT` have all moved between
recent majors, so *hermetic-against-the-wrong-major* proves a migration runs
**somewhere**.

**The outcome was good and the guard was still right.** All four applied and
verified against 16.15 unchanged. **That is a result, not a non-event** — it was
discovered by applying to a disposable canary database rather than to
`stockgrader`, and the ordering is what made a bad outcome survivable rather
than what made this one fine.

**OPEN-30 had been open since 2026-09-23** and was resolved by one statement
costing nothing, folded into a step the owner was already performing.

---

### F-028 — the dashboard password flow works for a FRESHLY CREATED user

**Established 2026-09-25, closing the one unestablished step in OPEN-27.**

F-019 recorded a human setting a password in the Fly dashboard, **but for an
existing account.** Whether it worked for a newly created MPG user had never
been seen, and OPEN-27 called it out: *"If it does not, step 2 fails — and the
ordering means it fails while both compromised accounts still exist and the
recovery path is intact."*

**It works.** `stockgrader_schema_admin` was created by CLI, given a password in
the dashboard, and then **connected, ran `CREATE TABLE`, `INSERT`, `SELECT` and
`DROP TABLE`** against `stockgrader_scratch`.

**The proof step was not ceremony.** *Created-and-given-a-password* is an account
that **looks** usable; *connected-and-ran-DDL* is a usable account. The gap
between those two claims is where D-029's recovery row sat.

**So the recovery path for this platform is now established end to end and not
merely argued:** create by CLI, set the password by hand in the dashboard, store
it in the password manager, prove it with DDL. **No credential entered a
transcript**, which is the part F-021 got wrong earlier the same day.

---

### F-029 — two correct guards collided, and the collision was only findable on a real cluster

**Established 2026-09-25, on the migrations' first contact with a Fly cluster.**

0003's **A2** fired and rolled the migration back in full:

```
A2 FAILED: table(s) carry no source_fetch_id NOT NULL and are not declared
in provenance_exempt: public.keel_disposable_canary
```

**A2 was right.** That table has no provenance. But it is **a safety mechanism,
not stray data**: `keel_disposable_canary` marks a database as safe to truncate.
Its **presence** makes scratch disposable; its **absence** is what refuses the
test harness against production (testplan R-2). `db/keel_canary.sql` says in
capitals: *never add it to a migration.*

**So whether it exists is environment-dependent BY DESIGN, and that design is
itself a control.**

**Which put two correct rules in direct conflict:**

| | |
|---|---|
| **A2** fails closed on a table without provenance | so the canary must be exempted, or scratch cannot migrate |
| **A3** refuses an exemption naming a non-existent table | so a static exemption would **break production**, where no canary exists |

**A static exemption satisfies one and violates the other**, and no ordering of
the two fixes it — the conflict is in the shape of the problem, not in the
sequence.

**Resolved with a conditional exemption:** the row is inserted only where the
table actually is. Scratch gets it; production does not, because production has
no canary. **The migration does not create the canary** — it exempts one a human
already placed, so the file's prohibition stands.

**Why this is worth a finding.** Every prior A2 test used a table we invented
for the test. **This was a real table, placed by a real safety procedure, that
nobody had thought about while writing the guard** — and it was undiscoverable
hermetically, because a local throwaway database has no canary. The cost of
finding it was zero: a disposable database, a migration rolled back whole, an
unwritten ledger, and 0001/0002 still applied.

> **A guard proven only against the tables its author invented has been tested
> against their imagination.** The first real database supplied a case the
> imagination did not.

---

### F-030 — a real quarter loaded, and 5% of rows carry no value at all

**Established 2026-09-25.** First load of real SEC data through the full
pipeline, into a local PostgreSQL 18.3 cluster with 0001–0004 applied.

| | |
|---|---|
| Archive | `2026q2.zip`, 60,419,016 bytes, sha256 `d7c815395cd420cf…` |
| Submissions | 7,714 |
| Filers | 6,179 |
| **Facts seen** | **3,608,711** |
| **Facts loaded** | **3,368,813 (93.4%)** |
| Refused — co-registrant | 61,134 (1.69%) |
| **Refused — no value** | **178,555 (4.9%)** |
| Refused — filing absent | **0** |
| Collapsed duplicates | 14 |
| Quarantined | 195 |
| Extension facts | 259,489 |
| **Accounting** | **BALANCED — 3,608,711 of 3,608,711** |
| Wall clock | **3 min 9 s** → ~2.4 h for 45 quarters |

`facts_seen` reproduces the register's earlier measurement exactly, and
`refused_unknown_filing = 0` confirms that FSDS `sub.txt` is complete for the
facts in its own archive — 7,714 distinct `adsh` in `num.txt`, all 7,714
present in `sub.txt`.

---

**The number that needs a decision is 178,555.**

Every malformed refusal in the quarter had **one** cause: `value` is empty.
Verified against the raw archive rather than inferred from the counter —
179,806 rows carry an empty `value` field, of which 1,251 also carry a `coreg`
and are counted under that refusal instead.

```
0000001961-26-000014|CostOfRevenue|us-gaap/2025|20240331|1|USD||||
0000001961-26-000014|GrossProfit  |us-gaap/2025|20240331|1|USD||||
```

**These are real FSDS rows, not a parsing artifact.** The tag, taxonomy, period
and unit are all present and well-formed; the number is simply absent. Only
1,404 of them carry a footnote, so a footnote does not explain them either.

**And they are not obscure tags.** The most common are:

| Tag | Rows |
|---|---|
| `NetIncomeLoss` | 11,538 |
| `CommitmentsAndContingencies` | 9,585 |
| `ProfitLoss` | 5,143 |
| `StockholdersEquity` | 4,561 |
| `StockIssuedDuringPeriodValueNewIssues` | 4,138 |

**`NetIncomeLoss` and `StockholdersEquity` are core GQS inputs.**

**The current behaviour is to refuse and count**, which satisfies the discipline
— the rows are visible in `coverage_quarter.refused_malformed` rather than gone.
`fact.value` is `NOT NULL`, and a fact without a value is not a fact.

**But 4.9% is material and the behaviour arrived as a default rather than as a
decision.** The tension is real: *store, don't filter* says keep what the source
asserted, and what the source asserted here is **an element with no number** —
which may itself be information (a tagged line item deliberately left blank is
not the same as an untagged one).

**Recorded as OPEN-64 rather than settled here**, because it changes what the
store contains and the argument runs both ways. What is NOT in doubt: the rows
are counted, the accounting balances, and nothing vanished silently.

---

**A smaller correction, from the same measurement.** The real `num.txt` header is

```
adsh, tag, version, ddate, qtrs, uom, segments, coreg, value, footnote
```

**`coreg` sits after `segments`, not after `version`**, which is where the test
fixtures had put it. The loader is header-driven so its behaviour was never
affected — the tests passed before and after the correction, which is the
evidence for that. Fixed anyway: **a fixture that does not look like the data is
a weaker test than one that does**, and the next person to read it will take it
for the real layout.

**Also observed:** 12 of 3,608,711 rows carry 11 fields against a 10-field
header, almost certainly an embedded tab in `footnote`. They parse harmlessly
because the extra field is beyond every column the loader reads. Noted, not
acted on.

---

### F-031 — 3.37 million facts are in a real Fly cluster, and the counts are identical across two major versions

**Established 2026-09-25.** The first load of real SEC data into
`stockgrader_scratch` on `kzpwm0j1dm204nv3`, PostgreSQL **16.15**.

**Every counter reproduces the local run on 18.3 exactly:**

| | Local 18.3 | Fly 16.15 |
|---|---|---|
| facts seen | 3,608,711 | **3,608,711** |
| facts loaded | 3,368,813 | **3,368,813** |
| refused — co-registrant | 61,134 | **61,134** |
| refused — no value | 178,555 | **178,555** |
| refused — filing absent | 0 | **0** |
| collapsed duplicates | 14 | **14** |
| quarantined | 195 | **195** |
| extension facts | 259,489 | **259,489** |
| accounting | BALANCED | **BALANCED** |

**Same bytes, same code, same answer across two major versions.** Nothing in the
loader is environment-dependent, and the divergence that would have stopped the
work did not occur.

**This retires the largest unvalidated assumption in the project.** Four
migrations, the runner, the EDGAR client, slice 1's patterns and the fact loader
had been proven only on local throwaway clusters that were then deleted.

---

**The period derivation is correct on 3,368,813 real rows.**

```
duration   1,460,152    rows collapsed to a point: 0
instant    1,908,661    rows collapsed to a point: 1,908,661
```

**A clean 100% / 0% split.** Every `qtrs=0` row became an instant with
`period_start = period_end`; no duration collapsed. OPEN-41 warned that an
off-by-one-quarter error here is **silent** and poisons every growth metric in
§4.1 — and that a sample-inferred encoding *would look right on the samples it
was inferred from*. This is the derivation meeting 3.4M rows rather than a
fixture, and it holds.

**The quarantine caught the case the register documented.** `fact_collision`
holds 195 rows. `DerivativeAssetFairValueGrossLiability` carries competing
values including **-3,123,000 and 706,000** and **645,000 and 1,591,000** — the
exact pairs recorded in `F-next/fsds-violates-its-own-documented-key` when the
collision was first measured. **Both sides are stored.** `ON CONFLICT DO NOTHING`
would have kept one and discarded the other with no record.

**`coverage_window` reports `2026q2..2026q2`, 1 quarter, 0 gaps**, refused
239,689 — which is 61,134 + 178,555 exactly.

---

### F-032 — the Basic write path is the constraint, and it is index maintenance

**Established 2026-09-25, by a load that stalled for roughly three quarters of
an hour.**

The first proxy load died mid-`executemany` (connection closed). The second,
using COPY for the facts, reached the fact insert and then appeared to hang.

**`pg_stat_database` could not answer why, and I misread it.** `tup_inserted`
read 0 and I took that as *nothing has happened*. **Those counters are flushed
at transaction boundaries**, so for an uncommitted transaction they report
essentially nothing regardless of the work done. The probe could not answer the
question it was asked, and the conclusion drawn from it was wrong.

**`pg_locks` answered it.** The transaction held `RowExclusiveLock` on `fact`
and on **all seven** of its indexes:

```
fact_pkey                fact_one_per_filing      fact_accession_idx
fact_concept_period_idx  fact_consolidated_idx    fact_entity_concept_idx
fact_source_fetch_idx
```

**Seven index structures maintained per row, 3.4M rows, on 1 GB of shared-CPU
instance.** Locally that phase costs ~50 s because the indexes sit in RAM. On
Basic they do not, so each insert becomes random I/O.

**This is OPEN-57's question arriving on the WRITE path.** Both previous attempts
to settle Basic's adequacy measured **reads** — a point-in-time query. Neither
touched ingest. The tier's first real constraint showed up somewhere nobody was
looking, and it showed up in a disposable database on quarter one of forty-five.

**The fix follows from OPEN-57's own evidence:** an index **build** is cheap —
1,075 MB in 15.4 s even under a 1 GB cgroup — while **maintenance during insert**
is not. So `--defer-indexes` drops `fact`'s five query indexes for the load and
rebuilds them after. `fact_pkey` and `fact_one_per_filing` are **not**
deferrable: without the latter the insert has no conflict arbiter and duplicate
facts become representable, which is the one thing 0001 exists to prevent.

**It did eventually complete without the fix**, and every counter matched. So
this is a cost finding, not a correctness one — but at ~45 minutes per quarter it
is **~34 hours for 45 quarters**, against ~2 hours at local speed.

---

### F-033 — three probes reported confidently on work that had not happened

**Recorded together because they are one shape, all on 2026-09-25.**

1. **`tup_inserted = 0`** read as *nothing inserted*, when the counter simply is
   not flushed mid-transaction. See F-032.
2. **An index drop-and-rebuild check printed `DEFINITIONS IDENTICAL`** while the
   rebuild had crashed on a syntax error. It compared a file to itself and
   reported agreement.
3. **The red-test harness's precondition** hardcoded `"applied 3 migration"`;
   when 0004 arrived it reported `SETUP FAILED` on every case rather than
   silently passing — **the one of the three that failed safe**, because the
   check asserted a specific expectation instead of a mere absence of error.

**The pattern, and it is the project's oldest:** *a check that cannot run
reports the same thing as a system with no defects.* Previously recorded for a
`psql` harness broken by an unquoted path with a space, and for A2's scope, and
for A5's proxy.

**What distinguishes (3) from (1) and (2) is worth stating.** It compared against
a **stated expectation** and failed loudly when reality moved. The other two
compared a thing to itself, or read a counter whose semantics were assumed. **A
probe that cannot fail is not evidence**, and the way to tell the difference is
to ask what result would have made it complain.

The index check now prints the intermediate count — 7 indexes, then 2, then 7 —
so the drop is **proven to have happened** before the comparison is trusted.
