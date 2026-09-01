' Codeloupe hidden-process helper (Windows).
'
' Runs one command with NO visible window at all (not minimized, not
' hidden-but-in-the-taskbar -- no window is created in the first place),
' in the given working directory, with its output redirected to a log
' file (since there's no window left to read output from directly), and
' writes the launched process's PID to a file so stop.bat can find and
' stop it again later.
'
' This uses WScript.Shell.Exec, the standard, long-established Windows
' Script Host mechanism for running a console command invisibly -- it's
' been part of Windows since Windows 98/2000, so there's nothing extra
' to install. It's called from start.bat, not meant to be run directly:
'
'   wscript run-hidden.vbs <workdir> <command> <logfile> <pidfile>

workDir = WScript.Arguments(0)
command = WScript.Arguments(1)
logFile = WScript.Arguments(2)
pidFile = WScript.Arguments(3)

Set objShell = CreateObject("WScript.Shell")
objShell.CurrentDirectory = workDir

' The redirect is part of the command line handed to this inner cmd.exe,
' not something WScript.Shell does itself -- cmd.exe is what actually
' understands "> logfile 2>&1". This also means nothing meaningful ever
' flows back through Exec's own stdout pipe (only the inner command's
' real output would, and that's already been redirected away), so there
' is no risk of that pipe filling up and stalling anything even though
' this script never reads from it.
fullCommand = "cmd.exe /c " & command & " > """ & logFile & """ 2>&1"

Set objExec = objShell.Exec(fullCommand)

Set objFSO = CreateObject("Scripting.FileSystemObject")
Set objPidFile = objFSO.CreateTextFile(pidFile, True)
objPidFile.WriteLine objExec.ProcessID
objPidFile.Close
