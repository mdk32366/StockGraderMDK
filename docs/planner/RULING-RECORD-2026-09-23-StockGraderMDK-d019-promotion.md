# RULING RECORD — Owner → Planner → Code — StockGraderMDK: D-019 promotion

**From:** Planner, recording an owner ruling received 2026-09-23
**Issued:** 2026-09-23, first issue
**Supersedes:** nothing. **Answers:** §5 of
`REPORT-Code-2026-09-23-...-D3-applied-PR6-open.md`

---

## 1. The ruling

**D-019 — `windows-setup` is promoted to a required check. RULED.**

A red on Windows now blocks merge to `main`. The counter existed because the
check was new and unproven; ten consecutive green runs with no reds, across five
branches and four merges, is the threshold the owner set for when that stops
being the reason to hold back. It was met and the ruling was made on it rather
than reached by default.

**The caveat is recorded with the ruling, not against it.** Those ten runs are
ten runs of a repo with 22 tests and almost no application code. `windows-setup`
has not been stressed by dependency churn, and ingest — the next work — is
exactly what stresses a Windows setup path. That is the argument for promoting
now: a check made required *after* the churn is one that was proven against
nothing and then made load-bearing at the moment it started to matter.

**D-019 status:** PROPOSED → RULED. The counter is retired.

---

## 2. What the promotion requires

**Branch protection on `main` is a repository settings change, not a commit.**
It is made either in the GitHub UI — Settings → Branches → the `main` protection
rule → require status checks → add `windows-setup` — or through `gh api` if the
Builder's token carries admin scope on the repository.

**Builder: check the token's scope and say which path applies.** If it is a UI
change it goes to the owner as a single step, described rather than commanded,
since there is no command to hand over.

**Immediate interaction with PR-6, checked:** PR-6 is open and its
`windows-setup` is green, so promotion does not block it. Adding a required check
applies to open PRs immediately, and it is worth confirming PR-6 still shows
mergeable after the change rather than assuming it.

---

## 3. Verification — and the direction that actually proves it

Promotion is verified when a pull request shows `windows-setup` as **Required**.
That proves the setting took. It does not prove the block works.

**The proof in the refusing direction is a deliberate red that blocks a merge** —
the same both-directions discipline the deploy gate was proven under. It costs
one throwaway branch with an intentionally broken Windows setup step.

**Not scheduled today.** Recorded as a testplan open item so it is a thing we
have not done yet rather than a thing we believe. A required check that has never
refused anything is a required check in name.

---

## 4. The reversal path, named in advance

If `windows-setup` proves flaky on runner-side failures rather than real ones, a
required check becomes a merge block with no defect behind it. The reversal is
the same settings change in reverse, and naming it now makes it a decision rather
than a scramble.

**Condition for reversal:** a red attributable to the runner rather than to the
repository, twice. One is noise.

---

## 5. Carried forward from the previous ruling

The counter is retired, so `F-next/d019-counter-fell-behind` must record the
**lesson** rather than the incident: a value with a known, tolerated error has a
place for a real error to hide, because a count that is supposed to lag does not
look wrong when it lags further. That generalises past this counter, which is why
it should outlive it.

The recompute-never-increment rule stands for any counter this project keeps.

---

## 6. Unchanged

The drill is the thing waiting. Amended §4, eleven steps, owner at the keyboard,
one command at a time. Then B-9. Then ingest per rulings 4 and 5.

Blocked: the scoring build order, on §11.1 / §5.4 only.
