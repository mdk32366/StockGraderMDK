# REPORT — Code → Planner — the 150 GB cluster is built and verified

**From:** Code (Builder) · **Date:** 2026-09-25
**Executes:** D-039. **Owner at the keyboard throughout; the Builder ran nothing
against the cluster.**

| | |
|---|---|
| Cluster | `w8675081kdjr3pk4` / `stockgrader-db-r2`, `sjc`, basic, **150 GB** |
| Server | **PostgreSQL 16.15** — identical major/minor to r1 |
| Databases | `fly-db`, `stockgrader`, `stockgrader_scratch` |
| Migrations | 0001–0004 applied **and verified** |
| Data | **3,368,813 facts**, 195 quarantined, 7,714 filings, 6,179 filers |
| Verification | **9/9 assertions match r1** |

---

## 1. What was done

Eleven commands, one at a time, each confirmed before the next.

1. **Preflight** — `fly mpg list`. Expected one cluster, **found four**. See §3.
2. **Create** — 150 GB, create-time, since `fly mpg` cannot resize (OPEN-56).
3. **Databases** — `stockgrader_scratch` **and** `stockgrader`, then verified by
   listing rather than by assuming the create returned cleanly (phase-0 §5.3).
4. **Proxy** — `127.0.0.1:16380 -> direct.w8675081kdjr3pk4.flympg.net:5432`.
   **Direct, not pgbouncer**, which is what the runner needs.
5. **Canary** — scratch only, via the new `tools/apply_canary.py`.
6. **Migrations** — `plan` then `apply`. Four applied, four verified.
7. **Load** — `--dry-run` first, then committed.
8. **Verify** — `tools/verify_cluster.py`, 9/9.

## 2. Three things established that were open questions going in

