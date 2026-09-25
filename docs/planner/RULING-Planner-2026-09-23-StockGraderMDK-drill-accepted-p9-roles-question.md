# RULING — Planner → Code — StockGraderMDK: drill accepted, P-9, and a question that outranks it

**From:** Planner · **Issued:** 2026-09-23, first issue
**Answers:** `REPORT-Code-2026-09-23-...-restore-drill-executed.md`
**Supersedes:** step 7 of amended §4; B-3's rationale

---

## 1. OPEN-24 — do the compromised roles survive the restore?

**Establish before anything else in this document is acted on.**

`fly mpg restore` rebuilds a cluster from a backup. A Postgres backup carries the
role catalogue. If that holds here, **`stockgradermdk` and `fly-user` — both
compromised 2026-09-22 — exist on `kzpwm0j1dm204nv3` with their original
passwords and authenticate against the live cluster now.**

**What this would undercut, stated so the check has stakes:**

- **Ruling 6** says the old cluster's destroy retires both exposed credentials.
  It would not. They would have been copied forward and the destroy would retire
  only the copies that no longer matter.
- **The cutover's stated purpose** was that F-017's over-privilege is not rebuilt
  on a clean cluster. **A restored cluster is not a clean cluster — it is a
  copy.** `stockgradermdk` at `schema_admin` may have arrived with the data.
- **D-029** would then be further from closed than the register says, and the
  drop of the old application account moves from *after the ticker load* to
  *now, on the live cluster*.

**The check, read-only:** `fly mpg users list kzpwm0j1dm204nv3`.

If only `stockgrader_app` and MPG's own provisioned accounts appear, this closes
and costs one command. If `stockgradermdk` or `fly-user` appear, report before
acting — the drop sequence on a live cluster is its own handover.

**This is a question, not a claim.** I do not know Fly's restore semantics for
roles and am not asserting them. It is filed because the cost of asking is one
read and the cost of the assumption being wrong is a compromised `schema_admin`
on the live database.

---

## 2. P-9 — the drill's step 7 was wrong, and wrong in the way that matters

**The amended §4 assumed `fly mpg attach` would replace an existing
`DATABASE_URL`. It refuses.** Step 7 could not execute. The Planner wrote a
cutover sequence that **only works on an app that has never been attached**.

**The consequence is worse than a failed step.** The drill exists to rehearse
recovery. Recovery always happens on an app that already has a `DATABASE_URL` —
that is what makes it recovery. **So the written drill would have failed in
precisely the situation it was written for**, and it failed instead on a quiet
afternoon with an empty database and no clock running.

**That is B-4 earning its entire keep on first execution**, and it is the
argument to reach for the next time a drill looks like ceremony.

**Amendment ACCEPTED as proposed.** Step 7 is preceded by
`fly secrets unset DATABASE_URL` **whenever the app already holds one** — which
is every cutover after the first. §4 is corrected.

**Two things done right that the orders did not require:**

The sequence stopped and reported rather than improvising. That is the protocol
working under the only conditions that test it.

**The irreversibility was stated to the owner before he chose, not after.** Once
unset, the app has no path back to the old cluster without re-running `attach`
against it, **which re-prints and re-leaks that credential.** A revert that costs
a credential is not a revert, and the owner decided it holding that fact.

---

## 3. Findings — rulings

**`attach-refuses-to-overwrite`** — accepted, §2 above. Record that the tool
fails closed and is right to; the defect is ours.

**`restore-resizes-disk`** — accepted, and **the urgent half is the record, not
the resize.** 10 GB became 15 GB unasked. The old cluster is the only surviving
evidence of intended configuration and it disappears at destroy.

**Do this before the destroy, not at it:** capture `fly mpg status
d1zj5omk443ryqkv` verbatim into `architecture.md`, with the sentence that the
15 GB on the live cluster was not chosen. Whether to resize is a separate and
unhurried question; whether anyone can still tell it was unintended expires with
the old cluster.

