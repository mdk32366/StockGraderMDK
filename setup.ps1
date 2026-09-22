# StockGraderMDK local setup - idempotent. Safe to run any number of times.
#   .\setup.ps1              create/refresh .venv, install deps, run the hermetic suite
#   .\setup.ps1 -SuiteOnly   run the suite against an existing .venv, installing nothing
#
# -SuiteOnly exists so the offline run is a repeatable mode rather than a
# sequence someone has to remember (D-012). The original order said to run this
# script with the network off, but the script installs dependencies, so it could
# not work (F-004). Install once with the network on, then use -SuiteOnly with
# the network off to prove the suite needs no network.
[CmdletBinding()]
param(
    [switch]$SuiteOnly
)
$ErrorActionPreference = "Stop"
Set-Location -Path $PSScriptRoot

# KEEL P5: never run the suite in a shell that has a database armed.
if ($env:DATABASE_URL) {
    Write-Host "DATABASE_URL is set in this shell. The suite's DB guard will refuse to run" -ForegroundColor Yellow
    Write-Host "unless the target is verified disposable. For hermetic runs:  Remove-Item Env:DATABASE_URL" -ForegroundColor Yellow
}

if ($SuiteOnly) {
    # No network, no installs, no venv creation. A missing .venv is a hard error:
    # creating one here would silently defeat D-011.
    if (-not (Test-Path ".venv\Scripts\python.exe")) {
        throw "-SuiteOnly needs an existing .venv. Run .\setup.ps1 once with the network on first. Never create .venv by hand (D-011)."
    }
    Write-Host "Running hermetic suite (-SuiteOnly: no installs) ..."
    & .\.venv\Scripts\python.exe -m pytest -q
    if ($LASTEXITCODE -ne 0) { throw "Suite is RED. Do not push." }
    Write-Host "Suite GREEN." -ForegroundColor Green
    return
}

# Python 3.12 everywhere: local, CI, and the Docker image (D-011). The workstation
# default being 3.11 is F-003; 3.12 installs alongside it without replacing it.
if (-not (Get-Command py -ErrorAction SilentlyContinue)) {
    throw "The 'py' launcher is missing. Install Python 3.12: winget install --id Python.Python.3.12 -e"
}
& py -3.12 --version *> $null
if ($LASTEXITCODE -ne 0) {
    throw "Python 3.12 not found (py -3.12). Install alongside 3.11: winget install --id Python.Python.3.12 -e"
}

if (-not (Test-Path ".venv\Scripts\python.exe")) {
    Write-Host "Creating .venv with Python 3.12 ..."
    py -3.12 -m venv .venv
    if ($LASTEXITCODE -ne 0) { throw "venv creation failed." }
} else {
    Write-Host ".venv already exists - reusing."
}

& .\.venv\Scripts\python.exe -m pip install --upgrade pip --quiet
& .\.venv\Scripts\python.exe -m pip install -r requirements-dev.txt --quiet
if ($LASTEXITCODE -ne 0) { throw "Dependency install failed." }

Write-Host "Running hermetic suite ..."
& .\.venv\Scripts\python.exe -m pytest -q
if ($LASTEXITCODE -ne 0) { throw "Suite is RED. Do not push." }
Write-Host "Suite GREEN." -ForegroundColor Green
