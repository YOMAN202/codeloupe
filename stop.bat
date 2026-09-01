@echo off
REM Codeloupe stopper (Windows).
REM
REM start.bat runs the backend and frontend detached in the background,
REM so closing that window doesn't stop them -- run this when you're
REM done for the day. It stops exactly the two processes start.bat
REM started (and shows a popup confirming what it did); it's safe to
REM run even if Codeloupe isn't running.

setlocal
set "ROOT=%~dp0"

where powershell >nul 2>nul
if errorlevel 1 (
    echo [Codeloupe] "powershell" was not found on PATH.
    pause
    exit /b 1
)

start "" /min powershell -NoProfile -ExecutionPolicy Bypass -WindowStyle Hidden -File "%ROOT%scripts\stop.ps1"
exit /b 0