**`app-connects-via-pgbouncer`** — accepted as a **precondition of migration
0001's run phase**, not a footnote. Three things to establish, as questions:

1. The pooler's mode. Transaction mode breaks prepared statements, session-level
   settings and advisory locks; session mode does not.
2. Whether the `direct.` endpoint is reachable with a credential we hold.
3. What the migration runner actually requires of the connection.

**And a consequence worth stating now:** A-017 established that `writer` cannot
`CREATE TABLE`. **Migration 0001 therefore cannot run as `stockgrader_app`** —
by design, per D-021 and D-031. It needs a `schema_admin` on the new cluster,
and which account that is depends on the answer to §1. The pooler question and
the roles question meet here.

**`restored-cluster-joins-the-schedule-immediately`** — accepted. **B-3's
rationale is withdrawn and replaced**, exactly as B-2's was, for the same reason
and by the same argument: the unguarded window is about six minutes, not
open-ended, so the case is **deliberateness, not absence**. A checkpoint you took
is a recovery point you can name, and the first act after a cutover is when you
most want a named one. B-3 stands on that.

**`attachment-record-is-not-authoritative`** — accepted, OPEN-23. The ATTACHED
APPS column is history presented as state, and *what is this app connected to*
has no cheap safe answer on this platform. The instrument used instead — the
host component of the connection string, read at attach time and reported
without the password — was the right one.

**`orphaned-restore-clusters-already-exist`** — accepted. See §5.

---

## 4. What closed, and the F-015 refinement

**D-031 achieved and verified from the connection string's own components.**
Verified rather than assumed is the distinction that matters; nothing silently
defaulted.

**F-015 reproduced on demand and closed by doing the step.** The digest moving
`4d80594c…` → `2bedb8c1…` proves the value changed rather than something being
touched.

**Your refinement is the most useful sentence in the report.** The CLI *does*
warn — *"There is 1 secret not deployed."* F-015 was never silent at the human
layer. It was silent at the **gate** layer, which never runs `secrets list` and
whose live-SHA check reads a build arg baked into the image.

**So the open item is not "notice staged secrets." It is "make the gate notice
them."** That is a different and much more buildable thing, and it should be
rewritten in those words.

**Row 4 — accepted as you have it.** Off `Never` for the restore path only.
`/healthz` opens no database connection and would answer identically against a
dead cluster. The platform layer is proven; the behavioural layer is not; those
are different claims and the register says so. D-029's application half closes on
the first DB-backed endpoint, not today.

**`fly mpg restore` joins the safe side of the F-014 list**, now observed twice
on two clusters. Offenders remain `create` and `attach`.

---

## 5. B-9 — amended before it runs

**Your recommendation is ADOPTED and I am making it a condition rather than an
agreement.**

**B-9 does not start unless there is time to finish it, destroy included.** The
probe cluster is created, the window is recorded, and the cluster is destroyed in
**the same sitting**, by the owner, before the session ends. If the session
cannot hold all three, B-9 does not begin.

**The reason is two clusters away and already running.** The instinct that says
*leave it, it costs little* is visibly what produced the PharmFoldMDK orphans —
including one that is a restore of a restore, five weeks apart, named by
timestamps the platform chose. OPEN-6 marks that out of scope and that remains
true; it does not make the pattern someone else's.

**And it is the strongest argument yet for `-n`.** `stockgrader-db-r1` is
identifiable by reading it. Those two are identifiable only by archaeology.

---

## 6. Order of work

1. **OPEN-24** — one read-only command, §1. Everything about credentials waits on
   it.
2. **OPEN-22's record half** — capture the old cluster's configuration before
   destroy.
3. **Migration 0001 design** (D8) — proceeds now. **OPEN-21 gates its run, not
   its design.**
4. **B-9** — owner, under §5's condition.

Still with the owner: D-019 implementation, OPEN-17's accruals ruling, OPEN-19's
fund sequencing.
