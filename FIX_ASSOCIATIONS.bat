@echo off
:: GENLEX ASSOCIATION FIX UTILITY
:: Run this as Administrator to bind .all and .cgl to the native C++ Kernel.

set "GSK_PATH=C:\Genlex_Linear\gsk.exe"

if not exist "%GSK_PATH%" (
    echo [ ERROR ] gsk.exe not found at %GSK_PATH%
    pause
    exit /b
)

echo [ NATIVE ] Registering .all association...
assoc .all=GenlexNative
ftype GenlexNative="%GSK_PATH%" "%%1"

echo [ NATIVE ] Registering .cgl association...
assoc .cgl=GenlexGrid
ftype GenlexGrid="%GSK_PATH%" "%%1"

echo.
echo [ SUCCESS ] .all and .cgl files are now bound to the C++ GSK.
echo [ READY ] You can now double-click .all files to execute them.
pause
