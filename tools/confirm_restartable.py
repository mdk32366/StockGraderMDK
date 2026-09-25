"""OPEN-65's confirmation: quarters commit independently and a re-run is a no-op.

The Planner's point is that a 34-hour unattended batch with free restart is not
a problem to optimise - but that rests on a property, and the property must be
confirmed rather than assumed. Three loads:

  1. 2026q2            -> establishes a baseline
  2. 2015q2            -> a SECOND quarter, committed independently
  3. 2026q2 AGAIN      -> must change nothing

Also exercises the gap detection on real data for the first time: 2015q2 and
2026q2 are eleven years apart, so `coverage_window.gaps` should be large and
non-zero. A batch that dies at hour twenty leaves exactly this shape, and a
window that reported it as contiguous would be the OPEN-51 failure arriving
through the instrument built to prevent it.
"""
import os, subprocess, sys, time

PGBIN = r"C:\Program Files\PostgreSQL\18\bin"
PORT = "55438"
REPO = r"C:\Projects\StockGraderMDK"
PY = os.path.join(REPO, ".venv", "Scripts", "python.exe")
S = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(S, "pgmulti")
DSN = f"postgresql://postgres@127.0.0.1:{PORT}/sgmulti"


def sh(*a, **k):
    return subprocess.run(a, capture_output=True, text=True, timeout=900, **k)


def detached(*a):
    return subprocess.run(a, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
                          timeout=120)


def q(sql, db="sgmulti"):
    r = sh(os.path.join(PGBIN, "psql"), "-U", "postgres", "-h", "127.0.0.1",
           "-p", PORT, "-d", db, "-Atc", sql)
    return r.stdout.strip()


detached(os.path.join(PGBIN, "pg_ctl"), "-D", DATA, "stop", "-m", "immediate")
import shutil
shutil.rmtree(DATA, ignore_errors=True)
if sh(os.path.join(PGBIN, "initdb"), "-D", DATA, "-U", "postgres", "-A", "trust",
      "-E", "UTF8").returncode != 0:
    sys.exit("initdb failed")
detached(os.path.join(PGBIN, "pg_ctl"), "-D", DATA, "-o",
         f"-p {PORT} -c listen_addresses=127.0.0.1",
         "-l", os.path.join(DATA, "log"), "start")
if q("select 1", "postgres") != "1":
    sys.exit("server did not start - refusing to report results")
q("CREATE DATABASE sgmulti", "postgres")

env = dict(os.environ, DATABASE_URL=DSN)
r = sh(PY, "db/migrate.py", "apply", cwd=REPO, env=env)
if "applied 4 migration" not in r.stdout:
    sys.exit("migrations failed: " + r.stdout + r.stderr)
print("  migrations applied")


def load(quarter):
    t0 = time.time()
    r = sh(PY, "tools/load_quarter.py", "--quarter", quarter, "--submissions",
           "--archive", os.path.join(S, f"{quarter}.zip"), cwd=REPO, env=env)
    ok = "committed" in r.stdout
    return ok, time.time() - t0, r.stdout + r.stderr


results = {}
for step, quarter in ((1, "2026q2"), (2, "2015q2"), (3, "2026q2")):
    ok, secs, out = load(quarter)
    facts = int(q("SELECT count(*) FROM fact"))
    quarters = int(q("SELECT count(*) FROM coverage_quarter"))
    results[step] = (quarter, ok, secs, facts, quarters)
    print(f"  step {step}: {quarter:>7}  ok={ok}  {secs:5.1f}s  "
          f"facts={facts:,}  coverage_rows={quarters}")
    if not ok:
        print(out[-600:])

print()
print("=== the three properties ===")
_, _, _, f1, c1 = results[1]
_, _, _, f2, c2 = results[2]
_, _, _, f3, c3 = results[3]

a = c2 == 2 and f2 > f1
print(f"  [{'PASS' if a else 'FAIL'}] a second quarter commits independently "
      f"(coverage rows {c1} -> {c2}, facts {f1:,} -> {f2:,})")

b = f3 == f2 and c3 == c2
print(f"  [{'PASS' if b else 'FAIL'}] re-running a completed quarter is a NO-OP "
      f"(facts {f2:,} -> {f3:,}, coverage rows {c2} -> {c3})")

win = q("SELECT earliest_quarter||' .. '||latest_quarter||'  quarters='||"
        "quarters_loaded||'  gaps='||gaps FROM coverage_window")
gaps = int(q("SELECT gaps FROM coverage_window"))
c = gaps > 0
print(f"  [{'PASS' if c else 'FAIL'}] a discontiguous window reports its gaps")
print(f"          {win}")

print()
print("  overall:", "ALL THREE HOLD" if (a and b and c) else "*** SOMETHING FAILED ***")

detached(os.path.join(PGBIN, "pg_ctl"), "-D", DATA, "stop", "-m", "immediate")
shutil.rmtree(DATA, ignore_errors=True)
print("  cluster removed")
sys.exit(0 if (a and b and c) else 1)
