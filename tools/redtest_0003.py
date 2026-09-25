"""Red-test harness for 0003's new guards.

Each case gets a FRESH database: apply 0001-0003 through the runner, mutate the
schema to reintroduce a specific defect, re-run the verification, and record
whether the expected check fired.

The harness asserts its own preconditions first. A harness that cannot run
reports the same thing as a system with no defects.
"""
import os, re, subprocess, sys

PGBIN = r"C:\Program Files\PostgreSQL\18\bin"
PSQL = os.path.join(PGBIN, "psql")
PORT = "55433"
REPO = r"C:\Projects\StockGraderMDK"
PY = os.path.join(REPO, ".venv", "Scripts", "python.exe")
VERIFY = os.path.join(REPO, "db", "migrations",
                      "0003_fact_provenance_and_quarantine.verify.sql")

KEY = ("accession, entity_cik, concept, taxonomy, unit, period_type, "
       "period_start, period_end, dimensions")


def psql(db, sql=None, f=None):
    cmd = [PSQL, "-U", "postgres", "-h", "127.0.0.1", "-p", PORT, "-d", db,
           "-v", "ON_ERROR_STOP=1"]
    cmd += ["-c", sql] if sql else ["-f", f]
    return subprocess.run(cmd, capture_output=True, text=True)


def fresh(db, pre_sql=None):
    subprocess.run([PSQL, "-U", "postgres", "-h", "127.0.0.1", "-p", PORT,
                    "-d", "postgres", "-c", f"DROP DATABASE IF EXISTS {db};"],
                   capture_output=True, text=True)
    r = subprocess.run([PSQL, "-U", "postgres", "-h", "127.0.0.1", "-p", PORT,
                        "-d", "postgres", "-c", f"CREATE DATABASE {db};"],
                       capture_output=True, text=True)
    if r.returncode != 0:
        sys.exit("cannot create database: " + r.stderr)
    if pre_sql:
        # Placed BEFORE the migrations, as a human would have placed it.
        rr = psql(db, sql=pre_sql)
        if rr.returncode != 0:
            sys.exit("pre_sql failed: " + rr.stderr)
    env = dict(os.environ, DATABASE_URL=f"postgresql://postgres@127.0.0.1:{PORT}/{db}")
    r = subprocess.run([PY, "db/migrate.py", "apply"], cwd=REPO,
                       capture_output=True, text=True, env=env)
    return r


def run_case(name, mutations, expect_fire, expect_text, pre_sql=None):
    db = "sgcase"
    r = fresh(db, pre_sql=pre_sql)
    if not re.search(r"applied \d+ migration", r.stdout):
        print(f"  [{name}] SETUP FAILED - migrations did not apply cleanly")
        print("   ", (r.stdout + r.stderr).strip().splitlines()[-1:])
        return False
    for m in mutations:
        rr = psql(db, sql=m)
        if rr.returncode != 0:
            print(f"  [{name}] SETUP FAILED - mutation rejected: {rr.stderr.strip()[:120]}")
            return False
    out = psql(db, f=VERIFY)
    combined = out.stdout + out.stderr
    fired = out.returncode != 0
    ok = (fired == expect_fire) and (not expect_fire or expect_text in combined)
    status = "PASS" if ok else "*** UNEXPECTED ***"
    detail = ""
    if fired:
        for line in combined.splitlines():
            if "FAILED" in line or "ERROR" in line:
                detail = line.split("ERROR:")[-1].strip()[:110]
                break
    print(f"  [{status}] {name}")
    print(f"           expected fire={expect_fire} actual={fired}")
    if detail:
        print(f"           -> {detail}")
    return ok


print("=== harness precondition: server reachable and runner works ===")
probe = psql("postgres", sql="select 1;")
if probe.returncode != 0:
    sys.exit("server unreachable - refusing to report verdicts: " + probe.stderr)
print("  server reachable\n")

cases = [
    # The control MUST be green, or every other verdict is meaningless.
    ("CONTROL - unmodified 0003", [], False, ""),

    ("OPEN-59 wrong fix: key+value, no source_ordinal",
     ["ALTER TABLE fact_collision DROP CONSTRAINT fact_collision_one_per_source_row;",
      f"ALTER TABLE fact_collision ADD CONSTRAINT fact_collision_one_per_source_row "
      f"UNIQUE ({KEY}, value);"],
     True, "B6 FAILED"),

    ("OPEN-59 no constraint at all",
     ["ALTER TABLE fact_collision DROP CONSTRAINT fact_collision_one_per_source_row;"],
     True, ""),

    ("A5 regression: uniqueness on the colliding key alone",
     ["ALTER TABLE fact_collision DROP CONSTRAINT fact_collision_one_per_source_row;",
      f"ALTER TABLE fact_collision ADD CONSTRAINT fact_collision_bad UNIQUE ({KEY});"],
     True, "A5 FAILED"),

    ("OPEN-60: unprovenanced table in another schema",
     ["CREATE SCHEMA staging;",
      "CREATE TABLE staging.bulk_facts (id bigint, value numeric);"],
     True, "A2"),

    # Found on the migrations' FIRST contact with a real Fly cluster: scratch
    # carries keel_disposable_canary, a hand-placed disposability marker with no
    # provenance. A2 fails closed on it, correctly.
    ("canary present: the conditional exemption covers it",
     [], False, "",
     "CREATE TABLE keel_disposable_canary (marked_at timestamptz NOT NULL "
     "DEFAULT now(), marked_by text NOT NULL, note text);"),

    ("A3 still catches a genuinely stale exemption",
     ["INSERT INTO provenance_exempt (schema_name, table_name, reason) VALUES "
      "('public','no_such_table_anywhere','A stale exemption that names a "
      "table which does not exist, which is the hole A3 refuses.');"],
     True, "A3 FAILED"),

    ("OPEN-60: exemption must not reach across schemas",
     ["CREATE SCHEMA staging;",
      "CREATE TABLE staging.bulk_facts (id bigint, value numeric);",
      "INSERT INTO provenance_exempt (schema_name, table_name, reason) VALUES "
      "('public','bulk_facts','Exempts the public table only and must not "
      "silence another schema.');"],
     True, "A2"),
]

print("=== cases ===")
results = [run_case(*c) for c in cases]
print()
print(f"  {sum(results)}/{len(results)} behaved as expected")
sys.exit(0 if all(results) else 1)
