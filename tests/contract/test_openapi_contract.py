"""Producer/consumer contract (KEEL: a spec that names a producer and a
consumer names the contract test between them).

The API is consumed by another application. If the live schema drifts from
the committed snapshot, the gate goes red BEFORE the consumer finds out."""
from tests.contract.update_snapshot import SNAPSHOT, render


def test_openapi_matches_committed_contract():
    assert SNAPSHOT.exists(), "contract snapshot missing — run update_snapshot deliberately"
    committed = SNAPSHOT.read_text(encoding="utf-8")
    assert render() == committed, (
        "The API contract changed. If intended: run "
        "`python -m tests.contract.update_snapshot`, commit the diff, and log a D-entry."
    )
