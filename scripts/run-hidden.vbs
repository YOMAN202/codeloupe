' Codeloupe hidden-process helper (Windows).
'
' Runs one command with NO visible window at all (not minimized, not
' hidden-but-in-the-taskbar -- no window is created in the first place),
' in the given working directory, with its output redirected to a log
' file (since there's no window left to read output from directly), and
' writes the launched process's PID to a file so stop.bat can find and
' stop it again later.
'
' Uses WshShell.Run with an explicit hidden window style (0 = SW_HIDE) --
' a direct, unambiguous instruction to Windows not to create a window at
' all. An earlier version of this script used WshShell.Exec instead,
' which turned out to not reliably guarantee a hidden window in every
' situation; .Run's explicit window-style argument is the more direct,
' dependable way to get true invisibility. The trade-off is that .Run
' doesn't hand back a process ID the way .Exec does, so the ID is looked
' up afterward instead, by matching the distinctive command line via a
' plain WMI query (a read-only lookup of an already-running process,
' not a WMI-based launch, so it doesn't carry the environment-inheritance
' risk that launching a process through WMI can).
'
' Called from start.bat with exactly 5 arguments; not meant to be run
' directly:
'
'   wscript run-hidden.vbs <workdir> <command> <logfile> <pidfile> <matchtext>
'
' <matchtext> is a short, distinctive substring of <command> (e.g.
' "app.py") used to find the right process afterward -- it needs to be
' unique enough that no unrelated cmd.exe window on the system would
' also match it.
'
' Running it any other way (double-clicking it in Explorer, or from a
' command line without all 5 arguments) shows a message explaining that,
' instead of a raw "Subscript out of range" runtime error.

If WScript.Arguments.Count < 5 Then
    WScript.Echo "run-hidden.vbs needs 5 arguments -- <workdir> <command> <logfile> <pidfile> <matchtext>" & vbCrLf & _
        "-- and is meant to be run by start.bat, not directly." & vbCrLf & vbCrLf & _
        "Got " & WScript.Arguments.Count & " argument(s)."
    WScript.Quit 1
End If

workDir = WScript.Arguments(0)
command = WScript.Arguments(1)
logFile = WScript.Arguments(2)
pidFile = WScript.Arguments(3)
matchText = WScript.Arguments(4)

Set objShell = CreateObject("WScript.Shell")
objShell.CurrentDirectory = workDir

' The redirect is part of the command line handed to this inner cmd.exe,
' not something WScript.Shell does itself -- cmd.exe is what actually
' understands "> logfile 2>&1".
fullCommand = "cmd.exe /c " & command & " > """ & logFile & """ 2>&1"

' 0 = SW_HIDE (no window at all), False = don't wait for it to finish --
' this call returns immediately once the process has been started.
objShell.Run fullCommand, 0, False

' Look up the PID of the cmd.exe we just started by matching its command
' line -- a short retry loop since it can take a brief moment to become
' queryable right after starting.
Set objWMI = GetObject("winmgmts:\\.\root\cimv2")
foundPid = 0
For attempt = 1 To 30
    Set colProcesses = objWMI.ExecQuery( _
        "Select ProcessId from Win32_Process Where Name='cmd.exe' and CommandLine Like '%" & matchText & "%'")
    For Each objProcess In colProcesses
        foundPid = objProcess.ProcessId
    Next
    If foundPid <> 0 Then Exit For
    WScript.Sleep 100
Next

Set objFSO = CreateObject("Scripting.FileSystemObject")
Set objPidFile = objFSO.CreateTextFile(pidFile, True)
objPidFile.WriteLine foundPid
objPidFile.Close
