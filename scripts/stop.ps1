<#
  Codeloupe background stopper (Windows).

  Invoked by ..\stop.bat. Stops exactly the backend/frontend processes
  that start.bat started (tracked by PID files in .codeloupe-run\),
  including any child processes they spawned (e.g. the node.exe/vite
  process underneath npm). Safe to run even if nothing is running, or
  if only one of the two servers is up.
#>

$ErrorActionPreference = 'Continue'
Add-Type -AssemblyName System.Windows.Forms | Out-Null

$Root = Split-Path -Parent $PSScriptRoot
$RunDir = Join-Path $Root '.codeloupe-run'

function Stop-Tracked($name, $pidFile, $commandLineHint) {
    if (-not (Test-Path $pidFile)) {
        return "$name`: not running (no record of it)."
    }
    $procId = (Get-Content $pidFile -ErrorAction SilentlyContinue | Select-Object -First 1)
    Remove-Item $pidFile -ErrorAction SilentlyContinue
    if (-not $procId) {
        return "$name`: no PID on record."
    }
    $proc = Get-Process -Id $procId -ErrorAction SilentlyContinue
    if (-not $proc) {
        return "$name`: already stopped."
    }
    # Safety check: confirm the PID still points at the process we
    # actually started (by inspecting its command line, not just its
    # name -- the frontend PID is a cmd.exe host, so name alone isn't
    # specific enough) before killing anything. Guards against a
    # stale PID having been reused by an unrelated process since.
    $cmdLine = ''
    try {
        $cim = Get-CimInstance Win32_Process -Filter "ProcessId=$procId" -ErrorAction SilentlyContinue
        if ($cim) { $cmdLine = $cim.CommandLine }
    } catch { }
    if ($cmdLine -and ($cmdLine -notlike "*$commandLineHint*")) {
        return "$name`: PID $procId no longer looks like Codeloupe's $name (reused PID) -- left alone."
    }
    # /T kills the whole process tree (e.g. npm's node.exe child), not
    # just the top-level process Start-Process handed back.
    taskkill /PID $procId /T /F 2>$null | Out-Null
    return "$name`: stopped."
}

$results = @()
$results += Stop-Tracked 'Backend'  (Join-Path $RunDir 'backend.pid')  'app.py'
$results += Stop-Tracked 'Frontend' (Join-Path $RunDir 'frontend.pid') 'npm run dev'

$summary = $results -join "`r`n"

[System.Windows.Forms.MessageBox]::Show(
    $summary,
    'Codeloupe - Stopped',
    [System.Windows.Forms.MessageBoxButtons]::OK,
    [System.Windows.Forms.MessageBoxIcon]::Information
) | Out-Null
