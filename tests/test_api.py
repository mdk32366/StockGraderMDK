"""Auth guard proofs and the health check. Each refusal is a distinct test."""
import pytest
from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_healthz_needs_no_key_and_reports_unknown_build_locally(monkeypatch):
    monkeypatch.delenv("GIT_SHA", raising=False)
    r = client.get("/healthz")
    assert r.status_code == 200
    assert r.json() == {"status": "ok", "build": "unknown"}


def test_healthz_reports_the_baked_build_sha(monkeypatch):
    monkeypatch.setenv("GIT_SHA", "c0ffee5ha")  # distinctive value
    assert client.get("/healthz").json()["build"] == "c0ffee5ha"


def test_meta_without_key_is_401(api_key):
    assert client.get("/v1/meta").status_code == 401


def test_meta_with_wrong_key_is_401(api_key):
    r = client.get("/v1/meta", headers={"X-API-Key": api_key + "-wrong"})
    assert r.status_code == 401


def test_meta_with_right_key_returns_service_identity(api_key):
    r = client.get("/v1/meta", headers={"X-API-Key": api_key})
    assert r.status_code == 200
    assert r.json()["service"] == "StockGraderMDK"
    assert r.json()["api"] == "v1"


@pytest.mark.parametrize("configured", [None, ""])
def test_unconfigured_server_fails_closed(monkeypatch, configured):
    """Direction check: a missing server key must never mean 'let everyone in'."""
    if configured is None:
        monkeypatch.delenv("STOCKGRADER_API_KEY", raising=False)
    else:
        monkeypatch.setenv("STOCKGRADER_API_KEY", configured)
    r = client.get("/v1/meta", headers={"X-API-Key": ""})
    assert r.status_code == 503
