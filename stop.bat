@echo off
REM Codeloupe stopper (Windows).
REM
REM start.bat's backend/frontend windows (minimized, titled "Codeloupe
REM Backend" / "Codeloupe Frontend") keep running after start.bat itself
REM closes, so run this when you're done for the day. Safe to run even
REM if Codeloupe isn't running, or if only one of the two is up.

echo [Codeloupe] Stopping backend and frontend...

taskkill /FI "WINDOWTITLE eq Codeloupe Backend*" /T /F >nul 2>nul
taskkill /FI "WINDOWTITLE eq Codeloupe Frontend*" /T /F >nul 2>nul

echo [Codeloupe] Done. (If either wasn't running, that's fine -- nothing
echo to do there.)

timeout /t 2 /nobreak >nul
