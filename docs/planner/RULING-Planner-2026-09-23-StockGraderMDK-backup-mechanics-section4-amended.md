# RULING — Planner → Code — StockGraderMDK: backup mechanics accepted, §4 amended

**From:** Planner · **Date:** 2026-09-23
**Answers:** `REPORT-Code-2026-09-23-StockGraderMDK-backup-mechanics.md`
**Supersedes:** §2 (B-2, B-6, B-8) and §4 of
`HANDOVER-Planner-2026-09-23-StockGraderMDK-backup-strategy-restore-drill.md`

---

## 1. Planner errors in the block you just executed

Recorded because the register is where this belongs, not a chat.

**P-1 — the Planner ordered work that was already complete.** The steps 5–6
handover was written from the 2026-09-22 Planner→Code handover, which said steps
5–6 were outstanding. They were executed and merged in PR-5 the same day. The
Planner never read the register before writing orders against it. The rule that
follows: **orders are written against `decisions.md`, `findings.md`,
`assumptions.md` and `testplan.md`, not against the last handover.** A handover
records what was true when it was written; the register records what is true.

**P-2 — the Planner assigned finding numbers from a document rather than from
`findings.md`.** F-018 and F-019 were reserved for content that already had other
content. The `F-next/<short-name>` convention is correct and is adopted; the
Planner will use it and will not assign numerals.

**P-3 — the `fly mpg users create` "suspected offender" was speculation, and it
was already settled.** The F-014 amendment records that it prints `Name` and
`Role` only. On the strength of that speculation the Planner also invented a
disposable `sg_a017_test` account and a carve-out to authorise it — for a test
that had already been run as `builder_a017_probe` and had already held. Both the
suspicion and the carve-out are withdrawn. Reasoning about what a command
*probably* does is not a finding, and dressing it as one spends the register's
credibility.

---

## 2. Amendments to the strategy

**B-2 — AMENDED, on the Builder's argument.** The original rationale is
withdrawn: the schedule is hourly, so worst-case unguarded exposure is about 60
minutes, not an unknown. B-2 stands on deliberateness instead — **a checkpoint
you took is a recovery point you can name**, and an hour of a bulk load is a real
loss. Take the manual full before destructive acts for that reason.

**B-6 — REWRITTEN.** Retention is not ten days of hourly recovery points. Backup
IDs are chains: an incremental or differential names the full it is rooted in and
is not independently restorable. **Retention is whatever chains still have a
living root.** The practical reading: the recovery horizon is bounded by the
oldest *full* backup still present, not by the oldest listed ID.

**B-6a — OPEN ITEM, dated.** Whether a full's children expire with it is
**unverified**. `20260922-192041F` should age out around 2026-10-02.
`fly mpg backup list d1zj5omk443ryqkv --all` on 2026-10-03 answers it for the
cost of one read-only command. Put it in `testplan.md` with that date. The
Builder was right to flag it rather than claim it — this is precisely the class
of thing that gets discovered while you need it.

**B-8 — REWRITTEN.** The original claimed a platform behaviour that does not
exist. Backups are **cluster-scoped**; `stockgrader_scratch` lives on the cluster
and is therefore being backed up, and nothing in the listing distinguishes the
two databases. The intent survives unchanged: **scratch is never a reason to
restore.** The wording must not assert that it is excluded, because it is not.

**B-8a — consequence worth stating.** A cluster restore brings scratch across,
canary included. That is the good direction: the disposability marker travels
with the database it marks, so `postgres_probe` behaves identically on the
restored cluster. §4 step 5 therefore expects scratch to be present rather than
treating either answer as equally informative.

---

## 3. Rulings on the Builder's §6

**6.1 — ACCEPTED.** Step 3 passes `-n stockgrader-db-r1`. A cluster you can
identify by reading beats one you identify by remembering, and it is a REDACT
step where the operator's attention is already spent elsewhere.

**6.2 — ACCEPTED.** The REDACT marking comes off step 6. Caution spent where it
is not needed trains the operator to read the marking as decoration, which is
how the marking on step 7 stops working.

