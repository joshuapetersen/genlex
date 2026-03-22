@echo off
set "RUNNER=C:\Genlex_Linear\genlex_runner.exe"

echo --- REGISTERING GENLEX NATIVE HANDLER ---
echo Runner: %RUNNER%
echo.

:: Associate .all
reg add "HKCU\Software\Classes\.all" /ve /d "Genlex.File" /f
reg add "HKCU\Software\Classes\Genlex.File" /ve /d "Genlex Logic Script" /f
reg add "HKCU\Software\Classes\Genlex.File\shell\open\command" /ve /d "\"%RUNNER%\" \"%%1\"" /f

:: Associate .cgl
reg add "HKCU\Software\Classes\.cgl" /ve /d "Genlex.Grid" /f
reg add "HKCU\Software\Classes\Genlex.Grid" /ve /d "Genlex Grid Matrix" /f
reg add "HKCU\Software\Classes\Genlex.Grid\shell\open\command" /ve /d "\"%RUNNER%\" \"%%1\"" /f

echo.
echo --- REGISTRATION COMPLETE ---
echo You can now double-click .all and .cgl files to execute them.
echo.
pause