**`fly-user` already resolves to `schema_admin`.** Connecting as `user=fly-user`
reports `current_user = schema_admin`. The migrations' headers say **`RUN AS: a
schema_admin`**, so they ran as the role they were written for. The concern that
we were running them under an unproven role was unfounded, and no separate
migration account was needed for this operation.

**r2 is PostgreSQL 16.15, the same as r1.** F-027 recorded a two-major gap
between the local 18.3 and the cluster, with the warning that identical results
across them were *"a result, not a guarantee for future work."* That risk does
not apply here — there is no gap.

**`btree_gist` created without incident.** 0001 line 27 needs it for the
`filer_ticker_no_overlap` GiST exclusion constraint, and `CREATE EXTENSION` is
more privileged than `CREATE TABLE`. Flagged in advance as the likeliest failure
point; it was not one.

## 3. The preflight found four clusters, not one

| ID | Name | Status |
|---|---|---|
| `kzpwm0j1dm204nv3` | stockgrader-db-r1 | ours, live, **15 GB** |
| `d1zj5omk443ryqkv` | stockgrader-db | ours, superseded 2026-09-23 |
| `kyzl60xz9zyrpj9g` | sentinel… restored ×2 | **not ours** |
| `zp2wjrej9lwodn4q` | sentinel… restored | **not ours** |

**Neither sentinel cluster was touched, and the register is the reason.**
`F-next/orphaned-restore-clusters-already-exist` was **corrected** on 2026-09-25:
the evidence established only that they exist, `ATTACHED APPS` records what has
ever been attached rather than what is in use, and one of them may be Sentinel's
production database. Its operational line — *a cost argument ending in "destroy
the three idle clusters" is one action away from deleting a live production
database on the strength of a name in a listing* — is why they are still there.

**`d1zj5omk443ryqkv` cannot be retired before 2026-10-03.** OPEN-7 requires
`fly mpg backup list d1zj5omk443ryqkv --all` on that date to settle whether a
full backup's children expire with it. **Destroying it destroys the test**, and
that test is the evidence behind the stated recovery horizon.

**So there are now five clusters and five plan fees**, and the register's own
note is that the plan fee, not storage, is what makes a forgotten cluster
expensive. r1 and r2 both have stated end conditions. Neither sentinel cluster
is ours to give one.

## 4. Why this was done now and not later

The store held **one quarter, ~1.8 GB**. The FSDS archives are immutable and
were still cached on disk — `2026q2.zip`, 60,419,016 bytes, **sha256 matching the
closeout's recorded value** — so r2 was filled by **re-running the loader**, not
by moving bytes.

**After the 45-quarter load this becomes a ~114 GB migration.** The ordering was
the whole argument: **new cluster first, load second.**

## 5. New tools, and why each is a tool rather than an instruction

| | |
|---|---|
| `tools/apply_canary.py` | Phase-0 §5.4 says to *assert which database you are connected to* before marking it disposable, because *"a proxy connected to the wrong database looks exactly like a proxy connected to the right one."* An instruction to eyeball a value is a check that fails silently. This refuses on mismatch before writing, refuses `stockgrader` by name with **no override**, and confirms rows after commit. |
| `tools/verify_cluster.py` | *A count with no prior expectation returns a number that looks like an answer and nothing disputes it.* Expectations are arguments, defaulted to r1's measured state; a mismatch is a non-zero exit, not a line read past at the end of a long session. |
| `tools/load_progress.py` | `pg_locks`, not `pg_stat_activity` — `schema_admin` gets `<insufficient privilege>` from the latter. Deliberately reports **no row count**: `pg_stat_database` does not flush mid-transaction and F-032 is the finding where exactly that misled someone. |

## 6. The repoint — DONE

**The app points at r2 and is serving.**

| step | outcome |
|---|---|
| `stockgrader_app` at `writer` | created by owner; password set in the dashboard |
| A-017 re-proven on r2 | **6/6** via `tools/verify_writer.py` |
| `DATABASE_URL` | imported from stdin, digest `fd2725dd59203146` (was `4d80594c9b6ff503`), **Deployed** |
| Deploy | rolling, both machines updated |
| `/healthz` | `{"status":"ok","build":"0e9c771..."}` |

**A-017 holds on r2, proven rather than asserted:** `stockgrader_app` reads
3,368,813 facts, performs INSERT/UPDATE/DELETE, and is refused `CREATE TABLE`
with *permission denied for schema public* — the ceiling exactly where D-031
wants it. **My prediction that it would lack GRANTs on another role's tables was
wrong**: Fly's `writer` is grant-bearing by construction and no GRANT step was
needed.

**F-015 did not bite.** The deploy half happened — rolling update, both machines,
digest changed and reported Deployed. That is the step the register records as
the one that silently does not happen, and this time it did.

**OPEN-63 is closed by this.** Its subject is *the credential the deployed
application uses*, and the deployed application now uses a new account on a new
cluster. **Residual, stated rather than implied:** the compromised
`stockgrader_app` on **r1** still exists and still works against r1, and will
until r1 is destroyed. Nothing points at it.

## 6a. What is NOT done

**r1 is still running, deliberately, and its end condition is now met** — D-039 required it retained until the new
cluster passed the same verification, and r2 has (9/9). **It is not destroyed:**
standing constraint, and B-9 says the destroy happens in a sitting somebody sees
through. Recommend leaving it several days against r2 proving itself.

**`d1zj5omk443ryqkv` must survive to 2026-10-03** regardless — OPEN-7's
backup-expiry test runs against it that day.

**`fly-user` on r2 is compromised from creation** (F-014, third occurrence — see
F-044). The owner has ruled it acceptable and will cycle at the end. It is the
account these migrations ran under.

## 7. The honest column

**The runbook I wrote for this had four defects and one omission**, all found by
walking it, all recoverable from the register, none found by re-reading it before
writing. **F-043.** Its own §5 predicted exactly that and even named the section
that would be weakest. The prediction was the most accurate part of the document
and the only part nobody could act on.

**The 148-second expectation I quoted was a local figure.** F-034 measured *"three
loads against a local cluster"*, and I carried the number across to a remote
cluster over a proxy without carrying its conditions — the same shape as F-040,
during the operation where I had just been told to stop doing it. The load took
substantially longer, which was correct behaviour and a wrong expectation.