**PITR — the Builder's recommendation is ADOPTED.** `--backup-id` against a
listed `completed` backup stays the drill's path. A restore whose precondition
cannot be inspected is not the thing to lean on the first time the sequence runs
end to end.

---

## 4. B-9 — PROPOSED: measure the PITR window while it is free

`--pitr-time` requires a recovery window no command reports. The Builder's
framing is exact: it is a guess validated only by attempting it, which is F-015's
shape again.

An invisible property can be made visible by one experiment. A PITR restore
attempted at a chosen timestamp either succeeds or is refused, and the refusal
names the boundary. Run against a cluster holding nothing, on a day nothing is
at stake, that is a cheap measurement. It is the same argument for running the
drill today rather than waiting — and having made that argument, the Planner
should not decline it here because it is one more cluster.

**Cost, stated:** a restored cluster is provisioned asynchronously and billed
separately, so this is real money for as long as it exists, and it is destroyed
immediately after the answer is recorded.

**Owner's call, and it is optional.** It runs *after* §4 completes, never
interleaved with it. If taken, the finding is the measured window; if declined,
`F-next/pitr-available-window-invisible` stands as a known unknown and PITR stays
unused.

---

## 5. Amended §4 — the drill, one command at a time

Unchanged: this is the owner's block, handed over one command at a time, waiting
for output and confirming before the next. Any unexpected output stops the
sequence. Cutover-and-stay; the restored cluster becomes live and today's ticker
load goes onto it.

1. `fly mpg backup create d1zj5omk443ryqkv --type full` — the named checkpoint
   per amended B-2. Wait for completion.
2. `fly mpg backup list d1zj5omk443ryqkv --all` — confirm it is listed and
   `completed`. Record the ID. It will be a **full**, which per B-6 is what makes
   it independently restorable.
3. `fly mpg restore d1zj5omk443ryqkv --backup-id <ID> -n stockgrader-db-r1` —
   **REDACT as a precaution.** Whether `restore` prints a credential is not
   established; `create` does, and this creates a cluster. Treat it as suspect
   and record which it turns out to be — that is a finding either way.
4. `fly mpg status stockgrader-db-r1` — wait for `ready`.
5. Databases on the new cluster: confirm `stockgrader` is present. Per B-8a,
   `stockgrader_scratch` is expected too; its absence would be the surprise.
6. `fly mpg users create` on the new cluster at **`writer`** role. **No redaction
   needed** — prints `Name` and `Role` only. A-017 held on scratch 2026-09-22, so
   the gate is satisfied.
7. `fly mpg attach <NEW_CLUSTER_ID>` with the writer account — **REDACT. Named
   F-014 offender.**
8. `fly secrets list` — `DATABASE_URL` reads **Staged**. Confirm you see it
   before fixing it. This is F-015 reproduced deliberately.
9. `fly secrets deploy`, then `fly secrets list` again. Both **Deployed**.
10. Verify the app is alive. `/healthz` cannot prove the database half — state
    that limit in the record rather than letting a green check stand for a
    verification that has not happened.
11. `fly mpg backup create stockgrader-db-r1 --type full` — per B-3. The
    restored cluster has no chain root of its own until this completes, and per
    B-6 a chain without a root is not a recovery point.

**Old cluster is not destroyed today.** It holds nothing and costs little. It is
destroyed once the ticker load and scoring are proven on `stockgrader-db-r1`.
Until then the exposed `stockgradermdk` credential remains valid against it — no
longer the app's path, but not dead.

**Row 4 moves off `Never` when step 10 has a DB-backed answer behind it**, not
when step 9 goes green. The Builder is right that the row's condition is the full
sequence.

---

## 6. After the drill

Ingest is next and is not blocked: the universe, the point-in-time fact store,
and the filing-date/accession discipline are the same work whichever way the four
§11 questions land.

**Scoring is still blocked by the TDD's own §13 completeness gate.** Three of its
conditions are open. See
`PLANNER-NOTE-2026-09-23-StockGraderMDK-GQS-variable-source-map.md` — four items
in §7 of that note are ratifiable immediately and would clear part of it.
