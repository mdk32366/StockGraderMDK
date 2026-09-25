# RUNBOOK — provisioning the 150 GB cluster — D-039

**From:** Code (Builder) · **Date:** 2026-09-25
**For:** the owner, at the keyboard. **Every command here is the owner's.**

**The Builder cannot run any of this and must not be asked to.** No credential
reaches the Builder, and **`fly mpg create` prints a live connection string in
its normal, successful output** (F-014) — the command that creates the cluster is
the command that leaks its credential. Two roles were compromised that way on day
one. **This runbook is written so the Builder never sees a secret and the owner
never has to paste one.**

---

## 0. Read this first: it is not a resize

`fly mpg` exposes **no subcommand that changes a volume after creation**
(OPEN-56). The full list is attach, backup, connect, create, databases, destroy,
detach, list, proxy, restore, status, users. **`restore` picks its own size**
(OPEN-22), so it is not a way around it either.

**So: new cluster at 150 GB, move the data, repoint, retire the old.**

## 1. Why now is the cheapest this will ever be

| | Today | After the 45-quarter load |
|---|---|---|
| Store | **1 quarter, 3.37M facts, ~1.8 GB** | ~114 GB |
| Migration | **Re-run the loader, ~148 s** (F-034) | Dump and restore 114 GB |
| Risk | A re-load that is byte-reproducible from immutable archives | A one-shot data move |

**The FSDS archives are immutable once published and already cached on disk**, so
the new cluster does not need the old one's bytes — it needs the loader run
against it. **That is a two-minute job today and a different category of job
next week.**

**Order is therefore: new cluster first, 45-quarter load second.** Reversing them
converts a trivial migration into a large one for no benefit.

## 2. The sequence

**One command at a time. Wait for output. Confirm before the next.** Any
unexpected output stops the sequence — that is the standing rule for live-cluster
work and it has caught things.

### 2.1 Create — **this command prints a credential**

```
fly mpg create --name stockgrader-db-r2 --region sjc --plan basic --volume-size 150 --org personal
```

**When it returns, it will print a connection string containing a live password.**

- **Do not paste its output anywhere**, including to the Builder, including
  "just the cluster id part". F-021 happened because a credential sat inside a
  region of text somebody was asked to return.
- **What the Builder needs is two non-secret facts:** the **cluster id** and the
  **name**. Type those out yourself rather than copying the block.
- Note `--org personal` — `fly mpg` needs it non-interactively (closeout §1.6).

### 2.2 Confirm the size actually took

```
fly mpg list --org personal
```

**Check the new cluster reads 150 GB.** This is the one number the whole
exercise is for, and `--volume-size` is a create-time flag with a default of 10 —
a typo yields a 10 GB cluster that looks fine until it does not. **Verify it
before anything else is built on it.**

### 2.2a Create the databases — **the step this runbook originally omitted**

**A new cluster has `fly-db` and nothing else.** D-009 records that `stockgrader`
was *"created deliberately, not the `fly-db` default"*, and phase-0 §5.3 created
`stockgrader_scratch` separately. **Neither exists on a fresh cluster.** The
first issue of this runbook went straight from create to migrations, which would
have failed. F-043.

**Pass the cluster ID explicitly.** Omitting it turns a read-only command into a
blocking interactive picker — the same family as the `fly mpg connect` ban.

```
fly mpg databases create <CLUSTER_ID> -n stockgrader_scratch
fly mpg databases create <CLUSTER_ID> -n stockgrader
fly mpg databases list   <CLUSTER_ID>
```

**Create BOTH, even though only scratch holds data.** OPEN-1's real-cluster proof
is that `stockgrader` and `stockgrader_scratch` *"sit on the same cluster, same
host, same port, and were probed by the same user - nothing but the canary table
distinguishes them."* That is what makes it proof of **positive identity** rather
than a hostname check. **With scratch alone, the new cluster cannot reproduce
it** — and the old cluster is being retired. An empty database costs nothing.

