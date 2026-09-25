# HANDOVER — Planner → Code — StockGraderMDK: Phase 0 steps 5–6, A-017, D-031

**From:** Planner · **Date:** 2026-09-23
**Predecessor:** `HANDOVER-Planner-2026-09-22-StockGraderMDK-phase0-cluster.md`
**Status:** Phase 0 steps 1–4 done. This document covers steps 5–6, the A-017
test, and Code's half of D-031.

---

## 0. Standing rules for this block

**Cluster:** `d1zj5omk443ryqkv` (`stockgrader-db`, `sjc`).
**Databases:** `stockgrader` (real), `stockgrader_scratch` (you create it).

**You will not be given any credential, and you will not create one that lives.**
Use `fly mpg proxy` and a non-interactive client. Do not use `fly mpg connect` —
it opens an interactive psql session and you will handle it badly.

**Commands you must NOT run in this block:**

- `fly mpg attach` — named F-014 offender. Prints the live connection string in
  normal successful output. Owner runs it.
- `fly mpg create` — same, if a cluster is ever made.
- `fly secrets set KEY=value` — puts the value in shell history. Owner uses
  `fly secrets import` from stdin.

**Owner-at-the-keyboard protocol.** For anything on the forbidden list, or
anything else you judge the owner must run himself, do not batch it and do not
write a script. Hand him **one command at a time**, wait for the output, confirm
it did what it was supposed to do, then hand him the next. If a command in that
sequence fails or returns something unexpected, stop the sequence and report —
do not continue to the next command on the assumption that the previous one took.

**If a credential appears in your output anyway:** stop, record that it happened
and which command did it, and do not reproduce the value in your report. Treat
that credential as compromised and say so. This is how F-014 happened; the
mitigation is mechanical, not attentional.

**Do not, in this block:** run the canary against `stockgrader`, run migrations,
or load any ticker data. The first real data load is gated on D-029.

**Suspected new offender — establish this before you rely on it.**
`fly mpg users create` has not been run on this project. It almost certainly
prints a password, because it has to hand you one somehow. Check
`fly mpg users create --help` first and treat the output as hostile. Whatever it
does, record it — that is finding **F-018**, number subject to the owner's log.

---

## 1. Step 5 — the scratch database

**5.1 Environment.** `flyctl version`, `fly auth whoami`, `fly mpg list`.
Confirm the cluster is visible and you are authenticated. Stop and report if not.

**5.2 Syntax first.** `fly mpg databases --help`. We have not seen the create
syntax. Do not guess it. If the help output is ambiguous, stop and report rather
than trying variants against a live cluster.

**5.3 Create.** Create `stockgrader_scratch` on `d1zj5omk443ryqkv`. Verify it
exists by listing, not by assuming the create succeeded.

**5.4 Canary — scratch only.** Open `fly mpg proxy` in the background, connect
to `stockgrader_scratch`, and run `db/keel_canary.sql`.

Before you execute it: echo the database name you are actually connected to and
assert it is `stockgrader_scratch`. Running the canary against `stockgrader` is
one of the two deliberate acts that would defeat the guard, and a proxy
connected to the wrong database looks exactly like a proxy connected to the right
one.

Confirm the canary rows are present afterwards.

---

## 2. A-017 — a `writer` can do everything the application needs

**Carve-out, PROPOSED, number to be assigned in PR-5.** You will need a
`writer`-role user to run this test, and creating one may expose its password
per F-018. Create a disposable account for the test — suggested name
`sg_a017_test` — use it against `stockgrader_scratch` only, and drop it at the
end of this step. The exposure is bounded, scratch-only and deliberate, and it
is recorded here rather than discovered later. This does **not** authorise
creating the live `writer` account; that is the owner's, in §4.

**Test it can do what the app needs.** Against scratch, as `sg_a017_test`:
SELECT, INSERT, UPDATE, DELETE on ordinary tables.

**Test it cannot do what the app must not.** CREATE TABLE, ALTER TABLE, DROP
TABLE. Capture the exact error text — the refusal is the evidence, and the
wording tells us whether the ceiling is the role or something else.

**Falsification conditions, from the predecessor:** A-017 is falsified if the app
cannot run its queries, or if the migration runner turns out to need the app's
credential. Under D-021 migrations run from the Builder, so the second should
not bite — but say so explicitly if it does, because D-031 changes shape if
A-017 fails.

**Then drop `sg_a017_test`.** Confirm the drop.

---

## 3. Step 6 — close OPEN-1

**6.1 Prove the probe is read-only before pointing it at the real database.**
Read `postgres_probe`'s source and state the evidence — what it executes, what
it would do on a write path, whether there is one. The owner said this would be
confirmed first; asserting it is not confirming it.

**6.2 Against `stockgrader_scratch`:** expect canary present, small →
**accepted**.

**6.3 Against `stockgrader`:** expect no canary → **refused**.

Capture both outputs verbatim. The refusal against a database that now actually
matters is the finding. Until it exists the guard has only ever been proven
against fakes, and OPEN-1 stays open.

---

## 4. Stop here and report

Steps 5, A-017 and 6 are your block. When they are done, stop.

---

## 5. Credential work — DEFERRED by owner ruling, 2026-09-23

The owner has deferred the D-029 / D-031 credential work past today's ticker
load. Recorded here rather than left implicit, because a deferral nobody wrote
down is indistinguishable from an oversight.

**What this means for you:**

- Do **not** create the live `writer` account, and do not run `fly mpg attach`.
  D-031's replacement is not happening in this block.
- The application continues to connect as the exposed `stockgradermdk` account
  at `schema_admin` — F-017's over-privilege and F-014's exposure, both still
  live, both known.
- Run A-017 anyway, as specified in §2. The point of testing it now is that when
  the replacement does happen it is a known-good path rather than a discovery.
- Do not drop the `stockgradermdk` account. It is the account the app is using.

**Standing verification, unchanged.** When the replacement eventually happens,
`fly secrets list` reading **Deployed** is necessary and not sufficient. F-015 is
the scar: a secret that reads Deployed proves the platform's state, not the
running machine's behaviour. Only a request to the live service that answers from
the database closes D-029.

**Tripwire.** The deferral holds only while everything in `stockgrader` can be
rebuilt from source. The first write that cannot — anything user-owned, anything
whose loss is not fixed by re-running the loader — ends it. Flag it if you see
the schema heading that way.

---

## 6. What to return

1. Every command run, in order, with its outcome. Not commands that look right —
   commands that were executed and whose output you saw.
2. Verbatim outputs for: `fly mpg databases --help`, the canary verification,
   the A-017 permit and refusal results with exact error text, and both
   `postgres_probe` runs.
3. A findings block ready for PR-5: **F-018** (`fly mpg users create` behaviour —
   does it print a credential), **F-019** (A-017 result: held or falsified, with
   the evidence), and the OPEN-1 closure evidence.
4. Anything that surprised you. Two of the four findings in the predecessor came
   from noticing that a normal, successful command had done something other than
   what it appeared to do.

---

## 7. What is still true and not covered by this block

The backup `20260922-192041F` covers `stockgrader` as of 2026-09-22T19:20:41Z.
It does not cover `stockgrader_scratch`, which you are about to create, and it is
not meant to — the canary marks that database disposable.

The gate still cannot see a staged secret. That remains an open testplan item,
not a guard, until a DB-backed endpoint exists.
