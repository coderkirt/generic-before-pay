# One-command run on Windows.
#   .\start.ps1           -> Docker
#   .\start.ps1 --local   -> local venv
Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"
Set-Location $PSScriptRoot

if (-not (Test-Path .env)) {
    Copy-Item .env.example .env
    Write-Host "Created .env from .env.example (OCR_PROVIDER=mock, so the demo works without a model)."
}

if ($args -contains "--local") {
    Set-Location backend
    if (-not (Test-Path .venv)) {
        python -m venv .venv
    }
    & .\.venv\Scripts\python.exe -m pip install -q -r requirements.txt
    Get-Content ..\.env | ForEach-Object {
        if ($_ -match '^\s*#' -or $_ -notmatch '=') { return }
        $name, $value = $_.Split('=', 2)
        Set-Item -Path "Env:$($name.Trim())" -Value $value.Trim()
    }
    $data = if ($env:DATA_DIR) { $env:DATA_DIR } else { "data" }
    $env:DATA_DIR = "../$data"
    & .\.venv\Scripts\python.exe -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
} else {
    docker compose up --build
}
