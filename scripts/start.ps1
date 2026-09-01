<#
  Codeloupe background launcher (Windows).

  Invoked by ..\start.bat -- not meant to be double-clicked directly.
  Does the actual work of a "double-click and it just works" start:

    1. Checks python/npm are on PATH, and that setup has been done
       (backend packages importable, frontend node_modules present,
       database file exists -- auto-creating the database only, since
       that's a safe, idempotent, one-time step; it deliberately does
       NOT run "pip install"/"npm install" for you, since those are
       slower, need network access, and are best done once, on
       purpose, by the person -- see README.md).
    2. If the backend/frontend already appear to be running (from a
       previous start), leaves them alone instead of erroring out on
       a port conflict -- so double-clicking start.bat again is safe.
    3. Otherwise starts them as detached background processes with no
       visible console window, with their output captured to log
       files under .codeloupe-run\ instead of a terminal.
    4. Polls the real health/readiness of each server (not a fixed
       sleep) and only opens the browser once both actually respond.
    5. On any failure, shows a native Windows message box (not a
       console window that can vanish) with a clear explanation and,
       where useful, the last lines of the relevant log file.

  Because the servers are started detached, closing this script (or
  the start.bat window that launched it) does not stop them. Use
  stop.bat when you're done for the day.
#>

$ErrorActionPreference = 'Stop'
Add-Type -AssemblyName System.Windows.Forms | Out-Null

$Root = Split-Path -Parent $PSScriptRoot
$RunDir = Join-Path $Root '.codeloupe-run'
if (-not (Test-Path $RunDir)) {
    New-Item -ItemType Directory -Path $RunDir | Out-Null
}

$BackendPort = 5001
$FrontendPort = 5173
$BackendHealthUrl = "http://127.0.0.1:$BackendPort/api/health"
$FrontendUrl = "http://127.0.0.1:$FrontendPort/"

function Show-Error($title, $message) {
    [System.Windows.Forms.MessageBox]::Show(
        $message,
        "Codeloupe - $title",
        [System.Windows.Forms.MessageBoxButtons]::OK,
        [System.Windows.Forms.MessageBoxIcon]::Error
    ) | Out-Null
}

function Test-UrlUp($url) {
    try {
        $resp = Invoke-WebRequest -Uri $url -UseBasicParsing -TimeoutSec 2
        return $resp.StatusCode -ge 200 -and $resp.StatusCode -lt 500
    } catch {
        return $false
    }
}

function Get-LogTail($path, $lines = 15) {
    if (Test-Path $path) {
        $content = Get-Content -Path $path -Tail $lines -ErrorAction SilentlyContinue
        if ($content) { return ($content -join "`r`n") }
    }
    return '(no output captured)'
}

