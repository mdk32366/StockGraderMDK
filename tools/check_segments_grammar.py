"""Fetch one FSDS quarter and confirm the `segments` grammar against readme.htm.

Two questions, and the second is the one that decides anything:
  1. What does the SEC document `segments` to contain?
  2. Does the loader's parser accept what the archive actually holds?

A documented grammar the real data violates is the shape this project keeps
finding, so both are checked and disagreement between them is the finding.
"""
import os, re, sys, zipfile, html


def p(*a):
    """Windows console is cp1252; never let an encoding error hide a result."""
    print(*[str(x).encode("ascii", "replace").decode("ascii") for x in a])

sys.path.insert(0, r"C:\Projects\StockGraderMDK")
from ingest.edgar import EdgarClient                       # noqa: E402
from ingest.fsds import parse_segments, FactRefused        # noqa: E402

SCRATCH = os.path.dirname(os.path.abspath(__file__))
QUARTER = "2026q2"
URL = f"https://www.sec.gov/files/dera/data/financial-statement-data-sets/{QUARTER}.zip"
CACHE = os.path.join(SCRATCH, f"{QUARTER}.zip")

if os.path.exists(CACHE):
    body = open(CACHE, "rb").read()
    p(f"  using cached {QUARTER}.zip ({len(body):,} bytes)")
else:
    p(f"  fetching {URL}")
    client = EdgarClient()
    f = client.fetch(URL)
    body = f.body
    open(CACHE, "wb").write(body)
    p(f"  fetched {len(body):,} bytes  sha256={f.sha256[:16]}")

z = zipfile.ZipFile(CACHE)
p("  members:", ", ".join(sorted(n for n in z.namelist())))

# ---- 1. the documentation -------------------------------------------------
readme_name = next((n for n in z.namelist() if n.lower().startswith("readme")), None)
p("\n=== readme.htm on `segments` ===")
if not readme_name:
    p("  NO README IN ARCHIVE - cannot confirm from documentation")
else:
    raw = z.read(readme_name).decode("utf-8", "replace")
    text = re.sub(r"<[^>]+>", " ", raw)
    text = html.unescape(text)
    text = re.sub(r"\s+", " ", text)
    for m in re.finditer(r"segments", text, re.I):
        s = max(0, m.start() - 200)
        chunk = text[s:m.start() + 700].strip()
        p("  ...", chunk[:900])
        p()
        break
    # also pull any explicit axis/member wording
    for kw in ("axis", "member", "semicolon", "delimit"):
        for m in re.finditer(kw, text, re.I):
            s = max(0, m.start() - 150)
            p(f"  [{kw}] ...{text[s:m.start()+250].strip()[:400]}")
            break

# ---- 2. what the data actually holds --------------------------------------
p("\n=== measuring parse_segments against real num.txt ===")
num = z.read("num.txt").decode("utf-8", "replace")
lines = num.splitlines()
header = lines[0].split("\t")
try:
    idx = header.index("segments")
except ValueError:
    p("  num.txt has no `segments` column; header:", header)
    sys.exit(1)

total = nonempty = accepted = refused = 0
samples_ok, samples_bad = [], []
for line in lines[1:]:
    if not line.strip():
        continue
    parts = line.split("\t")
    if idx >= len(parts):
        continue
    total += 1
    raw = parts[idx]
    if not raw.strip():
        continue
    nonempty += 1
    try:
        d = parse_segments(raw)
        accepted += 1
        if len(samples_ok) < 3:
            samples_ok.append((raw[:150], d))
    except FactRefused as e:
        refused += 1
        if len(samples_bad) < 6:
            samples_bad.append((raw[:200], str(e)[:100]))

p(f"  num.txt rows          : {total:,}")
p(f"  with segments         : {nonempty:,}  ({nonempty/total*100:.1f}%)")
p(f"  parser ACCEPTED       : {accepted:,}  ({accepted/nonempty*100:.2f}% of non-empty)")
p(f"  parser REFUSED        : {refused:,}  ({refused/nonempty*100:.2f}% of non-empty)")

p("\n  accepted samples:")
for raw, d in samples_ok:
    p(f"    {raw!r}\n      -> {d}")

if samples_bad:
    p("\n  REFUSED samples - these decide whether the grammar is right:")
    for raw, why in samples_bad:
        p(f"    {raw!r}\n      -> {why}")
else:
    p("\n  no refusals: the grammar accepts every non-empty segments value "
          "in this quarter")
