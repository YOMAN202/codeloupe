@echo off
REM Codeloupe launcher (Windows).
REM
REM Double-click this. It checks your setup is in place, starts the
REM backend and frontend each in their own MINIMIZED window (so they're
REM out of your way in the taskbar, not full windows on your screen),
REM waits until the frontend is actually responding to HTTP requests
REM (not a fixed timer), then opens http://localhost:5173/ automatically.
REM This window closes itself when that's done; the backend/frontend
REM windows keep running until you run stop.bat.
REM
REM This is a convenience on top of the manual steps in README.md -- it
REM does NOT run "pip install" or "npm install" for you. Do that
REM one-time setup first; after that, this script (and stop.bat) is all
REM you need for every subsequent start.
REM
REM Deliberately plain batch, no PowerShell/hidden-process tricks: this
REM replaced an earlier version that used those, which turned out to
REM fail silently on some real Windows setups. This is simpler and uses
REM only well-worn Windows batch primitives (start /min, curl, taskkill
REM by window title), which is worth the trade-off of "minimized" over
REM "fully invisible" windows.

setlocal
set "ROOT=%~dp0"
title Codeloupe Launcher

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

where curl >nul 2>nul
if errorlevel 1 (
    echo [Codeloupe] "curl" was not found on PATH. curl ships with
    echo Windows 10/11 by default, so this is unusual -- if you're on an
    echo older or customized Windows install without it, install curl
    echo and try again.
    pause
    exit /b 1
)

python -c "import flask, flask_cors" >nul 2>nul
if errorlevel 1 (
    echo [Codeloupe] Backend Python packages aren't installed yet. Run:
    echo   cd backend
    echo   pip install -r requirements.txt
    echo See README.md for the full first-time setup.
    pause
    exit /b 1
)

if not exist "%ROOT%frontend\node_modules" (
    echo [Codeloupe] Frontend dependencies aren't installed yet. Run:
    echo   cd frontend
    echo   npm install
    echo See README.md for the full first-time setup.
    pause
    exit /b 1
)

REM Create the database on a genuine first run only -- never touched
REM again afterwards, so your progress/attempts/history are never wiped.
if not exist "%ROOT%backend\db\traceviz.db" (
    echo [Codeloupe] Setting up the database for the first time...
    pushd "%ROOT%backend"
    python db\init_db.py
    if errorlevel 1 (
        popd
        echo [Codeloupe] Database setup failed -- see the error above.
        pause
        exit /b 1
    )
    popd
)

REM Start the backend, unless it's already up from a previous start.bat
REM run. This is deliberately the exact "cd /d ... && python app.py"
REM invocation used manually (and in the very first version of this
REM launcher) -- same command, just handed to "start /min" instead of
REM typed at a prompt, so there's nothing new here to behave
REM differently. Uses /k (not /c): if python crashes right away, /k
REM leaves the window open with the error still on screen instead of
REM vanishing before anyone can read it -- open the minimized "Codeloupe
REM Backend" window from the taskbar to see it.
curl -f -s -o nul -m 2 http://127.0.0.1:5001/api/health
if errorlevel 1 (
    echo [Codeloupe] Starting backend...
    start "Codeloupe Backend" /min cmd /k "cd /d "%ROOT%backend" && python app.py"
) else (
    echo [Codeloupe] Backend already running.
)

REM Start the frontend, unless it's already up. --strictPort makes Vite
REM fail loudly instead of silently moving to 5174+ if 5173 is taken by
REM something else, so a real port conflict shows up as a clear error
REM in the "Codeloupe Frontend" window rather than a confusing mismatch.
curl -f -s -o nul -m 2 http://127.0.0.1:5173/
if errorlevel 1 (
    echo [Codeloupe] Starting frontend...
    start "Codeloupe Frontend" /min cmd /k "cd /d "%ROOT%frontend" && npm run dev -- --port 5173 --strictPort"
) else (
    echo [Codeloupe] Frontend already running.
)

echo [Codeloupe] Waiting for the backend to respond...
set tries=0
:waitbackend
curl -f -s -o nul -m 2 http://127.0.0.1:5001/api/health
if not errorlevel 1 goto backendready
set /a tries=tries+1
if %tries% GEQ 30 goto backendfailed
timeout /t 1 /nobreak >nul
goto waitbackend

:backendfailed
echo.
echo [Codeloupe] The backend didn't respond within 30 seconds.
echo If a "Codeloupe Backend" window is minimized in your taskbar, open
echo it to see the actual error (for example, a port already in use by
echo something else, or a missing dependency).
pause
exit /b 1

:backendready
echo [Codeloupe] Backend is up.

echo [Codeloupe] Waiting for the frontend to respond...
set tries=0
:waitfrontend
curl -f -s -o nul -m 2 http://127.0.0.1:5173/
if not errorlevel 1 goto frontendready
set /a tries=tries+1
if %tries% GEQ 45 goto frontendfailed
timeout /t 1 /nobreak >nul
goto waitfrontend

:frontendfailed
echo.
echo [Codeloupe] The frontend didn't respond within 45 seconds.
echo If a "Codeloupe Frontend" window is minimized in your taskbar, open
echo it to see the actual error (for example, a port already in use by
echo something else, or a dependency problem).
pause
exit /b 1

:frontendready
echo [Codeloupe] Frontend is up.
echo [Codeloupe] Opening http://localhost:5173/ ...
start "" http://localhost:5173/

exit /b 0
