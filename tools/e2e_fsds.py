"""End-to-end proof of the fact loader against a real PostgreSQL 18.3 database.

Applies 0001-0004 through the runner, loads a synthetic FSDS archive, and checks
what actually landed. Then re-loads the SAME archive and asserts nothing moved,
because double-ingest idempotency is the schema's property and this is where it
is demonstrated rather than claimed.
"""
import io, os, subprocess, sys, zipfile
from datetime import datetime, timezone

sys.path.insert(0, r"C:\Projects\StockGraderMDK")
from ingest.fsds import load_quarter                      # noqa: E402
from ingest.edgar import Fetch                            # noqa: E402

import psycopg                                            # noqa: E402

PGBIN = r"C:\Program Files\PostgreSQL\18\bin"
PORT = "55434"
REPO = r"C:\Projects\StockGraderMDK"
PY = os.path.join(REPO, ".venv", "Scripts", "python.exe")
DSN = f"postgresql://postgres@127.0.0.1:{PORT}/sgfacts"

ADSH_A = "0001628280-26-034133"
ADSH_B = "0000320193-26-000010"
ADSH_MISSING = "0009999999-26-000001"

SUB = ("adsh\tcik\tname\tform\tperiod\tprevrpt\n"
       f"{ADSH_A}\t1628280\tEXAMPLE CORP\t10-Q\t20260331\t0\n"
       f"{ADSH_B}\t320193\tOTHER INC\t10-K\t20260331\t1\n"
       f"{ADSH_MISSING}\t777777\tGHOST CO\t10-Q\t20260331\t0\n")

H = "adsh\ttag\tversion\tcoreg\tddate\tqtrs\tuom\tsegments\tvalue"
ROWS = [
    # 2 that load cleanly
    f"{ADSH_A}\tRevenues\tus-gaap/2025\t\t20260331\t1\tUSD\t\t5000",
    f"{ADSH_A}\tAssets\tus-gaap/2025\t\t20260331\t0\tUSD\tProductAxis=WidgetMember\t9000",
    # 1 filer extension - loads, and is counted
    f"{ADSH_A}\tCustomMetric\t{ADSH_A}\t\t20260331\t0\tUSD\t\t42",
    # 1 co-registrant - refused (OPEN-39)
    f"{ADSH_A}\tRevenues\tus-gaap/2025\tSUBSIDIARY\t20260331\t1\tUSD\t\t111",
    # 1 unreadable dimensions - refused, NOT defaulted to {}
    f"{ADSH_A}\tEquity\tus-gaap/2025\t\t20260331\t0\tUSD\tgarbage\t7",
    # 1 empty value - refused
    f"{ADSH_A}\tLiabilities\tus-gaap/2025\t\t20260331\t0\tUSD\t\t",
    # 2 that DISAGREE on the same key - both quarantined, neither loaded
    f"{ADSH_B}\tDerivativeAsset\tus-gaap/2025\t\t20260331\t0\tUSD\t\t-3123000",
    f"{ADSH_B}\tDerivativeAsset\tus-gaap/2025\t\t20260331\t0\tUSD\t\t706000",
    # 2 that AGREE exactly - collapse to one load
    f"{ADSH_B}\tCash\tus-gaap/2025\t\t20260331\t0\tUSD\t\t250",
    f"{ADSH_B}\tCash\tus-gaap/2025\t\t20260331\t0\tUSD\t\t250",
    # 1 whose filing is absent from `filing` - its own counter
    f"{ADSH_MISSING}\tRevenues\tus-gaap/2025\t\t20260331\t1\tUSD\t\t1",
]
NUM = H + "\n" + "\n".join(ROWS) + "\n"


def build_zip() -> bytes:
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w") as z:
        z.writestr("sub.txt", SUB)
        z.writestr("num.txt", NUM)
    return buf.getvalue()


def sh(*args, **kw):
    return subprocess.run(args, capture_output=True, text=True, timeout=120, **kw)


def sh_detached(*args):
    """pg_ctl start must NOT inherit a captured pipe: the postgres child keeps
    it open and subprocess.run then waits for an EOF that never arrives."""
    return subprocess.run(args, stdout=subprocess.DEVNULL,
                          stderr=subprocess.DEVNULL, timeout=120)


def psql(db, sql):
    return sh(os.path.join(PGBIN, "psql"), "-U", "postgres", "-h", "127.0.0.1",
              "-p", PORT, "-d", db, "-v", "ON_ERROR_STOP=1", "-Atc", sql)


# ---- cluster -------------------------------------------------------------
data = os.path.join(os.path.dirname(os.path.abspath(__file__)), "pgdata2")
sh_detached(os.path.join(PGBIN, "pg_ctl"), "-D", data, "stop", "-m", "immediate")
if os.path.isdir(data):
    import shutil; shutil.rmtree(data, ignore_errors=True)
r = sh(os.path.join(PGBIN, "initdb"), "-D", data, "-U", "postgres", "-A", "trust", "-E", "UTF8")
if r.returncode != 0:
    sys.exit("initdb failed: " + r.stderr[-400:])
r = sh_detached(os.path.join(PGBIN, "pg_ctl"), "-D", data, "-o",
                f"-p {PORT} -c listen_addresses=127.0.0.1",
                "-l", os.path.join(data, "log"), "start")
if r.returncode != 0:
    sys.exit(f"pg_ctl failed rc={r.returncode}")

