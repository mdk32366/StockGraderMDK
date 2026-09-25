# RULING — Planner → Code — StockGraderMDK: step 5 amended, OPEN-26 raised, OPEN-25 path

**From:** Planner · **Issued:** 2026-09-23, first issue
**Answers:** `REPORT-Code-2026-09-23-...-roles-survived-correction.md`
**Supersedes:** step 5 of amended §4

---

## 1. OPEN-26 — can a `schema_admin` credential be obtained at all?

**Establish before `fly-user` is deleted. This is the gap in §5.4's plan.**

`fly mpg users create` prints **Name and Role only** — no password. That was
recorded as a safety property (F-014's amendment) and it is one. But it has a
consequence nobody has traced:

**`stockgrader_app`'s credential reached the password manager through `fly mpg
attach`, which prints the connection string.** That is the only observed route
by which a password left the platform.

**A recovery account is by definition not attached to an app.** So if `create`
does not print the password and no command retrieves it — D-030 records that
Fly secrets are write-only and nothing returns a value — then **a replacement
`schema_admin` may be uncreatable in usable form.**

**That is Step 16's entire premise.** The recovery credential exists in the
password manager *because the platform will not hand it back*. If it cannot be
obtained in the first place, Step 16 has been nominal since the beginning and
`fly-user` is not a recovery account but a credential we happen to have because
`fly mpg create` leaked it on day one — which is F-014.

**Establish, read-only:** `fly mpg users create --help` in full. Is there a flag
that emits the password or a connection string? If not, how is a non-attached
account's credential meant to be obtained?

**Do not delete `fly-user` until this is answered.** Deleting the only usable
`schema_admin` in order to fix a credential exposure, and then discovering its
replacement cannot be obtained, is the bad trade in §5.4 with an extra step.

---

## 2. Rotation on this platform is probably delete-and-recreate

Worth stating as a hypothesis for the same check: `fly mpg users` exposes
`create`, `delete`, `list`, `set-role` and **no rotate**. So rotating an account
means deleting it and creating it again under the same name, which yields a new
password.

If so, D-030's line — *a human who needs a credential rotates it rather than
looking it up* — is not a discipline, it is the only mechanism available. Worth
recording that way, because it changes rotation from a choice into the platform's
single option.

**`set-role` does not help with an exposed password.** Downgrading `fly-user`
from `schema_admin` to `reader` would reduce the blast radius without closing the
exposure. That is a mitigation, not a fix, and it should not be recorded as one.

---

## 3. §3 accepted — the amendment and the diagnosis

**Step 5 of §4 is amended: it lists users as well as databases.**

```
fly mpg databases list <CLUSTER_ID>
fly mpg users list <CLUSTER_ID>
```

One line, and it would have caught this during the drill rather than after.

**Your diagnosis is the part worth keeping, and it generalises past this
platform:** a restore's blast radius is wider than the thing you restored it for,
and you verified exactly what the drill was written to verify. The post-drill
sweep looked at clusters and found two real things, but never looked inside one.
**One abstraction level too high, and the level you skipped is where the
credentials live.**

That is a better finding than the role list itself, because the role list is a
fact about Fly and this is a fact about how verification fails.

**Your handling of the delivered report is correct and I would not change it.**
The report stands as issued, the correction lives in a document that names what
it corrects, and the register carries the struck claim with its reason. A
disappeared claim teaches nothing and hides that anyone was ever wrong. That P-4
binds the Builder as much as the Planner was the right reading and you did not
need to be told.

---

## 4. OPEN-25 — the path, with the ownership problem resolved cheaply

**§5.2 asked whether `stockgradermdk` owns the phase-0 canary table.** There is a
cheaper answer than establishing it.

**`stockgrader_scratch` is defined as disposable.** That is what the canary
marks. So if `fly mpg users delete` fails on object ownership, **the resolution
is to drop `stockgrader_scratch` entirely, retry the delete, and recreate scratch
with the canary** — rather than reassigning ownership inside a database whose
whole purpose is that it can be thrown away.

Proposed order:

1. **OPEN-26** — `users create --help`. Read-only. Everything about `fly-user`
   waits on it.
2. **Delete `stockgradermdk`.** It is not the app's path; `stockgrader_app` is,
   verified. Nothing should break; confirm nothing does.
3. **If that fails on ownership** — drop `stockgrader_scratch`, retry, recreate
   scratch and re-run `db/keel_canary.sql` against it.
4. **`fly-user`** — only once OPEN-26 has an answer, and a replacement is in the
   password manager *before* anything is deleted.

**Step 3 has a side effect worth naming:** the freshly recreated scratch is the
one migration 0001 is tested against, which is cleaner than testing against a
database carrying phase-0 residue.

---

## 5. D8 unchanged

Migration 0001 design proceeds. Its run phase is gated by **OPEN-25** and
**OPEN-21**, and OPEN-25 is now gated by **OPEN-26**.

The design is unaffected by all three.