**Then verify by listing** (§5.3's rule), expecting exactly three:
`fly-db`, `stockgrader`, `stockgrader_scratch`.

### 2.3 The connecting role — and `fly-user` is already a `schema_admin`

**Established on r2, 2026-09-25:** connecting with `user=fly-user` through the
proxy reports **`current_user = schema_admin`**. The phase-0 handover records
`fly-user` as holding that role and the platform resolves to it. **So the
migrations run as the role their headers name** — `RUN AS: a schema_admin` — with
no separate role needed for the migration itself.

**A dedicated `stockgrader_schema_admin` is still the right end state** and is
made this way: `fly mpg users create <CLUSTER> -u <name> -r schema_admin` prints
**only Name and Role, no password** (F-014's amendment), then **the password is
set by hand in the Fly dashboard** and stored in the password manager. That is
not a workaround — on this platform it is the mechanism. *Every credential this
project holds arrived either by a leak or by a human typing it into a browser;
there is no third route.* `fly mpg users` has no `rotate`.

**Keep `fly mpg attach` out of this — `attach` leaks too.**

### 2.3b Mark scratch disposable

```
.venv\Scripts\python.exe tools\apply_canary.py --dsn "host=127.0.0.1 port=16380 user=fly-user dbname=stockgrader_scratch" --expect-database stockgrader_scratch --i-understand-this-marks-it-disposable
```

Phase-0 §5.4 requires asserting **which database you are actually connected to**
before running the canary, because *"a proxy connected to the wrong database
looks exactly like a proxy connected to the right one."* `tools/apply_canary.py`
makes that assertion mechanical: it refuses on mismatch before writing, refuses
`stockgrader` by name with no override, and confirms the rows after commit.

### 2.4 Apply the migrations

Proxy to the **direct** endpoint, not the pooler — the runner takes
`pg_advisory_xact_lock` and owns each migration's transaction, and those
semantics are not reliable through a transaction-mode pooler (closeout §1.6):

```
fly mpg proxy stockgrader-db-r2
```

Then, in a second shell, with the password read interactively so it never
appears in a pasted line or in shell history:

```
$s = Read-Host -AsSecureString "password"
$env:PGPASSWORD = [Runtime.InteropServices.Marshal]::PtrToStringAuto([Runtime.InteropServices.Marshal]::SecureStringToBSTR($s))
.venv\Scripts\python.exe db\migrate.py plan  --dsn "host=127.0.0.1 port=16380 user=fly-user dbname=stockgrader_scratch"
.venv\Scripts\python.exe db\migrate.py apply --dsn "host=127.0.0.1 port=16380 user=fly-user dbname=stockgrader_scratch"
```

**The DSN is in keyword form and carries no secret**, so the runner's full output
is safe to paste back. That is the shape D-030 requires and the shape F-021
violated.

### 2.5 Re-load the quarter

```
$env:DATABASE_URL = "host=127.0.0.1 port=16380 user=fly-user dbname=stockgrader_scratch"
.venv\Scripts\python.exe tools\load_quarter.py --quarter 2026q2 --archive "<ARCHIVE_DIR>\2026q2.zip" --submissions --dry-run
```

`--quarter` and `--archive` are both **required**, and the DSN comes from
`DATABASE_URL` in the environment - the loader takes no `--dsn`. Run `--dry-run`
first: it parses the whole archive and rolls back, proving the parse against
this cluster's schema without writing.

Expect **~148 s** and **3,368,813 facts** (F-034). **State that expectation
before running it** — a count with no prior expectation returns a number that
looks like an answer and nothing disputes it.

### 2.6 Verify before repointing anything

```sql
SELECT * FROM coverage_window;
SELECT count(*) FROM fact;
```

**The new cluster must match the old on all of it:** `2026q2..2026q2`, one
quarter, **3,368,813** facts, 195 quarantined, 7,714 filings, 6,179 filers.
**A mismatch stops the sequence.** This is the verification the old cluster
passed, and it is the old cluster's stated end condition.

### 2.7 Repoint the app

**`fly secrets import` from stdin - NOT `fly secrets set`.** The phase-0
handover puts `fly secrets set KEY=value` on the must-not-run list because **it
puts the value in shell history**, which is a copy that survives closing the
window. This runbook said `set` in its first issue; that was wrong and it is
F-043. **Note the interaction with
OPEN-63:** `stockgrader_app`'s password rotation is already deferred and its
credential is already compromised. **A new cluster means a new
`stockgrader_app` anyway — so OPEN-63 closes for free here**, and deferring it
past this point means deliberately carrying a compromised credential onto a
clean cluster.

The restore drill found the cutover **will not overwrite an existing connection
string** — check the result rather than assuming the set took.

## 3. What does NOT happen at the end

**The old cluster is not destroyed in this sitting.** Standing constraint: no
cluster is destroyed; anything built is named and recorded with a stated end
condition.

- **End condition, stated:** retained until §2.6 passes on the new cluster, then
  destroyed in a sitting somebody sees through to completion (B-9).
- **Two Basic clusters running costs two plan fees.** F-next/orphaned-restore-
  clusters-already-exist records two PharmFoldMDK clusters nobody destroyed, and
  the finding's point was that **the plan fee, not storage, is what makes a
  forgotten cluster expensive.** This one has a name and an end condition so it
  does not join them.

## 4. What the Builder needs back, and it is not much

**Two non-secret strings, typed rather than pasted:** the new cluster's **id**
and **name**, so `fly.toml`, the register and D-039 can be updated to name the
cluster the project actually runs on.

**Nothing else.** Not a DSN, not a password, not the block `create` printed.

## 5. The honest column

**None of this has been executed and I cannot execute it.** The sequence is
assembled from the register — OPEN-56's CLI inventory, F-014's amendment, F-034's
load timing, the closeout's proxy and pooler notes — and **every step is
therefore a claim about commands I have read about rather than run.** The
register has already recorded one cutover procedure that only worked on an app
which had never been connected to a database, so **a runbook written from
documents is exactly the artifact that has failed here before.**

**Expect §2.3 to be the rough one.** It is the step with the least written down:
the current `stockgrader_schema_admin` was created interactively across a
back-and-forth, and what this runbook says about it is the shortest section for
the worst reason.
