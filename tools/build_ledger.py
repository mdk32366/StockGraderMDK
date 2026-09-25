"""Build ledger — what actually shipped, computed rather than narrated.

WHY THIS EXISTS
---------------
On 2026-09-25 this project measured itself: commit velocity had fallen 23 -> 9
-> 4 across three days while document volume held, reaching five documents per
commit. The register grew faster than it closed. Nobody noticed until the owner
asked, and the data to notice had been sitting in git the whole time.

The same thing happened on PharmFoldMDK. **It is not a project-specific mistake,
so this is not a project-specific tool.** It has no StockGraderMDK in it and
should be copied unchanged into any repo that runs a plan/build loop.

THE DESIGN POINT
----------------
Every *process* rule this project wrote failed. "Default to build, not measure"
was adopted and violated the next day. "Name the decision a measurement changes"
was recorded and walked past. Rules in a register do not fire.

Every *executable* guard caught something: a CHECK constraint refused a bad load,
a derived catalogue query found an unprovenanced table, a --check flag caught a
stale index. So this is executable too.

**Put its output at the top of every report, above the prose.** If the ledger is
empty, that is the headline and nobody has to be the one to notice.

A LIMITATION, STATED SO IT IS NOT DISCOVERED LATER
--------------------------------------------------
**This can only see what is in the repository.** Run against the days it was
built to describe, it reports roughly parity - because during the bog the
documents were written to the owner's Downloads folder and never committed. The
output that constituted the problem was invisible to git.

It works going forward *because* Code reports are now committed to
`docs/reports/` as well as delivered. The two changes reinforce: committing
reports made them measurable, and measuring them is what makes the ledger
meaningful. **If reports ever stop being committed, this tool goes quiet without
going wrong**, which is the failure mode it exists to prevent. Keep them
committed.

USAGE
-----
    python tools/build_ledger.py                  # since the last report commit
    python tools/build_ledger.py --since 3.days
    python tools/build_ledger.py --since <sha>
    python tools/build_ledger.py --markdown       # a block to paste
    python tools/build_ledger.py --check          # exit 1 if prose outran code
"""

from __future__ import annotations

import argparse
import os
import re
import subprocess
import sys

CODE_EXT = {".py", ".sql", ".ts", ".tsx", ".js", ".jsx", ".go", ".rs", ".java",
            ".rb", ".c", ".h", ".cpp", ".cs", ".sh", ".ps1", ".yml", ".yaml",
            ".toml", ".cfg", ".ini", ".json"}
PROSE_EXT = {".md", ".rst", ".txt", ".adoc"}

#: Paths holding documents this loop RECEIVED rather than authored. Committing
#: an inbound archive is bookkeeping, not output, and counting it as prose makes
#: the ledger fire on any day spent filing. A guard that always fires is ignored,
#: which is a worse failure than no guard.
#:
#: This is an exclusion of known-inputs, not a filter tuned to flatter the
#: number - reports the loop writes still count, in full.
RECEIVED_DIRS = ("docs/planner/", "docs/inbox/", "docs/received/")


def git(*args: str) -> str:
    r = subprocess.run(("git",) + args, capture_output=True, text=True)
    return r.stdout.strip() if r.returncode == 0 else ""


def default_since() -> tuple[str, str]:
    """The last commit that looks like a report drop, else 1 day ago."""
    sha = git("log", "--format=%H", "-n", "1", "--grep", r"^docs(reports)")
    if sha:
        return sha, "since the last report"
    sha = git("log", "--format=%H", "-n", "1", "--before", "1.day")
    return (sha, "since 24h ago") if sha else ("", "all history")


def collect(since: str):
    rng = f"{since}..HEAD" if since else "HEAD"
    shas = [s for s in git("log", "--format=%H", rng).splitlines() if s]

    numstat = git("diff", "--numstat", rng) if since else ""
    code_add = code_del = prose_add = prose_del = received_add = 0
    code_files: set[str] = set()
    prose_files: set[str] = set()
    received_files: set[str] = set()
    for line in numstat.splitlines():
        parts = line.split("\t")
        if len(parts) != 3:
            continue
        a, d, path = parts
        if a == "-" or d == "-":      # binary
            continue
        if any(path.startswith(d) for d in RECEIVED_DIRS):
            received_add += int(a)
            received_files.add(path)
            continue
        ext = os.path.splitext(path)[1].lower()
        if ext in CODE_EXT:
            code_add += int(a); code_del += int(d); code_files.add(path)
        elif ext in PROSE_EXT:
            prose_add += int(a); prose_del += int(d); prose_files.add(path)

    return {
        "commits": len(shas),
        "code_files": len(code_files),
        "code_added": code_add,
        "code_removed": code_del,
        "prose_files": len(prose_files),
        "prose_added": prose_add,
        "prose_removed": prose_del,
        "received_files": len(received_files),
        "received_added": received_add,
    }


