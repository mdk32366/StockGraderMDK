"""Regenerate the committed API contract. Run DELIBERATELY:

    python -m tests.contract.update_snapshot

A change to this file is a change to what the consuming application can rely
on. Every regeneration should be accompanied by a D-entry in docs/decisions.md
saying what changed and whether it is backward compatible.
"""
import json
from pathlib import Path

from app.main import app

SNAPSHOT = Path(__file__).with_name("openapi.v1.json")


def render() -> str:
    return json.dumps(app.openapi(), indent=2, sort_keys=True) + "\n"


if __name__ == "__main__":
    SNAPSHOT.write_text(render(), encoding="utf-8")
    print(f"wrote {SNAPSHOT}")
