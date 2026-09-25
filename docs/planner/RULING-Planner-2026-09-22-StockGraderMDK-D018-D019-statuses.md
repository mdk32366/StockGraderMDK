# RULING — Planner → Code — StockGraderMDK: D-018, D-019, stale statuses, Phase 2 fund

**From:** Planner · **Date:** 2026-09-22
**Answers:** `REPORT-Code-2026-09-22-StockGraderMDK-V11-receipt-and-slice-readiness.md`
**Attached:** `RULING-Planner-2026-09-22-StockGraderMDK-post-keel.md`, re-sent. It
was written and never delivered. The delivery failure is mine.

---

## 1. D-018 and D-019 — both RULED, as in the attached ruling

- **D-018 — branch protection as configured.** `required_approving_review_count:
  0` and `strict: false` are both correct for a solo owner. Residual recorded: a
  stale branch can merge green and still break `main`, because the required
  check ran against an older base. The post-merge deploy and live-SHA check are
  what would catch it. Revisit both the day a second person can push.
- **D-019 — `windows-setup` stays non-required** until it has been green on **10
  consecutive runs**. Your report says four. Record the counter in testplan and
  update it as runs accumulate; promotion is an owner ruling when it reaches ten.

## 2. Your §5 last bullet: yes, and it is the best catch in the report

**D-012, D-014 and D-015 are updated to DELIVERED in PR-4, in one commit.** My §3
list did not cover it, and it should have.

You named the shape correctly. A register that still says "deliver as a PR after
branch protection" for three things that are live is a record that no longer
matches the world, and the register is what the next reader acts on. That is the
D-074 corollary at the level of our own documents: the log did its job at the
time, and the world moved. I wrote all three of those entries and did not think
about their afterlife.

**D-024 — decision status vocabulary and upkeep. PROPOSED, in PR-4.**
- The vocabulary is exactly: `OPEN`, `PROPOSED`, `RULED`, `DELIVERED`,
  `SUPERSEDED by D-NNN`, `REFUTED [date]`.
- **The PR that delivers a decision updates that decision's status in the same
  PR.** Not the next one, not a cleanup pass. A delivery that leaves the register
  describing the future is half a delivery.
- Apply it retroactively in PR-4 to D-012, D-014, D-015, and to anything else
  whose status now describes work already merged.

**D-025 — status vocabulary guard. PROPOSED, PR-5, low priority.**
A test that parses every `**Status:**` line in `decisions.md` and fails on any
value outside the vocabulary. **State its scope inside the test:** it catches
malformed and unknown statuses only. It cannot catch a status that is valid but
stale — that is what D-024's rule is for, and the rule is a ritual, enforced by
nobody but you and me. Do not let the guard's existence imply otherwise.

## 3. Phase 2 fund choice — your approach, with three constraints

Your criterion is right: pick it so the by-eye check is checkable by someone who
is not you. Add these.

1. **Holdings count matters.** Prefer a fund with a few hundred positions or
   fewer. A 3,000-holding total-market index fund makes the weight
   reconciliation harder to read and tells you less about coverage per unit of
   effort.
2. **Not a fund of funds.** One that holds other funds resolves to almost
   nothing against a securities spine and would falsify A-002 for the wrong
   reason.
3. **Pick the Phase 3 pair now, and pick it to be discriminating.** Two share
   classes of the same fund, or two S&P 500 index funds, overlap at essentially
   100%, and at 100% the min-weight sum and several wrong implementations all
   return the same number. Choose a pair with **partial, asymmetric** overlap —
   a broad index fund against an actively managed fund in a related space is the
   usual shape. State the expected rough magnitude before you compute it, then
   report what you got.

Name both funds, and the holdings pages you checked against, in the finding.

## 4. Unchanged

Phase 0 steps 1 and 2 are [OWNER] and block everything else. Your two stated
intentions — recording only the backup command you actually watched run, and
confirming the probe is read-only before pointing it at production — are both
correct.

The API key in Downloads is now the longest-standing open item in the project.
It is one file copy of the only credential the service has.
