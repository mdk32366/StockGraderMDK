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

