@echo off
REM Codeloupe launcher (Windows).
REM
REM Double-click this. It checks your setup is in place, starts the
REM backend and frontend completely invisibly (no window at all, not
REM even minimized), waits until the frontend is actually responding to
REM HTTP requests (not a fixed timer), then opens http://localhost:5173/
REM automatically and closes itself. The backend/frontend keep running
REM in the background until you run stop.bat -- since there's no window
REM for either of them, that's the only way to stop them.
REM
REM This is a convenience on top of the manual steps in README.md -- it
REM does NOT run "pip install" or "npm install" for you. Do that
REM one-time setup first; after that, this script (and stop.bat) is all
REM you need for every subsequent start.
REM
REM Plain batch plus one small VBScript helper (scripts\run-hidden.vbs)
REM for the invisible part -- Windows Script Host's WshShell.Exec is the
REM standard, decades-old way to run a console command with no window,
REM built into Windows already. No PowerShell involved: an earlier
REM version of this launcher used PowerShell for the same job and failed
REM silently on a real machine, which is why it isn't used here. Backend
REM and frontend output goes to .codeloupe-run\*.log, since there's no
REM window left to read it from directly if something goes wrong.

setlocal
set "ROOT=%~dp0"
set "RUNDIR=%ROOT%.codeloupe-run"
if not exist "%RUNDIR%" mkdir "%RUNDIR%"
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

where wscript >nul 2>nul
if errorlevel 1 (
    echo [Codeloupe] "wscript" was not found on PATH. It's part of
    echo Windows Script Host, which ships with Windows 10/11 by default --
    echo if it's been disabled on this PC, re-enable it and try again.
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
REM run. Runs completely invisibly via scripts\run-hidden.vbs; its PID
REM is written to backend.pid (for stop.bat) and its output goes to
REM backend.log (since there's no window to read it from directly).
curl -f -s -o nul -m 2 http://127.0.0.1:5001/api/health
if errorlevel 1 (
    echo [Codeloupe] Starting backend...
    wscript.exe //nologo "%ROOT%scripts\run-hidden.vbs" "%ROOT%backend" "python app.py" "%RUNDIR%\backend.log" "%RUNDIR%\backend.pid"
) else (
    echo [Codeloupe] Backend already running.
)

REM Start the frontend the same way, unless it's already up. --strictPort
REM makes Vite fail loudly instead of silently moving to 5174+ if 5173 is
REM taken by something else, so a real port conflict shows up clearly in
REM frontend.log rather than a confusing mismatch. Polling "localhost"
REM here (not 127.0.0.1) is deliberate: Vite listens on [::1] (IPv6
REM localhost) by default, which "localhost" resolves to on Windows but
REM the literal 127.0.0.1 never matches.
curl -f -s -o nul -m 2 http://localhost:5173/
if errorlevel 1 (
    echo [Codeloupe] Starting frontend...
    wscript.exe //nologo "%ROOT%scripts\run-hidden.vbs" "%ROOT%frontend" "npm run dev -- --port 5173 --strictPort" "%RUNDIR%\frontend.log" "%RUNDIR%\frontend.pid"
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
echo Check .codeloupe-run\backend.log for the actual error (for example,
echo a port already in use by something else, or a missing dependency).
pause
exit /b 1

:backendready
echo [Codeloupe] Backend is up.

echo [Codeloupe] Waiting for the frontend to respond...
set tries=0
:waitfrontend
curl -f -s -o nul -m 2 http://localhost:5173/
if not errorlevel 1 goto frontendready
set /a tries=tries+1
if %tries% GEQ 45 goto frontendfailed
timeout /t 1 /nobreak >nul
goto waitfrontend

:frontendfailed
echo.
echo [Codeloupe] The frontend didn't respond within 45 seconds.
echo Check .codeloupe-run\frontend.log for the actual error (for example,
echo a port already in use by something else, or a dependency problem).
pause
exit /b 1

:frontendready
echo [Codeloupe] Frontend is up.
echo [Codeloupe] Opening http://localhost:5173/ ...

REM explorer.exe (not cmd's own "start URL") is deliberate: explorer.exe
REM is a real, directly-executable program, so launching it is a normal,
REM independent process start -- unlike "start <bare URL>", which asks
REM cmd.exe itself to hand the URL off to the shell's URL association,
REM a path that depends on the calling console session in a way that's
REM known to occasionally get dropped on some Windows setups, especially
REM when the calling script exits immediately after. explorer.exe is the
REM standard, well-documented fix for exactly that failure pattern.
start "" explorer.exe "http://localhost:5173/"

REM Also deliberate: give the handoff a moment to actually happen before
REM this window (and the console session that issued it) closes, rather
REM than closing on the same instant the request was made.
timeout /t 2 /nobreak >nul

REM Plain "exit" (not "exit /b"): /b only returns from this script to
REM whatever invoked it -- closing a freshly-spawned window if that's
REM double-click, but leaving an existing terminal window open on its
REM prompt if start.bat was run from one. Plain "exit" ends the current
REM command-processor session outright either way, which is what
REM actually guarantees the window itself closes here.
exit 0