def count_test_functions() -> int:
    n = 0
    for root, dirs, files in os.walk("."):
        dirs[:] = [d for d in dirs
                   if d not in {".git", ".venv", "node_modules", "__pycache__"}]
        for f in files:
            if f.startswith("test_") and f.endswith(".py"):
                try:
                    with open(os.path.join(root, f), encoding="utf-8") as fh:
                        n += len(re.findall(r"^\s*def test_", fh.read(), re.M))
                except OSError:
                    pass
    return n


def verdict(m: dict) -> tuple[str, bool]:
    """Informational, and loud. The ratio is a signal, not a law."""
    code, prose = m["code_added"], m["prose_added"]
    if code == 0 and prose == 0:
        return "NOTHING SHIPPED in this window.", False
    if code == 0:
        return (f"NOTHING EXECUTABLE SHIPPED. {prose:,} lines of prose, "
                f"0 lines of code."), False
    ratio = prose / code
    if ratio >= 2:
        return (f"PROSE OUTRAN CODE {ratio:.1f}:1 ({prose:,} vs {code:,}). "
                "That is the shape of a loop resolving uncertainty instead of "
                "shipping. Check that the next block names an artifact."), False
    if ratio >= 1:
        return (f"Prose slightly ahead of code, {ratio:.1f}:1 "
                f"({prose:,} vs {code:,})."), True
    return (f"Code ahead of prose, {code:,} vs {prose:,} "
            f"({prose/code:.2f}:1)."), True


def main() -> int:
    ap = argparse.ArgumentParser(prog="build_ledger")
    ap.add_argument("--since", help="a sha, or a git date like 3.days")
    ap.add_argument("--markdown", action="store_true", help="emit a report block")
    ap.add_argument("--check", action="store_true",
                    help="exit 1 when prose outran code")
    args = ap.parse_args()

    if not git("rev-parse", "--git-dir"):
        print("not a git repository", file=sys.stderr)
        return 2

    if args.since:
        since, label = (args.since, f"since {args.since}")
        if not git("rev-parse", "--verify", "--quiet", since):
            since = git("log", "--format=%H", "-n", "1", "--before", args.since)
    else:
        since, label = default_since()

    m = collect(since)
    m["tests"] = count_test_functions()
    text, ok = verdict(m)

    if args.markdown:
        print(f"**Build ledger - {label}**\n")
        print("| | |\n|---|---|")
        print(f"| Commits | **{m['commits']}** |")
        print(f"| Code | **+{m['code_added']:,} / -{m['code_removed']:,}** "
              f"across {m['code_files']} files |")
        print(f"| Prose | +{m['prose_added']:,} / -{m['prose_removed']:,} "
              f"across {m['prose_files']} files |")
        print(f"| Test functions | **{m['tests']}** |")
        if m["received_files"]:
            print(f"| _Received documents (excluded)_ | "
                  f"_+{m['received_added']:,} across "
                  f"{m['received_files']} files_ |")
        print(f"\n{text}")
    else:
        print(f"  build ledger - {label}")
        print(f"    commits      : {m['commits']}")
        print(f"    code         : +{m['code_added']:,} / -{m['code_removed']:,}"
              f"  ({m['code_files']} files)")
        print(f"    prose        : +{m['prose_added']:,} / -{m['prose_removed']:,}"
              f"  ({m['prose_files']} files)")
        print(f"    test funcs   : {m['tests']}  (pytest collects more: parametrize)")
        if m["received_files"]:
            print(f"    received     : +{m['received_added']:,} "
                  f"({m['received_files']} files) - EXCLUDED, inbound not authored")
        print(f"    {text}")

    return 0 if (ok or not args.check) else 1


if __name__ == "__main__":
    raise SystemExit(main())
