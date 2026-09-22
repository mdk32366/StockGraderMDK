"""Repository hygiene guards (Principles 4 and 5).

Walks the FILESYSTEM, not git — so an untracked local .env is inspected too."""
import re
from pathlib import Path

from tests.keel_db_guard import CONFIRM_ENV

ROOT = Path(__file__).resolve().parent.parent
SKIP_DIRS = {".git", ".venv", "venv", "__pycache__", ".pytest_cache", "node_modules"}

# Patterns are assembled from pieces so this file never matches itself.
SECRET_PATTERNS = {
    "postgres URL with password": re.compile(r"postgres(?:ql)?://[^:/\s@]+:[^@\s]+@"),
    "Fly API token": re.compile("Fly" + r"V1 fm\d_"),
    "Anthropic key": re.compile("sk" + r"-ant-[A-Za-z0-9_-]{10,}"),
    "AWS access key": re.compile("AK" + r"IA[0-9A-Z]{16}"),
    "private key block": re.compile("-----BEGIN " + r"[A-Z ]*PRIVATE KEY-----"),
}

DIRECT_CONNECT = re.compile(r"\b(psycopg2?\.connect|asyncpg\.connect|create_engine)\s*\(")


def _files():
    for p in ROOT.rglob("*"):
        if p.is_file() and not (SKIP_DIRS & set(p.relative_to(ROOT).parts)):
            yield p


def _text(p: Path) -> str | None:
    try:
        return p.read_text(encoding="utf-8")
    except (UnicodeDecodeError, OSError):
        return None


def test_no_secrets_anywhere_in_the_working_tree():
    hits = []
    for p in _files():
        text = _text(p)
        if text is None:
            continue
        for name, pat in SECRET_PATTERNS.items():
            if pat.search(text):
                hits.append(f"{p.relative_to(ROOT)}: {name}")
    assert not hits, "Secrets found (Principle 4):\n" + "\n".join(hits)


def test_confirmation_variable_never_lives_in_an_env_file():
    """Factor 1 of the DB guard is only a factor if it cannot be loaded by
    sourcing a file. It must be typed by hand."""
    offenders = [
        str(p.relative_to(ROOT))
        for p in _files()
        if p.name.startswith(".env") and CONFIRM_ENV in (_text(p) or "")
    ]
    assert not offenders, f"{CONFIRM_ENV} found in env file(s): {offenders}"


def test_tests_never_open_database_connections_directly():
    """Enforces the DB guard's scope: all test DB access goes via db_url."""
    allowed = {"keel_db_guard.py", "test_hygiene.py"}
    offenders = [
        str(p.relative_to(ROOT))
        for p in (ROOT / "tests").rglob("*.py")
        if p.name not in allowed and DIRECT_CONNECT.search(_text(p) or "")
    ]
    assert not offenders, f"Direct DB connections in tests (use db_url): {offenders}"


UTF8_BOM = b"\xef\xbb\xbf"


def test_powershell_scripts_are_safe_for_windows_powershell_5():
    """F-006: Windows PowerShell 5.1 reads a BOM-less .ps1 as ANSI (cp1252).
    An em-dash (e2 80 94) then decodes to a curly quote that PowerShell treats
    as a string delimiter, and the script fails to PARSE, reported at a
    misleading line. CI runs on Linux and never executes .ps1 files, so this
    test is the only thing in the gate that can see the defect.

    D-013: every .ps1 must carry a UTF-8 BOM AND be pure ASCII after it.
    The BOM protects the next person who pastes a non-ASCII character in;
    ASCII protects against an editor that silently strips the BOM."""
    problems = []
    for p in _files():
        if p.suffix.lower() != ".ps1":
            continue
        raw = p.read_bytes()
        rel = p.relative_to(ROOT)
        if not raw.startswith(UTF8_BOM):
            problems.append(f"{rel}: no UTF-8 BOM")
        body = raw[len(UTF8_BOM):] if raw.startswith(UTF8_BOM) else raw
        for lineno, line in enumerate(body.split(b"\n"), start=1):
            bad = [b for b in line if b > 0x7F]
            if bad:
                problems.append(f"{rel}:{lineno}: non-ASCII byte(s) {bytes(bad[:3]).hex(' ')}")
    assert not problems, "PowerShell 5.1 hazards (F-006, D-013):\n" + "\n".join(problems)
