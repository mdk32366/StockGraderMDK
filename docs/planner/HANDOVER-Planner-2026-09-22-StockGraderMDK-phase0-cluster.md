# HANDOVER — Planner → Code — StockGraderMDK: Phase 0, cluster created

**From:** Planner · **Date:** 2026-09-22
**Session:** owner-run, terminal, with the Planner. Every command below was
executed and its output seen; nothing here is a command that merely looks right.
**Status:** Phase 0 steps 1–4 done. **Steps 5–6 are yours.**

---

## 1. Cluster facts (no credentials in this document)

| Item | Value |
|---|---|
| Cluster ID | `d1zj5omk443ryqkv` |
| Name | `stockgrader-db` |
| Region | `sjc` (D-017 holds — MPG is available there) |
| Plan / disk | `basic` / 10 GB |
| Status | ready |
| Database | `stockgrader` (created deliberately, not the `fly-db` default) |
| App attachment | attached to `stockgradermdk` |
| `DATABASE_URL` | Fly secret, **Deployed**, digest `4d80594c9b6ff503` |
| Accounts | `fly-user` (schema_admin), `stockgradermdk` (schema_admin) |
| Backup | one completed full, `20260922-192041F`, 2026-09-22T19:20:41Z |

**You will not be given any credential.** The app reads `DATABASE_URL` from its
injected environment. For your own work use `fly mpg connect` or
`fly mpg proxy` — the cluster is inside the private network and is not reachable
from the public internet.

## 2. `architecture.md` — recovery rows, ready to write

Row 1, replacing "Not established":

> `fly mpg backup list <CLUSTER_ID> --all` — run against `d1zj5omk443ryqkv` on
> 2026-09-22; returned one completed full backup (`20260922-192041F`). Without
> `--all` it lists only the last 24 hours. Retention is 10 days.

Row 3 addition — restore builds a **new** cluster:

> `fly mpg restore <CLUSTER_ID> --backup-id <ID>` restores into a NEW cluster, so
> recovery is not finished when the data comes back. It is finished when the app
> points at the new cluster: `fly mpg attach` **and then**
> `fly secrets deploy`. See F-015 — the deploy half is the step that silently
> does not happen.

Row 4 stays **Never**, and now has a specific reason to be tested on a quiet day:
the restore path ends in the same attach-and-deploy sequence that F-015 caught.

## 3. Findings from this session — write them in PR-5

**F-014 — Fly commands print live credentials in normal, successful output.**
`fly mpg create` printed the full connection string for `fly-user`, and
`fly mpg attach` printed it for `stockgradermdk`, in both cases in the same block
as the cluster and app details the owner needed to relay. Both reached a planning
chat. Nobody was careless; the tooling hands you the secret at the exact moment
you are relaying the surrounding information. Consequence: two credentials
compromised on the day the cluster was created. Mitigation is mechanical, not
attentional — see D-030.

**F-015 — `DATABASE_URL` was left Staged by the attach.**
`fly secrets list` showed `DATABASE_URL` as **Staged** while
`STOCKGRADER_API_KEY` read Deployed. The running machine did not have the
connection string. `fly secrets deploy` fixed it in seconds and both then read
Deployed. This is the KEEL Principle 4 scar observed live: a secret that looks
set while the app holds the old value. It was harmless only because nothing
queries the database yet. Artifact: the two `fly secrets list` outputs.

**F-016 — the backup-list command has been run, and a backup exists.**
Principle 1's three sentences have real answers for the first time on this
project: a completed backup exists; exposure is everything since 19:20Z; it does
not cover the scratch database or anything ingested before the next backup.

**F-017 — Step 16's separation was nominal as first configured.**
`fly mpg users list` showed both accounts at `schema_admin`. Two accounts
differing only in name give the recovery account no capability the application
lacks. `fly mpg users create --help` then showed three roles —
`schema_admin`, `writer`, `reader` — so this was our default, not a platform
ceiling. Corrected by D-031.

