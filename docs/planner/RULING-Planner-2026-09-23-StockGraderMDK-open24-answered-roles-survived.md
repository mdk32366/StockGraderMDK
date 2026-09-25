# RULING — Planner → Code — StockGraderMDK: OPEN-24 answered, ruling 6 void, deadline set

**From:** Planner · **Issued:** 2026-09-23, first issue
**Answers:** OPEN-24, by owner-run `fly mpg users list kzpwm0j1dm204nv3`
**Supersedes:** ruling 6 of `RULING-RECORD-...-owner-rulings`; the D-029 closure
path; §3's over-privilege claim in the drill report

---

## 1. The finding

```
 NAME            │ ROLE
 fly-user        │ schema_admin
 stockgrader_app │ writer
 stockgradermdk  │ schema_admin
```

**`fly mpg restore` carries the role catalogue.** Both credentials compromised on
2026-09-22 exist on the **live** cluster with their original passwords.

Record as `F-next/restore-carries-compromised-roles`. The general form is the one
to keep: **a restore reproduces the source's security state, not just its data.**
A recovery from a compromise restores the compromise.

---

## 2. What this makes false

**Ruling 6 is void.** It held that destroying the old cluster retires both
exposed credentials, and that this was D-029 closing by replacement rather than
rotation. **The destroy now retires two copies that no longer matter.** The
originals are live on `kzpwm0j1dm204nv3`.

**The cutover's main stated purpose was not achieved.** The drill report says
F-017's over-privilege is not rebuilt on the clean cluster. **There is no clean
cluster** — a restore is a copy. `stockgradermdk` at `schema_admin` came across
with the data.

**D-029 has no closure path at present.** It was resting on ruling 6.

**What does still stand:** D-031 in full. The app connects as `stockgrader_app`
at `writer`, verified from the connection string's components. That was real work
and it is untouched. The defect is the residue, not the replacement.

---

## 3. The honest risk, neither inflated nor dismissed

The cluster sits inside the private network and is not reachable from the public
internet. A credential alone buys nothing without Fly organisation access — and
anyone with that access does not need the credential. So the practical
probability of exploitation is **low**, and it was low this morning when the
owner deferred rotation on that basis.

**What changed is not the probability. It is two other things.**

**The register asserts things that are false.** It records D-029 closing by a
destroy that will not close it. A wrong record is worse than a known risk,
because nobody re-examines it.

**And the remediation has a deadline**, which it did not have this morning.

---

## 4. The deadline — before migration 0001 runs

**`stockgrader` and `stockgrader_scratch` are empty of owned objects except the
canary.** Right now a role drop is close to free.

**After migration 0001 creates tables, those tables have an owner.** Dropping a
role that owns objects fails until ownership is reassigned or the objects
dropped — `REASSIGN OWNED` / `DROP OWNED`, run against the right database, by an
account with the right rights, on a cluster that by then holds the fact store.

**So the cheapest moment is now, and it closes when 0001 runs.** That is a
concrete gate, not an exhortation: **migration 0001 does not run against
`stockgrader-db-r1` until §5 is done.** Its design (D8) is unaffected and
proceeds.

---

## 5. What has to happen, as questions before commands

Nothing here is a command to hand over yet, because the syntax is unestablished
and this project does not hand over guesses.

**5.1 — Establish the mechanism.** `fly mpg users --help`. Does a delete or
destroy subcommand exist? If MPG offers no role removal, the operation is SQL
over `fly mpg proxy` and that is a different handover.

**5.2 — Establish whether `stockgradermdk` owns anything.** The canary table in
`stockgrader_scratch` was created during phase 0 by some account. If it is this
one, the drop needs ownership handled first. Check before attempting, not after
a failure message.

**5.3 — Drop `stockgradermdk`.** It is not the app's path; `stockgrader_app` is,
verified. Nothing should break. Confirm nothing does.

**5.4 — `fly-user` is harder and must not be dropped reflexively.** It is the
Step 16 recovery account — the credential in the password manager that exists
precisely because the platform will not hand it back. Dropping it without a
replacement removes the recovery path to fix a credential exposure, which is a
poor trade.

Establish first: can a replacement `schema_admin` be created and `fly-user`
dropped, or is `fly-user` MPG-provisioned and undroppable? If undroppable, the
answer is rotation rather than replacement, and D-030's exception applies — the
new value goes to the password manager under the project name.

**5.5 — Then the old cluster's destroy becomes ordinary housekeeping**, which is
all it ever was. Capture `fly mpg status d1zj5omk443ryqkv` first, per OPEN-22.

---

## 6. For the owner

This is the deferral from this morning arriving with a date on it. The reasoning
then — everything is rebuildable, the risk is low — was sound and I agreed with
it. It rested on there being no cost to waiting.

**There is now a cost to waiting, and it is not about risk.** It is that the
operation is nearly free while the database is empty and becomes a
schema-ownership problem the moment it is not. The work is small; it is only
small today.

**Owner's call whether §5 runs before migration 0001 or the gate in §4 is
lifted.** Recorded as a decision either way.
