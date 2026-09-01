@echo off
REM Codeloupe convenience launcher (Windows).
REM
REM Starts the backend and frontend each in their own window, then opens
REM the app in your browser. This is a convenience on top of the manual
REM steps in README.md -- it does NOT install dependencies or initialize
REM the database for you. Run the one-time setup in README.md's "Running
REM it locally" section first (pip install, npm install, db/init_db.py);
REM after that, this script is all you need for every subsequent start.
REM
REM To stop Codeloupe: close the two windows this opens (or press Ctrl+C
REM inside each one).

setlocal
set "ROOT=%~dp0"

where python >nul 2>nul
if errorlevel 1 (
    echo [Codeloupe] "python" was not found on PATH. Install Python 3.11+
    echo from https://python.org and make sure "Add python.exe to PATH"
    echo was checked during setup, then try again.
    pause
    exit /b 1
)

where npm >nul 2>nul
if errorlevel 1 (
    echo [Codeloupe] "npm" was not found on PATH. Install Node.js 18+
    echo from https://nodejs.org, then try again.
    pause
    exit /b 1
)

if not exist "%ROOT%backend\db\traceviz.db" (
    echo [Codeloupe] No database found yet. Run the one-time setup first:
    echo   cd backend
    echo   pip install -r requirements.txt
    echo   python db\init_db.py
    echo See README.md for the full first-time setup.
    pause
    exit /b 1
)

if not exist "%ROOT%frontend\node_modules" (
    echo [Codeloupe] Frontend dependencies not installed yet. Run first:
    echo   cd frontend
    echo   npm install
    echo See README.md for the full first-time setup.
    pause
    exit /b 1
)

echo [Codeloupe] Starting backend (http://127.0.0.1:5001) ...
start "Codeloupe Backend" cmd /k "cd /d "%ROOT%backend" && python app.py"

echo [Codeloupe] Starting frontend (http://127.0.0.1:5173) ...
start "Codeloupe Frontend" cmd /k "cd /d "%ROOT%frontend" && npm run dev"

echo [Codeloupe] Waiting for the servers to come up...
timeout /t 6 /nobreak >nul

echo [Codeloupe] Opening http://127.0.0.1:5173 in your browser ...
start http://127.0.0.1:5173

echo.
echo Codeloupe is running in the two new windows that just opened
echo ("Codeloupe Backend" and "Codeloupe Frontend"). Leave them open
echo while you use the app. To stop, close those two windows (or press
echo Ctrl+C inside each one).