if psql("postgres", "select 1").returncode != 0:
    sys.exit("server did not come up - refusing to report results")
psql("postgres", "CREATE DATABASE sgfacts;")

env = dict(os.environ, DATABASE_URL=DSN)
r = sh(PY, "db/migrate.py", "apply", cwd=REPO, env=env)
print(r.stdout.strip().splitlines()[-1] if r.stdout else r.stderr[-400:])
if "applied 4 migration" not in r.stdout:
    print(r.stdout, r.stderr)
    sys.exit("migrations did not apply - refusing to report load results")

ok = True
with psycopg.connect(DSN, autocommit=False) as conn:
    with conn.cursor() as cur:
        # Slice 1's job: filers and filings exist before facts reference them.
        cur.execute("""
            INSERT INTO fetch_log (url, retrieved_at, sha256, content_bytes)
            VALUES ('https://example.invalid/submissions.zip',
                    '2026-09-25 05:00:00+00', %s, 10) RETURNING fetch_id
        """, ("a" * 64,))
        f1 = cur.fetchone()[0]
        for cik, name in ((1628280, "EXAMPLE CORP"), (320193, "OTHER INC")):
            cur.execute("""INSERT INTO filer (cik, current_name, metadata_as_of,
                           source_fetch_id) VALUES (%s,%s,'2026-09-25',%s)""",
                        (cik, name, f1))
        for adsh, cik in ((ADSH_A, 1628280), (ADSH_B, 320193)):
            cur.execute("""INSERT INTO filing (accession, cik, form_type,
                           filing_date, is_amendment, source_fetch_id)
                           VALUES (%s,%s,'10-Q','2026-04-15',false,%s)""",
                        (adsh, cik, f1))

        archive = build_zip()
        fetch = Fetch(url="https://example.invalid/fsds/2026q1.zip",
                      retrieved_at=datetime(2026, 9, 25, 8, 0, tzinfo=timezone.utc),
                      sha256="b" * 64, body=archive)

        first = load_quarter(cur, quarter="2026q1", fetch=fetch, archive=archive)
        conn.commit()

print("\n=== first load ===")
for k, v in first.items():
    print(f"  {k:>24}: {v}")

expected = dict(submissions_seen=3, facts_seen=11, facts_loaded=4,
                refused_coreg=1, refused_malformed=2,
                refused_unknown_filing=1, collapsed_duplicates=1,
                quarantined=2, extension_facts=1)
print("\n=== expectations ===")
for k, v in expected.items():
    got = first[k]
    flag = "ok " if got == v else "XX "
    if got != v:
        ok = False
    print(f"  {flag}{k:>24}: got {got}, expected {v}")

# the arithmetic the database enforces
total = (first["facts_loaded"] + first["refused_coreg"] + first["refused_malformed"]
         + first["refused_unknown_filing"] + first["collapsed_duplicates"]
         + first["quarantined"])
print(f"\n  accounting: {total} accounted vs {first['facts_seen']} seen "
      f"-> {'BALANCED' if total == first['facts_seen'] else 'MISMATCH'}")
if total != first["facts_seen"]:
    ok = False

print("\n=== what landed ===")
for label, q in [
    ("fact rows", "SELECT count(*) FROM fact"),
    ("quarantined", "SELECT count(*) FROM fact_collision"),
    ("coverage rows", "SELECT count(*) FROM coverage_quarter"),
    ("window", "SELECT earliest_quarter||'..'||latest_quarter||' gaps='||gaps FROM coverage_window"),
    ("collision rate", "SELECT coalesce(sum(quarantined_rows),0) FROM fact_collision_rate"),
    ("both values kept", "SELECT string_agg(value::text, ' | ' ORDER BY value) FROM fact_collision"),
    ("dimensions stored", "SELECT dimensions::text FROM fact WHERE concept='Assets'"),
    ("duration derived", "SELECT period_start||'..'||period_end FROM fact WHERE concept='Revenues'"),
]:
    print(f"  {label:>20}: {psql('sgfacts', q).stdout.strip()}")

# ---- idempotency ---------------------------------------------------------
with psycopg.connect(DSN, autocommit=False) as conn:
    with conn.cursor() as cur:
        archive = build_zip()
        fetch2 = Fetch(url="https://example.invalid/fsds/2026q1.zip",
                       retrieved_at=datetime(2026, 9, 26, 8, 0, tzinfo=timezone.utc),
                       sha256="b" * 64, body=archive)
        load_quarter(cur, quarter="2026q1", fetch=fetch2, archive=archive)
        conn.commit()

print("\n=== re-ingest, NEW fetch, same archive ===")
after = {k: psql("sgfacts", q).stdout.strip() for k, q in [
    ("fact rows", "SELECT count(*) FROM fact"),
    ("quarantined", "SELECT count(*) FROM fact_collision"),
    ("coverage rows", "SELECT count(*) FROM coverage_quarter"),
]}
for k, v in after.items():
    print(f"  {k:>20}: {v}")

if after["fact rows"] != "4" or after["quarantined"] != "2" or after["coverage rows"] != "1":
    ok = False
    print("\n  *** NOT IDEMPOTENT ***")
else:
    print("\n  idempotent: re-ingesting the same archive under a new fetch changed nothing")

sh_detached(os.path.join(PGBIN, "pg_ctl"), "-D", data, "stop", "-m", "immediate")
import shutil; shutil.rmtree(data, ignore_errors=True)
print("\n  cluster removed")
sys.exit(0 if ok else 1)
