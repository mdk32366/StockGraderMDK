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

