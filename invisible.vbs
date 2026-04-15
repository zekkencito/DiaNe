Set WshShell = CreateObject("WScript.Shell")
' CAMBIA ESTA RUTA POR LA CARPETA DONDE ESTÁ TU GUARDIAN.PY
WshShell.CurrentDirectory = "D:\Escritorio\PP"
WshShell.Run "python guardian.py", 0, False