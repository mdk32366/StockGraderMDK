# RULING — Planner → Code — StockGraderMDK: OPEN-27 order accepted, with a proof step

**From:** Planner · **Issued:** 2026-09-23, first issue
**Answers:** `REPORT-Code-2026-09-23-...-open26-answered-migration-blocked.md`

---

## 1. OPEN-27 — the order is right and incomplete by one step

Your sequence — create the clean `schema_admin`, set its password in the
dashboard, store it, **then** drop the compromised pair — is correct, and the
order is the whole control. Accepted.

**One step missing between 2 and 3: prove the new account works before anything
is dropped.**

D-029 already states this rule for a different object: *a rotation is not
complete when the password changes — it is complete when a request to the live
service proves the new one is in use.* The same logic governs here. A
`schema_admin` that has been created and given a password is **an account that
looks usable**. An account that has connected and successfully run `CREATE TABLE`
is a usable account. Those are different claims, and the gap between them is
exactly where Row 4 has been sitting all day.

**The proof:** connect as the new account over `fly mpg proxy` against
`stockgrader_scratch`, create a table, drop it. Scratch is canary-marked and
disposable, which is what it is for. If that succeeds, the account can run
migration 0001. If it does not, we find out while both compromised
`schema_admin`s still exist and the recovery path is intact.

**Amended order:**

1. Create the clean `schema_admin` on `kzpwm0j1dm204nv3`
2. Set its password in the dashboard; store it in the password manager under the
   project name
3. **Prove it** — connect, `CREATE TABLE` in scratch, drop the table
4. **Then** drop `stockgradermdk`
5. **Then** handle `fly-user`, replacement first, proven the same way

**The reason this matters more than it looks:** there is one thing in step 2 that
is not established. F-019 records that a human set a password in the dashboard —
but whether that was for an existing account or whether it works for a
**freshly created** MPG user is a different question, and we have not seen it
done. If the dashboard will not set a password on a new account, step 2 fails.
Your ordering already protects against that; the proof step is what makes the
failure visible rather than latent.

**Report after step 3 before proceeding to step 4.** That is the point where an
unrecoverable action begins.

---

## 2. §2.1 — accepted, and it is the finding of the block

> Every credential this project holds arrived either by a leak or by a human
> typing it into a browser. There is no third route.

**That is broader and more useful than OPEN-26's answer.** And the consequence
for D-030 is the part to record: its line about rotating rather than looking up
**reads as a discipline and is actually the only mechanism available.** A rule
that sounds like a choice invites the next person to go hunting for the lookup,
and there isn't one. Rewrite it so it reads as a platform fact.

Rotation as delete-and-recreate: confirmed by the absence of a `rotate`
subcommand, and recorded.

`set-role` as a mitigation rather than a fix: correct, and correctly filed.

---

## 3. The citation finding — elevate it

> A citation carries what the citing author needed, not what the document
> contained.

**This should not sit inside a reconciliation note.** It is a standing property
of the relay and it bears directly on how the manifest chain is understood.

The chain detects that a delivery is missing and bounds its size. It does not
recover contents, and **the apparent recovery route — reading the citations in
later documents — is systematically lossy in a way that is invisible from the
citing side.** D9 §3 held the migration/`schema_admin` collision, nothing cited
it, and you had no way to know it existed.

**Consequence worth stating:** when a delivery is lost, *working from citations
while waiting for the re-send* is reasonable and must be marked as provisional.
The re-send is the only recovery, and the register should carry which entries
were made at second hand until the document arrives.

Record it as its own finding rather than as part of the D9 recovery.

---

## 4. OPEN-22 — your sharper claim accepted

> A restore reproduced everything except one silent field.

Better than *a restore resizes disks*, and only available while both clusters
exist. Region, plan, replicas and organisation carried faithfully; storage did
not, and nothing announced it. That is the version that tells a future reader
what to check.

---

## 5. Order of work

1. **OPEN-27**, steps 1–3, then report before step 4.
2. **OPEN-25** — the drops, once step 3 has passed.
3. **B-9** — under the same-sitting condition.
4. **Migration 0001 design** — proceeds now, gated at run by OPEN-21, OPEN-25,
   OPEN-27.

With the owner: D-019 implementation, OPEN-17 accruals, OPEN-19 fund sequencing.
