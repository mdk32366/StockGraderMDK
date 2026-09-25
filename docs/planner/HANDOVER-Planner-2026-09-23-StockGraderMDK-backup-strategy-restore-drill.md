# HANDOVER — Planner → Code + Owner — StockGraderMDK: backup strategy and restore drill

**From:** Planner · **Date:** 2026-09-23
**Predecessors:** `HANDOVER-Planner-2026-09-22-...-phase0-cluster.md`,
`HANDOVER-Planner-2026-09-23-...-phase0-steps5-6.md`
**Supersedes:** §5 of the steps 5–6 handover (the credential deferral). Cutover
closes D-029's application half as a side effect; the deferral is moot.

**Runs after** the steps 5–6 block. A-017 must have held on scratch before any
`writer` account is attached to a live path.

---

## 1. Platform facts — verified from Fly documentation, 2026-09-23

Documentation is not the installed binary. Every one of these is re-verified by
a `--help` in §3 before anything depends on it.

| Fact | Consequence |
|---|---|
| MPG backs clusters up automatically on a rolling schedule; backups are kept **10 days** | `20260922-192041F` is not a one-off artifact. But 10 days is the whole horizon. |
| No MPG command was found to configure cadence or retention | Retention is a platform constant, not a dial. Anything needing a longer horizon is produced by us. |
| `fly mpg backup create <CLUSTER_ID> --type full\|incr` exists | Manual backups on demand. This is the hook for pre-risk checkpoints. |
| `fly mpg restore` restores **into a new cluster**, from a backup **or a point in time** | PITR may be available. The `--backup-id` flag is documented; the PITR flags are not. Establish in §3. |
| `fly mpg destroy` exists | The old cluster is disposed of deliberately, not abandoned. |

---

## 2. Backup strategy — PROPOSED, numbers to be assigned in PR-5

**B-1 — Automatic backups are the floor, not the plan.** The rolling schedule
covers the last 10 days of ordinary operation. Everything below is what the
schedule does not do.

**B-2 — A manual full backup is taken immediately before any deliberate act that
could destroy data.** Specifically: before a migration, before a bulk load,
before a cutover, before a destroy. `fly mpg backup create <CLUSTER_ID> --type
full`. The cost is minutes; the alternative is depending on whenever the rolling
schedule last happened to fire.

**B-3 — A manual full backup is taken immediately after a cutover.** Restore
builds a new cluster, and backup history does not follow it. A freshly restored
cluster has no backup lineage until one is made or the schedule fires, and the
window between those is unguarded.

**B-4 — A backup that exists is not a backup that restores.** Row 4 of the
recovery table stays **Never** until a restore has been driven end to end,
including the cutover half. §4 of this document is the first execution. It is
re-run after the ticker load, when row counts make the data half meaningful too.

**B-5 — Recovery is not finished when the data comes back.** It is finished when
the app points at the new cluster and a request to the live service proves it:
`fly mpg attach`, **then** `fly secrets deploy`, then verify. F-015 is the scar —
the deploy half is the step that silently does not happen.

**B-6 — 10-day retention is an expiry, and expiry is silent.** Nothing on the
platform will tell you the recovery point you were relying on has aged out.
`fly mpg backup list <CLUSTER_ID> --all` is the only way to know, and without
`--all` it shows only the last 24 hours.

**B-7 — Off-platform copies are not required today, and the condition that
requires them is written down.** Everything in `stockgrader` is rebuildable by
re-running the loader, so 10 days on-platform is sufficient. The first write that
cannot be rebuilt from source — anything user-owned, anything whose loss is not
fixed by a re-run — makes an off-platform dump mandatory. This is the same
tripwire that ends the credential deferral.

**B-8 — The scratch database is explicitly out of scope.** `stockgrader_scratch`
carries the canary, which marks it disposable. It is not backed up on purpose,
and it is not a reason to restore anything.

---

## 3. [CODE] Establish the mechanics — read-only, no state changes

Run these and report verbatim. Do not act on any of them in this block.

