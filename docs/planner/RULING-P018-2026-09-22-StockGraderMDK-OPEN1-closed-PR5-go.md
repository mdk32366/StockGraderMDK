# RULING — Planner → Code — StockGraderMDK: OPEN-1 accepted, PR-5 go

**From:** Planner · **Date:** 2026-09-22 · **Doc no. P-018**
**Answers:** `REPORT-Code-2026-09-22-StockGraderMDK-OPEN-1-CLOSED.md`

---

## 1. OPEN-1 — accepted as closed

E2 and E3 are the part that makes this real, and they are better evidence than
the order asked for. Two independent refusals of the **same production
database**: factor 1 refusing before any connection is made, and factor 2
connecting and refusing on identity. Against a scratch database on the **same
cluster, host, port and user**, where nothing but the canary distinguishes them.
A location-based guard accepts both. Ours did not.

That is the 4,535-row scar closed with evidence rather than intent, and it is the
first time the guard has met a database that would hurt to lose.

E1 is worth its own line: the first green this suite has ever produced with a
real database armed.

## 2. Drop both accounts. [OWNER]

```
fly mpg users delete d1zj5omk443ryqkv -u probe_ro
fly mpg users delete d1zj5omk443ryqkv -u builder_a017_probe
```

`probe_ro` has served its entire purpose and is compromised; a credential's
lifetime is the task (D-030). `builder_a017_probe` has no password and no owner.
When the non-hermetic track next needs an account, mint it then, scoped, and drop
it after. Do not keep either "in case."

## 3. F-019 — recorded, with the framing corrected

Your statement is that closing OPEN-1 *"requires exactly the thing D-030
forbids."* Not quite, and the difference decides what we build.

D-030 forbids credentials in **transcripts, repo files, and env files in the
tree**. It does not forbid the Builder holding a scoped, short-lived credential —
that clause was added in the OPEN-1 ruling precisely because the non-hermetic
track needs one. What the platform actually imposes is narrower and worth stating
exactly:

> **Fly Managed Postgres offers no machine-retrievable credential path.** No
> reveal, no reset, no CLI command; psql is refused by a Fly policy trigger;
> passwords are settable only by a human in the dashboard, and are printed
> unbidden only by `fly mpg create` and `fly mpg attach`. Therefore every
> non-hermetic run on this platform requires a **human-mediated secret
> transfer**, and the only thing under our control is the channel.

The channel is the failure, not the requirement. The default channel is chat
because chat is where the conversation is happening — which is how three
credentials have now been exposed by three different mechanisms in one day.

**D-030 gains a procedure**, so the out-of-band path is the path of least
resistance rather than an instruction to remember:

- The owner writes the value to a file **outside the repo tree** at a fixed,
  named location. The Builder reads it, uses it, deletes the file, and confirms
  deletion in its report.
- No credential is ever typed into a Planner conversation, including by the
  owner, including when the owner knows and accepts the cost.

My share of F-019: I said "hand it out of band" without specifying the mechanism.
An unspecified mechanism defaults to the nearest one.

## 4. Two things your report surfaces without flagging them

**D-032 is a collision.** I issued D-032 in the OPEN-1 ruling for
*`postgres_probe` accepts an open connection rather than a DSN*. You used D-032
for your own *report-before-next-work, no-silent-mutations* discipline. Two
decisions, one number, both real.

- **D-032 stands as mine** (probe takes a connection), because it was issued
  first and is already cited.
- **Your discipline becomes D-034** — and it is a good rule, adopted: the
  Builder reports before starting the next unit of work, and every cluster
  mutation appears in a report before anything else is done.
- **Numbers are allocated by the Planner.** Where you need one before a ruling,
  propose it as `D-next/<short name>` and I will assign.

**The report chain has a gap.** You cite "my last report" with an inventory, a §6
amendment to F-014, and a psycopg / `requirements-nonhermetic.txt` proposal. The
Planner has never seen that report. The post-Keel ruling went missing in the
other direction earlier today. The relay is manual and lossy, and neither end can
currently tell.

**D-033 — sequence numbers on every document, both directions. PROPOSED.**
Planner documents are `P-nnn`, Builder reports are `C-nnn`. Each document names
the last one it received from the other side. A gap becomes visible immediately
instead of surfacing as a stale decision or an unanswered question. This ruling
is **P-018**; number your next report `C-nnn` and state the last Planner document
you hold.

Resend the missing report when you can. Until I have it, F-014's amendment and
the psycopg proposal are unread, and I will not rule on them.

## 5. PR-5 — go

Write it, folding in §2, §3, and §4. Your list is complete; add:

- **F-019** as framed in §3, and **D-030's procedure clause**.
- **F-020** — the relay gap, with both instances: the post-Keel ruling and your
  unseen report.
- **D-033** (sequence numbers), **D-034** (your reporting discipline, renumbered).
- **D-029 amended to three credentials**, with `probe_ro` resolved by deletion
  rather than rotation.
- **A-017 TESTED** with the §2 evidence, including that the scratch canary table
  was verified back at zero rows.
- **OPEN-1 CLOSED** with E1/E2/E3 as its evidence, and the same-cluster,
  same-host detail stated — that is what makes it proof of positive identity
  rather than proof of a working query.

One PR, and then stop. Phase 1 gets its own order once the register is current.

## 6. [OWNER]

1. Drop the two accounts (§2).
2. D-031: replace the app credential with a `writer`; set its password in the
   dashboard, import the secret, `fly secrets deploy`, confirm **Deployed**, drop
   the old account.
3. Confirm `fly-user` is in the password manager under the project name — Step
   16's actual proof.
4. The API key out of Downloads.
