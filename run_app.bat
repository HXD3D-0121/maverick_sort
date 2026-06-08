@echo off
chcp 65001 > nul
cd /d "%~dp0"

REM Check if .venv exists
if not exist ".venv\Scripts\streamlit.exe" (
    echo [ERROR] Virtual environment not found or streamlit not installed.
    echo Please run: python -m venv .venv
    echo Then: .venv\Scripts\pip install -r requirements.txt
    pause
    exit /b 1
)

echo Starting Sunergy Pharma Pro v5.0 ...
echo.
.venv\Scripts\streamlit.exe run streamlit_app_pro_v5.py

pause
