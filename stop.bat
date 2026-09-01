@echo off
REM Codeloupe stopper (Windows).
REM
REM start.bat's backend and frontend run completely invisibly (no
REM window at all), tracked only by the PID files it writes under
REM .codeloupe-run\ -- run this when you're done for the day, since
REM there's no window to close them from. Safe to run even if Codeloupe
REM isn't running, or if only one of the two is up.

setlocal
set "RUNDIR=%~dp0.codeloupe-run"

echo [Codeloupe] Stopping backend and frontend...

if exist "%RUNDIR%\backend.pid" (
    for /f "usebackq delims=" %%P in ("%RUNDIR%\backend.pid") do taskkill /PID %%P /T /F >nul 2>nul
    del "%RUNDIR%\backend.pid" >nul 2>nul
)

if exist "%RUNDIR%\frontend.pid" (
    for /f "usebackq delims=" %%P in ("%RUNDIR%\frontend.pid") do taskkill /PID %%P /T /F >nul 2>nul
    del "%RUNDIR%\frontend.pid" >nul 2>nul
)

echo [Codeloupe] Done. (If either wasn't running, that's fine -- nothing
echo to do there.)

timeout /t 2 /nobreak >nul
