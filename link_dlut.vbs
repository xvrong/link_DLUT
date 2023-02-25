Set oShell = CreateObject ("Wscript.Shell") 
Dim strArgs
strArgs = "cmd /c python path_to_project/link_dlut.py"
oShell.Run strArgs, 0, false