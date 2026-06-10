@echo off
chcp 65001 >nul
echo ==========================================
echo  Maverick-SORT Dashboard v3 Launcher
echo ==========================================
echo.

REM Get the directory where this batch file is located
set "SCRIPT_DIR=%~dp0"
cd /d "%SCRIPT_DIR%"

REM Check if virtual environment exists
if not exist ".venv\Scripts\python.exe" (
    echo [ERROR] Virtual environment not found at .venv\
    echo Please ensure the .venv folder exists in the project directory.
    pause
    exit /b 1
)

REM Check if streamlit_app_v3.py exists
if not exist "streamlit_app_v3.py" (
    echo [ERROR] streamlit_app_v3.py not found in current directory.
    echo Current directory: %CD%
    pause
    exit /b 1
)

REM Check if port 8501 is already in use
netstat -ano | findstr ":8501" | findstr "LISTENING" >nul
if %errorlevel% == 0 (
    echo [WARNING] Port 8501 is already in use.
    echo This may be a previous Streamlit instance still running.
    echo.
    choice /C YN /M "Do you want to kill the existing process and continue"
    if %errorlevel% == 1 (
        for /f "tokens=5" %%a in ('netstat -ano ^| findstr ":8501" ^| findstr "LISTENING"') do (
            echo Killing process PID: %%a
            taskkill /PID %%a /F >nul 2>&1
        )
        timeout /t 2 /nobreak >nul
    ) else (
        echo.
        echo You can try a different port by running manually:
        echo   .venv\Scripts\python.exe -m streamlit run streamlit_app_v3.py --server.port 8502
        pause
        exit /b 0
    )
)

echo [OK] All checks passed. Starting Streamlit dashboard...
echo.

REM Launch Streamlit with the v3 app
.venv\Scripts\python.exe -m streamlit run streamlit_app_v3.py --server.headless true

REM If we get here, Streamlit has exited
echo.
echo Streamlit has stopped.
pause
