@echo off
set GSK_PATH=C:\Genlex_Linear\gsk.exe
assoc .all=GenlexNative
ftype GenlexNative="%GSK_PATH%" "%%1"
echo [ NATIVE ] .all files bound to GSK kernel.
