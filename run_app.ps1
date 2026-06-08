# Sunergy Pharma Pro v5.0 — PowerShell Launcher
# Usage: Right-click → "Run with PowerShell"

$projectRoot = Split-Path -Parent $MyInvocation.MyCommand.Definition
Set-Location $projectRoot

$streamlitPath = Join-Path $projectRoot ".venv\Scripts\streamlit.exe"

if (-not (Test-Path $streamlitPath)) {
    Write-Host "[ERROR] Virtual environment not found or streamlit not installed." -ForegroundColor Red
    Write-Host "Please run: python -m venv .venv" -ForegroundColor Yellow
    Write-Host "Then: .venv\Scripts\pip install -r requirements.txt" -ForegroundColor Yellow
    Read-Host "Press Enter to exit"
    exit 1
}

Write-Host "Starting Sunergy Pharma Pro v5.0 ..." -ForegroundColor Green
Write-Host ""

& $streamlitPath "run" "streamlit_app_pro_v5.py"

Read-Host "Press Enter to exit"