1. `fly mpg backup --help`
2. `fly mpg backup create --help`
3. `fly mpg backup list --help`
4. `fly mpg restore --help` — **specifically**: does this build support
   point-in-time restore, and with what flags? The docs index describes a point
   in time; the restore page documents only `--backup-id`. Resolve it against the
   installed binary.
5. `fly mpg destroy --help`
6. `fly mpg backup list d1zj5omk443ryqkv --all` — how many backups exist now, and
   has a second one appeared since `20260922-192041F`? This answers whether the
   rolling schedule is observably running on *this* cluster, rather than in
   general.
7. `fly mpg status d1zj5omk443ryqkv`

**Finding to record** (number in PR-5): whether the rolling schedule is
observable on this cluster, and whether PITR is available. Both change the
strategy above if they come back other than expected — stop and report rather
than proceeding to §4.

---

## 4. [OWNER] The restore drill — one command at a time

**Code hands these over one at a time, waits for output, confirms, then hands the
next. If any step returns something unexpected, the sequence stops.**

**Ruling assumed: cutover-and-stay.** The restored cluster becomes the live one
and today's ticker load goes onto it. Say so now if you want
cutover-and-revert instead; steps 6–9 change.

**Redaction points are marked. Those commands print live credentials (F-014).**

1. `fly mpg backup create d1zj5omk443ryqkv --type full` — the pre-cutover
   checkpoint, per B-2. Wait for completion.
2. `fly mpg backup list d1zj5omk443ryqkv --all` — confirm the new backup is
   listed and completed. Record its ID.
3. `fly mpg restore d1zj5omk443ryqkv --backup-id <ID from step 2>` —
   **REDACT before relaying.** Record the new cluster's ID and name.
4. `fly mpg status <NEW_CLUSTER_ID>` — wait for ready.
5. `fly mpg databases <list — exact syntax from the steps 5–6 block>` against the
   new cluster. Confirm `stockgrader` came across. Note whether
   `stockgrader_scratch` did too — either answer is informative and neither is a
   failure.
6. `fly mpg users create` on the new cluster at **`writer`** role —
   **REDACT.** A-017 must have held in the earlier block before this runs.
   Per D-031 the app connects as a writer, not a schema_admin; a cutover that
   re-attaches as schema_admin rebuilds the F-017 problem on a clean cluster.
7. `fly mpg attach <NEW_CLUSTER_ID>` with the writer account —
   **REDACT. Named F-014 offender.**
8. `fly secrets list` — `DATABASE_URL` will read **Staged**. This is F-015
   reproducing on demand. Confirm you see it before fixing it.
9. `fly secrets deploy` — then `fly secrets list` again. Both secrets Deployed.
10. Verify the app is alive. `/healthz` is the only endpoint there is, and per
    D-029 it cannot prove the database half. State that limit in the record
    rather than letting a green check stand in for a verification that has not
    happened. The DB-backed proof arrives with the first real endpoint, today.
11. `fly mpg backup create <NEW_CLUSTER_ID> --type full` — per B-3. The new
    cluster has no backup lineage until this completes.

**Do not destroy the old cluster today.** It holds nothing and costs little.
It is destroyed after the ticker load and scoring are proven on the new cluster.
Note that the exposed `stockgradermdk` credential remains valid against the old
cluster until that destroy — it is no longer the app's path, but it is not dead.

---

## 5. What closes, and what does not

**Closes today, if §4 completes:** Row 4 of the recovery table moves off
**Never** — the restore path has been driven end to end including cutover.
D-029's application half closes without rotating anything in place: the app now
runs on a credential that was never printed into a chat, on a cluster the exposed
one does not reach. F-017's over-privilege closes, if step 6 attaches as writer.

**Does not close.** The gate still cannot see a staged secret — step 8 will
reproduce F-015 deliberately, which demonstrates the gap rather than fixing it.
It is buildable as a real guard once today's DB-backed endpoint exists, and that
is the moment to build it.

`fly-user` on the old cluster is still exposed and still unrotated. The old
cluster's destroy retires it. Until then it is a live credential against a live
cluster, and that is a fact rather than a hypothetical.
