# RECOVERY — Planner → Code — StockGraderMDK: D28, D30, D32 content, and a D33 amendment

**From:** Planner · **Issued:** 2026-09-25, first issue
**Replaces the delivery of:** D28, D30 and D32 — each named as a previous
manifest by a delivery that arrived, none of them present in `docs/planner/`.

**This is a new document carrying their content, not a re-send.** Re-sending has
failed six times, and D19 §1's other option — content moved rather than the file
— is what this is. The originals stand as issued.

---

## 1. First: D33 overstates the git relay, and the register should not carry it

D33 says the relay becomes git and **"losses become impossible rather than
detectable."**

**That is too strong and it is my error.** Git is the **archive** and the
Planner's **read path**. It is **not** the Planner → Code transfer mechanism,
which is unchanged.

**Correct statement:** losses become impossible **after receipt**. Before
receipt they are exactly as possible as they were on day one — and every loss so
far happened on that hop.

**Amend D33 in place with the reason.** The hazard is a reader concluding *the
relay is git* and stopping watching the hop that is still live. That is the
tolerated-error-hides-real-error shape, arriving in a decision rather than a
counter.

**What did improve, and it is real:** verification. Once the Planner can reach
`docs/planner/`, delivery is confirmed by **reading what landed** rather than by
predicting a count and waiting for a mismatch. Losses stay possible and become
**immediately visible** instead of inferred two deliveries later.

**The manifest chain therefore stays** until that read is confirmed — D33's own
end condition, unmet. See §6.

---

## 2. D28's content — the freeze, narrowed

D27 wrote the freeze as blanket and stopped work the owner did not intend to
stop. **The owner clarified: the constraint is on DESTROYING clusters. Building
whatever is needed is unrestricted.**

**Holds:**
- **No cluster is destroyed**, ours or anyone's, until what runs on the
  unidentified clusters is established.
- **Ruling 6's destroy of `stockgrader-db` stays suspended.** Holding cost
  accepted: roughly $41/month.

**Unrestricted:**
- **Building clusters** — probe clusters, test clusters, a real Basic cluster.
- **OPEN-25's role drops were never frozen.** Operations on roles inside a living
  cluster, still gated ahead of 0001's run, and **their cheap window closes when
  the fact store has tables.**

**How the freeze ends:** not with more `fly mpg` commands. PharmFoldMDK's and
Sentinel's own registers should record which cluster each project cut over to.
If they do, it is a document read; if they do not, that absence is the finding
and it belongs to those projects.

---

## 3. D28's standing requirement — anything built is named and recorded

Because nothing can be cleaned up while the freeze holds, **every cluster created
until it lifts is one we are committing to keep.**

1. **A `-n` name saying what it is for.** `stockgrader-db-r1` is identifiable by
   reading; `sentinel-holy-rain-4562 restored 2026-08-17… restored 2026-09-13…`
   only by archaeology.
2. **A register line: who built it, why, and what ends it.** The *what ends it*
   is the load-bearing half — **a retained cluster with no stated end condition
   is an orphan with a birth certificate.**

**This applies to B-9's probe cluster**, whose end condition is the freeze
lifting.

---

## 4. D32's content — two Planner errors, and the §8 endorsement

**P-12 — the coverage ruling preceded the measurement.** The owner ruled 45
quarters before anyone knew bytes per row, and the window turned out not to be
the binding constraint at all. Measuring first would have made three of the four
sizing rounds unnecessary. **The rule: a ruling that depends on a figure waits
for the figure.**

**P-13 — §11.1 was deferred to "its own session" on day one and no session was
ever scheduled.** The scoring track has not moved in three days. **A deferral
without a date is a deferral without an end.**

**Code's §8 rules are endorsed, and two of the three bind the Planner harder:**

- Default proposal is build, not measure.
- **No new OPEN item unless the block was blocked by it.** OPEN-44 through 62 are
  almost all mine. Several were load-bearing; several were observations turned
  into obligations because writing them as open items *felt* more rigorous than
  writing them as notes. **It is not. It is a bigger backlog for a fresh context
  to inherit.**
- **Sweep the register at the checkpoint.** The sweep is the Planner's to propose
  and the Builder's to apply, since the Planner created the surplus. An item that
  has gated nothing in 48 hours is a note.

---

## 5. D30 needs no recovery

D30 was the consolidation plus the OPEN-57 ruling. **Its unique content is
already in your hands:** OPEN-61 is stated in full in D31 §3, and OPEN-62 was
ruled by the owner in D33. **Mark D30 closed rather than outstanding.**

---

## 6. What the Planner needs to close D33's end condition

**One URL.** `/tree/…/docs/planner` is **robots-disallowed** — GitHub refuses
automated access to directory views. File pages under `/blob/` work; that is how
`decisions.md` was read. And constructed URLs are refused by the tool, correctly.

**So the Planner cannot discover files — only read a URL that has appeared, or
one linked from inside a page already fetched.**

**`INDEX.md` is therefore the navigation root**, for a reason nobody anticipated
when it was generated: it is a *file*, not a directory, and it links to
everything. **Its blob URL, pasted once, closes this permanently** — after that
the Planner follows links from inside it.

**Worth recording in INDEX.md itself:** any future reorganisation must keep a
single linked index file, because a directory listing is not readable and a
reader who can only follow links needs one door.

---

## 7. Archive observations, for the register

**The `*-Planner-*` selection error is the third instance of the pattern and it
landed on the worst possible subset** — every `RULING-RECORD-*` file, which is
the set carrying the owner's decisions rather than the Planner's reasoning. Had
it shipped, the archive would have preserved the arguments and dropped the
rulings.

**The word-splitting duplicate loop is the fourth instance of a verification
method that ran cleanly and checked nothing**, after the D-019 counter, the trip
harness and B1's tautology. Caught mid-task, which is the first time one has
been.

**The two-version `RULING-RECORD` was resolved on evidence rather than
inference** — `decisions.md` already carried both rulings, so the register took
the later revision at the time. And flagging that the sort-order pick happened to
land right **without being a method** is the distinction that matters: a correct
outcome from an arbitrary process is the one nobody re-examines.

**One correction to the archetype note.** The classifier is **both ruled and
unspecified**, and those are different things. Ruling 13 settled option (c); the
ruling itself says the classifier needs its own definition, its own
`insufficient_data` path and its own place in the output. **The choice is made;
the artifact does not exist.**
