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

### F-next/orphaned-restore-clusters-already-exist - The account holds restore artifacts from earlier recoveries, still running
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
