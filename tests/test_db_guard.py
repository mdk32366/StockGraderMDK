"""Proves each clause of the DB guard by tripping it (KEEL Principle 6).

Every refusal case uses a probe that would PASS if it were called, so a red
here can only come from the clause under test, not from the probe."""
import pytest

from tests.keel_db_guard import (
    CONFIRM_ENV,
    CONFIRM_SENTENCE,
    DISPOSABLE_VERIFIED,
    HERMETIC,
    MAX_DISPOSABLE_ROWS,
    ProbeResult,
    UnsafeDatabaseError,
    check_database_is_disposable,
    require_verified,
)

TUNNEL_TO_PROD = "postgresql://app@localhost:15432/stockgrader"  # what a fly proxy looks like
REMOTE = "postgresql://app@db.internal.example:5432/scratch"


class RecordingProbe:
    def __init__(self, result: ProbeResult | None = None, exc: Exception | None = None):
        self.result = result or ProbeResult(canary_present=True, max_table_rows=0)
        self.exc = exc
        self.calls: list[str] = []

    def __call__(self, url: str) -> ProbeResult:
        self.calls.append(url)
        if self.exc:
            raise self.exc
        return self.result


def confirmed(url: str) -> dict:
    return {"DATABASE_URL": url, CONFIRM_ENV: CONFIRM_SENTENCE}


def test_no_database_url_is_hermetic_and_never_probes():
    probe = RecordingProbe()
    assert check_database_is_disposable({}, probe) == HERMETIC
    assert probe.calls == []


def test_blank_database_url_is_refused():
    with pytest.raises(UnsafeDatabaseError, match="blank"):
        check_database_is_disposable({"DATABASE_URL": "   "}, RecordingProbe())


def test_tunnel_localhost_without_confirmation_is_refused_before_probing():
    """The 4,535-row signature: env file loaded, URL looks local."""
    probe = RecordingProbe()
    with pytest.raises(UnsafeDatabaseError, match=CONFIRM_ENV):
        check_database_is_disposable({"DATABASE_URL": TUNNEL_TO_PROD}, probe)
    assert probe.calls == [], "factor 1 must stop us before the database is touched"


def test_near_miss_confirmation_is_refused():
    env = {"DATABASE_URL": TUNNEL_TO_PROD, CONFIRM_ENV: CONFIRM_SENTENCE.lower()}
    with pytest.raises(UnsafeDatabaseError, match=CONFIRM_ENV):
        check_database_is_disposable(env, RecordingProbe())


def test_missing_canary_is_refused():
    probe = RecordingProbe(ProbeResult(canary_present=False, max_table_rows=0))
    with pytest.raises(UnsafeDatabaseError, match="Canary"):
        check_database_is_disposable(confirmed(TUNNEL_TO_PROD), probe)


def test_row_tripwire_refuses_one_over_the_ceiling():
    probe = RecordingProbe(ProbeResult(True, MAX_DISPOSABLE_ROWS + 1))
    with pytest.raises(UnsafeDatabaseError, match="rows"):
        check_database_is_disposable(confirmed(TUNNEL_TO_PROD), probe)


def test_row_tripwire_allows_exactly_the_ceiling():
    probe = RecordingProbe(ProbeResult(True, MAX_DISPOSABLE_ROWS))
    assert check_database_is_disposable(confirmed(TUNNEL_TO_PROD), probe) == DISPOSABLE_VERIFIED


def test_probe_failure_is_a_refusal_not_a_pass():
    probe = RecordingProbe(exc=ConnectionError("boom-5e1c"))
    with pytest.raises(UnsafeDatabaseError, match="boom-5e1c"):
        check_database_is_disposable(confirmed(TUNNEL_TO_PROD), probe)


def test_hostname_is_not_the_basis_remote_host_passes_on_identity():
    """If a remote hostname with both factors passes, and localhost without them
    fails (above), then location cannot be what the guard decides on."""
    probe = RecordingProbe()
    assert check_database_is_disposable(confirmed(REMOTE), probe) == DISPOSABLE_VERIFIED
    assert probe.calls == [REMOTE]


def test_db_fixture_errors_in_hermetic_mode_rather_than_skipping():
    with pytest.raises(UnsafeDatabaseError):
        require_verified(HERMETIC)
