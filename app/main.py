"""StockGraderMDK API.

Day-one scope is the Keel only: a health check for Fly, and one authenticated
/v1 endpoint so the auth guard and the API contract test have something real
to bite on. No scoring or overlap code exists until its D-entry is ruled.
"""
import os

from fastapi import Depends, FastAPI

from app import __version__
from app.auth import require_api_key

app = FastAPI(
    title="StockGraderMDK",
    version=__version__,
    description="Buy-and-hold suitability scoring for stocks and mutual funds, "
    "and holdings overlap between funds.",
)


@app.get("/healthz", tags=["ops"])
def healthz() -> dict:
    """Unauthenticated liveness check used by Fly.

    Returns the git SHA baked in at build time so the deploy job can prove the
    live service is the commit it just shipped — a green gate and a changed
    service are different claims (PharmFoldMDK lesson 3.4). A commit SHA is
    public on GitHub already; it reveals nothing new."""
    return {"status": "ok", "build": os.environ.get("GIT_SHA", "unknown")}


@app.get("/v1/meta", tags=["v1"], dependencies=[Depends(require_api_key)])
def meta() -> dict:
    """Authenticated service metadata. Proves the /v1 auth path end to end."""
    return {"service": "StockGraderMDK", "version": __version__, "api": "v1"}
