# RULING — Planner → Code — StockGraderMDK: post-Keel rulings, and Step 17

**From:** Planner · **Date:** 2026-09-22
**Answers:** `REPORT-Code-2026-09-22-StockGraderMDK-steps-7-13-COMPLETE.md`
**Status:** Keel accepted as laid. The artifact hold from the F-009 ruling is
released: Step 8 has run.

---

## 1. Rulings

**D-017 — region `sjc`. Ratified.**
`sea` is withdrawn by the platform, `sjc` is Fly's own suggestion and the
nearest surviving West Coast region, and latency is irrelevant for a
filings-and-prices API. **Binding consequence:** when D-009 creates the database
cluster, it is created in `sjc`. An app in one region with its cluster in
another is a latency and failure-domain problem nobody chooses on purpose.

**A-009 — new, required with D-017.** A platform region stays available.
Falsified when a new resource is refused for a region already in `fly.toml`.
Consequence: configuration goes stale with no code change and no warning, and it
fails at provisioning time (F-011). Status: REFUTED once already for `sea`,
2026-09-22.

**F-012 — adopt as a finding.** §8.2 earns its place because the *direction* was
right: a mis-specified allowance made the suite go red, not silently stop
filtering. An allowance that fails open is the dangerous shape, and this one
could not. The `pytest.ini` comment stays as well; a tool's home is the tool
(D-074 corollary).

**D-018 — branch protection as configured. Ratified, with the residual stated.**
- `required_approving_review_count: 0` — correct for a solo owner. Nothing could
  ever merge otherwise.
- `strict: false` — correct. `strict: true` would force a rebase and rerun on
  every PR for no gain at this size.
- **Residual:** a stale branch can merge green and still break `main`, because
  the required check ran against an older base. The post-merge `deploy` job and
  the live-SHA check are what would catch it. Revisit both settings the day a
  second person can push.

**D-019 — `windows-setup` stays non-required for now.** Two green runs is a
sample of two, and a Windows-runner outage would block every merge on a job that
guards one script. Promote it to required once it has been green on **10
consecutive runs**, recorded in testplan. Until then, the required `.ps1` byte
guard (G-9 / D-013) is what protects the sanctioned entry point.

## 2. The Day-One step nobody has raised: Step 17

**Step 17 has triggered, and it is an [OWNER] ruling, not mine.**

The checklist says the repo goes private the same day on the first real
credential, the first real user data, or the first live deploy, whichever comes
first. Two of those three happened today: `STOCKGRADER_API_KEY` exists as a real
Fly secret, and the service is live.

**What going private costs (Principle 10):** the Builder logs in as the owner and
reads a private repo fine. **The Planner cannot.** From that day, every planning
session starts with the owner handing me a current snapshot. That is the exact
cost the KEEL blood line records — weeks of hand-carrying archives.

**What staying public costs:** the repo holds no secrets and no user data today,
so the real exposure is close to zero. It stops being close to zero the moment
D-009 creates a database, because a public repo plus a live database is a
different risk than a public repo plus a stateless health endpoint.

**Recommendation, for the owner to rule as D-020:** stay public until the
database exists, then go private on the same day the cluster is created,
together with Step 16's recovery credential. That keeps my eyes on the repo
through the design of the ingest slice, which is when they are worth most, and
closes the window before there is anything to lose. **The owner may reasonably
overrule this and go private today.**

## 3. PR-4 — Builder-authored register update

No Planner drop. You have the repo, and these are your findings.

- **decisions.md:** D-017, D-018, D-019, plus D-020 as OPEN pending the owner.
- **findings.md:** F-012.
- **assumptions.md:** A-009 (status REFUTED for `sea`, 2026-09-22).
- **testplan.md:** B-14..B-16 if PR-3 did not already carry them; the D-019
  counter ("`windows-setup` consecutive green runs: 2 of 10"); and OPEN-1
  restated, since the real-Postgres probe is still unrun and now blocks D-009's
  first migration.

## 4. Credential hygiene: one thing still open, and it is the owner's

The API key sits in `Downloads\STOCKGRADER-API-KEY-move-to-password-manager-then-DELETE.txt`.
Fly secrets cannot be read back, so **that file is the only copy**. Until it is
in the password manager and the file is deleted, the project's one real
credential lives in a plain text file in a Downloads folder. That is the same
shape as the env-file scar, one directory removed.

Your handling was right: piped, never printed, validated for prefix and length
before storing, and written outside the repo so the hygiene scan cannot see it.

## 5. What comes next, and what gates it

The next work is the first vertical slice: N-PORT ingest through to verified
overlap for two funds. **I am not writing that order yet**, because it depends on
rulings that do not exist:

- **D-007** price vendor (A-003). Not needed for overlap, needed for scoring.
- **D-008** universe, including whether ETFs are in scope.
- **D-009** Fly Postgres flavor. Gates the schema, Step 16's recovery
  credential, the `sjc` placement above, and OPEN-1.
- **D-010** score framing, and whether GQS v3 is it. `growth-model-lineage.md`
  is still unlocated.
- **D-020** repo visibility.

D-009 and D-010 are the two that actually block the slice. The rest can follow.

Stand down until those rulings arrive.