# Everything below is wrapped in one big try/catch: if anything throws
# that none of the specific checks below anticipated (a permissions
# issue, antivirus interference, whatever), it still surfaces as a
# clear popup instead of vanishing or dumping a raw stack trace.
try {

# ---------------------------------------------------------------------
# 1. Prerequisite checks
# ---------------------------------------------------------------------

$pythonCmd = Get-Command python -ErrorAction SilentlyContinue
if (-not $pythonCmd) {
    Show-Error 'Python not found' @"
"python" was not found on PATH.

Install Python 3.11+ from https://python.org and make sure "Add
python.exe to PATH" is checked during setup, then try again.
"@
    exit 1
}

$npmCmd = Get-Command npm -ErrorAction SilentlyContinue
if (-not $npmCmd) {
    Show-Error 'Node.js not found' @"
"npm" was not found on PATH.

Install Node.js 18+ from https://nodejs.org, then try again.
"@
    exit 1
}

# Backend Python packages installed?
& $pythonCmd.Source -c "import flask, flask_cors" 2>$null
if ($LASTEXITCODE -ne 0) {
    Show-Error 'Backend packages missing' @"
Backend Python packages aren't installed yet.

Open a terminal and run:
  cd "$Root\backend"
  pip install -r requirements.txt

Then run start.bat again.
"@
    exit 1
}

# Frontend packages installed?
$nodeModules = Join-Path $Root 'frontend\node_modules'
if (-not (Test-Path $nodeModules)) {
    Show-Error 'Frontend dependencies missing' @"
Frontend dependencies aren't installed yet.

Open a terminal and run:
  cd "$Root\frontend"
  npm install

Then run start.bat again.
"@
    exit 1
}

# Database: create it on first run only (never touch it if it already
# exists, so your progress/attempts/history are never wiped).
$dbPath = Join-Path $Root 'backend\db\traceviz.db'
if (-not (Test-Path $dbPath)) {
    $initLog = Join-Path $RunDir 'db-init.log'
    $p = Start-Process -FilePath $pythonCmd.Source -ArgumentList 'db\init_db.py' `
        -WorkingDirectory (Join-Path $Root 'backend') `
        -WindowStyle Hidden -Wait -PassThru `
        -RedirectStandardOutput $initLog -RedirectStandardError "$initLog.err"
    if ($p.ExitCode -ne 0) {
        $tail = Get-LogTail "$initLog.err"
        Show-Error 'Database setup failed' @"
Setting up the database (backend\db\init_db.py) failed.

Last output:
$tail

Full log: $initLog.err
"@
        exit 1
    }
}

# ---------------------------------------------------------------------
# 2 & 3. Start backend/frontend as hidden, detached processes -- but
#         only if they aren't already up from a previous start.
# ---------------------------------------------------------------------

$backendAlreadyUp = Test-UrlUp $BackendHealthUrl
$frontendAlreadyUp = Test-UrlUp $FrontendUrl

if (-not $backendAlreadyUp) {
    $env:FLASK_DEBUG = '0'   # single process, no reloader child, more
                             # predictable for an unattended background run
    $env:PORT = "$BackendPort"
    $outLog = Join-Path $RunDir 'backend.out.log'
    $errLog = Join-Path $RunDir 'backend.err.log'
    $backendProc = Start-Process -FilePath $pythonCmd.Source -ArgumentList 'app.py' `
        -WorkingDirectory (Join-Path $Root 'backend') `
        -WindowStyle Hidden -PassThru `
        -RedirectStandardOutput $outLog -RedirectStandardError $errLog
    $backendProc.Id | Out-File -FilePath (Join-Path $RunDir 'backend.pid') -Encoding ascii
}

if (-not $frontendAlreadyUp) {
    $outLog = Join-Path $RunDir 'frontend.out.log'
    $errLog = Join-Path $RunDir 'frontend.err.log'
    # npm on Windows is a .cmd shim, not a directly-executable .exe, so
    # it's launched through cmd.exe /c rather than as FilePath directly
    # -- the reliable pattern when output also needs to be redirected.
    $npmArgs = "/c `"npm run dev -- --port $FrontendPort --strictPort`""
    $frontendProc = Start-Process -FilePath 'cmd.exe' -ArgumentList $npmArgs `
        -WorkingDirectory (Join-Path $Root 'frontend') `
        -WindowStyle Hidden -PassThru `
        -RedirectStandardOutput $outLog -RedirectStandardError $errLog
    $frontendProc.Id | Out-File -FilePath (Join-Path $RunDir 'frontend.pid') -Encoding ascii
}

# ---------------------------------------------------------------------
# 4. Poll for real readiness (not a fixed sleep)
# ---------------------------------------------------------------------

function Wait-ForUrl($url, $timeoutSec, $proc) {
    $deadline = (Get-Date).AddSeconds($timeoutSec)
    while ((Get-Date) -lt $deadline) {
        if (Test-UrlUp $url) { return $true }
        if ($proc -and $proc.HasExited) { return $false }
        Start-Sleep -Milliseconds 500
    }
    return $false
}

$backendReady = Wait-ForUrl -url $BackendHealthUrl -timeoutSec 30 -proc $backendProc
if (-not $backendReady) {
    $tail = Get-LogTail (Join-Path $RunDir 'backend.err.log')
    Show-Error 'Backend did not start' @"
The backend didn't respond at $BackendHealthUrl within 30 seconds.

Last output from backend.err.log:
$tail

Full logs are in: $RunDir
"@
    exit 1
}

$frontendReady = Wait-ForUrl -url $FrontendUrl -timeoutSec 45 -proc $frontendProc
if (-not $frontendReady) {
    $tail = Get-LogTail (Join-Path $RunDir 'frontend.err.log')
    Show-Error 'Frontend did not start' @"
The frontend didn't respond at $FrontendUrl within 45 seconds.

Last output from frontend.err.log:
$tail

Full logs are in: $RunDir
"@
    exit 1
}

# ---------------------------------------------------------------------
# 5. Open the app
# ---------------------------------------------------------------------
#
# Open exactly what was asked for (localhost, not the 127.0.0.1 used
# above for polling). PowerShell's own "Start-Process <url>" relies on
# .NET's ShellExecute path, which -- from a hidden, console-less
# background process like this one -- can silently no-op on some
# Windows setups instead of throwing, so nothing shows up and nothing
# is left to catch. cmd.exe's built-in "start" is the same mechanism
# the original, simpler version of this launcher used successfully, so
# it's tried first; Start-Process is kept as a fallback in case cmd.exe
# itself is ever unavailable. If neither manages it, that's reported
# instead of just doing nothing.

$FrontendOpenUrl = "http://localhost:$FrontendPort/"
$opened = $false

try {
    # The empty "" is deliberate -- it's the window title "start"
    # expects as its first argument so it doesn't mistake the quoted
    # URL that follows for one.
    $openArgs = "/c start `"`" `"$FrontendOpenUrl`""
    $openProc = Start-Process -FilePath 'cmd.exe' -ArgumentList $openArgs -WindowStyle Hidden -PassThru
    $openProc.WaitForExit(5000) | Out-Null
    if ($openProc.HasExited -and $openProc.ExitCode -eq 0) { $opened = $true }
} catch { }

if (-not $opened) {
    try {
        Start-Process $FrontendOpenUrl | Out-Null
        $opened = $true
    } catch { }
}

if (-not $opened) {
    Show-Error 'Codeloupe is ready' @"
Codeloupe is up and running at $FrontendOpenUrl, but this launcher
wasn't able to open it in your browser automatically this time.

Open that address yourself -- the app is ready and waiting.
"@
}

} catch {
    Show-Error 'Unexpected error' @"
Something unexpected went wrong while starting Codeloupe:

$($_.Exception.Message)

Logs (if any were written yet) are in: $RunDir
"@
    exit 1
}
