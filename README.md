# StockGraderMDK

Scores stocks and mutual funds on suitability for buying and holding, and
measures holdings overlap between funds. Hosted on Fly.io; exposes a versioned
HTTP API (`/v1`, GET and POST) for other applications.

Built under **KEEL V10 — The Build-First Pattern.** This README is a greeting,
not a container. Everything else lives where you would look for it:

| Question | Document |
|---|---|
| What am I looking at? | [docs/architecture.md](docs/architecture.md) |
| Why is it like this? | [docs/decisions.md](docs/decisions.md) |
| How do we know? | [docs/findings.md](docs/findings.md) |
| What would catch it if it broke? | [docs/testplan.md](docs/testplan.md) |
| What are we taking for granted? | [docs/assumptions.md](docs/assumptions.md) |

## Run it locally (Windows / PowerShell)

```powershell
.\setup.ps1
```

Idempotent, and **the only sanctioned way to create `.venv`** (D-011). A venv
made by hand on this workstation gets the wrong Python (F-005). Creates `.venv`, installs pinned dependencies, runs the hermetic
suite. No database, no network, no secrets required.

## The API today

| Method | Path | Auth | Purpose |
|---|---|---|---|
| GET | `/healthz` | none | Liveness + deployed build SHA |
| GET | `/v1/meta` | `X-API-Key` | Service identity; proves the auth path |

Interactive docs at `/docs` once deployed. The committed contract is
`tests/contract/openapi.v1.json`; the gate fails if the live schema drifts from it.
Scoring and overlap endpoints arrive only after their D-entries are ruled.
