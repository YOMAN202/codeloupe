@echo off
REM Codeloupe launcher (Windows).
REM
REM Double-click this and it just works: starts the backend and frontend
REM silently in the background (no terminal windows stay open), waits
REM until the frontend is actually ready, then opens
REM http://localhost:5173/ in your browser automatically.
REM
REM This is a convenience on top of the manual steps in README.md -- it
REM does NOT run "pip install" or "npm install" for you. Do the one-time
REM setup in README.md's "Running it locally" section first; after that,
REM this script (and stop.bat, when you're done) is all you need.
REM
REM All the real logic lives in scripts\start.ps1 -- this file just
REM hands off to it. If anything goes wrong (missing Python/Node, missing
REM dependencies, a server that fails to start), you'll get a clear popup
REM explaining what happened and what to do -- it won't fail silently.
REM
REM Closing this window does NOT stop Codeloupe -- it keeps running in
REM the background. Use stop.bat to stop it.

setlocal
set "ROOT=%~dp0"

where powershell >nul 2>nul
if errorlevel 1 (
    echo [Codeloupe] "powershell" was not found on PATH. This launcher
    echo needs PowerShell, which ships with every supported version of
    echo Windows -- if it's genuinely missing, something unusual is going
    echo on with this PC. Follow the manual setup in README.md instead.
    pause
    exit /b 1
)

REM Launched via "start" as its own detached process (not called
REM directly) so this window doesn't sit around waiting for it --
REM start.ps1 runs hidden in the background and reports any problem
REM itself, as a popup, whenever it happens.
start "" /min powershell -NoProfile -ExecutionPolicy Bypass -WindowStyle Hidden -File "%ROOT%scripts\start.ps1"

exit /b 0
