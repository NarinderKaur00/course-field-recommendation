# Launch the EduPath portal locally.
# Reads your own settings from portal\.env (copy .env.example to .env first).
#   Run from the project root:  .\portal\run_local.ps1
$ErrorActionPreference = "Stop"
$py = "C:\Users\HP\co544venv\Scripts\python.exe"
$here = Split-Path -Parent $MyInvocation.MyCommand.Path

if (-not (Test-Path (Join-Path $here ".env"))) {
    Write-Host "No .env found — copying .env.example to .env (fill in your values)." -ForegroundColor Yellow
    Copy-Item (Join-Path $here ".env.example") (Join-Path $here ".env")
}

Write-Host "Starting portal at http://127.0.0.1:5000  (Ctrl+C to stop)" -ForegroundColor Green
& $py (Join-Path $here "app.py")