## 4. Decisions from this session — write them in PR-5

**D-029 — both exposed credentials are replaced or rotated before the first real
data load (Phase 2). PROPOSED.**
Until then both are treated as compromised. The cluster holds nothing that
matters, which is what makes this cheap now and expensive later. The application
credential goes first. **A rotation is not complete when the password changes —
it is complete when a request to the live service proves the new one is in use.**
`/healthz` cannot prove it; the first DB-backed endpoint can.

**D-030 — credential handling. PROPOSED.**
- Credentials live as Fly secrets and are consumed from the injected environment
  at runtime. Never in a repo file, never in an env file, never in a chat.
- **Fly secrets are write-only.** `fly secrets list` returns names and digests;
  no command returns a value. The platform is where credentials are put, not
  retrieved. A human who needs one rotates it rather than looking it up.
- The exception is the Step 16 recovery credential, which is in the password
  manager precisely because the platform will not give it back.
- Prefer `fly secrets import` from stdin over `fly secrets set KEY=value`, which
  puts the value in shell history.
- Known offenders that print live credentials: `fly mpg create`,
  `fly mpg attach`. Redact before relaying.
- Residual, stated rather than hidden: anything in a machine's environment is
  readable by anyone who can `fly ssh console` into it. "Never printed" is a
  habit; least privilege and rotation are the controls.

**D-031 — the application connects as a `writer`, not a `schema_admin`.
PROPOSED.**
Under D-021 migrations run from the Builder, so the web process needs rows, not
schema rights. **Replace rather than rotate:** create a new user at `writer`,
attach with it, `fly secrets deploy`, verify, then drop the exposed
`stockgradermdk` account. That closes D-029's application half and F-017's
over-privilege in one pass, and never rotates a credential in place.
`fly-user` stays at `schema_admin`, in the password manager, as the Step 16
recovery account — which then means something, because the gap is real.

**A-017 — a `writer` can do everything the application needs. ASSUMED.**
Falsified when the app cannot run its queries, or when the migration runner
turns out to need the app's credential. **Test it against the scratch database
before it becomes the live path**, not at Phase 1.

## 5. Your remaining Phase 0 steps

**Step 5 — the scratch database.** Check `fly mpg databases --help` first; we
have not seen its create syntax. Create `stockgrader_scratch` on the same
cluster and run `db/keel_canary.sql` against **that one only**. The canary marks
a database as disposable; running it against `stockgrader` is one of the two
deliberate acts that would defeat the guard.

**Step 6 — close OPEN-1.** Run `postgres_probe` against both:
- `stockgrader_scratch` → canary present, small → **accepted**;
- `stockgrader` → no canary → **refused**.

Confirm the probe is read-only before pointing it at the real database, as you
said you would. The refusal against a database that now actually matters is the
finding; until it exists, the guard has only ever been proven against fakes.

While you are there, test A-017: connect as a `writer`-role user against the
scratch database and confirm it can do what the app needs and cannot alter the
schema.

## 6. Two gaps worth recording as testplan open items

**The gate cannot see a staged secret.** F-015 passed every check we have,
including the live-SHA verification, because the SHA is baked into the image and
has nothing to do with secrets. A DB-backed endpoint plus a check that it
actually answers from the database would close this. Not buildable until there
is such an endpoint — so it is an open item, not a guard.

**The `pharmfoldmdk` app is attached to two MPG clusters.** Seen in
`fly mpg list`. Out of scope for this project, and flagged because it is
PharmFoldMDK's own §3.1 shape — a write that appears to succeed against a
connection nobody proved. Owner's call, another day.

## 7. [OWNER] close-out list, this session

1. Replace the application credential per D-031 (`writer`, attach, deploy,
   verify, drop the old user).
2. Rotate `fly-user`.
3. Confirm `fly-user`'s password is in the password manager under the project
   name — Step 16's actual proof.
4. API key out of `Downloads\STOCKGRADER-API-KEY-move-to-password-manager-then-DELETE.txt`,
   then delete the file.
