@echo off
title AERIS SOVEREIGN SINGULARITY
color 0B
echo --- INITIALIZING GENLEX SINGULARITY ---
echo Enclave: C:\Genlex_Core
echo Engine:  C:\Genlex_Linear\all_engine.py
echo.
python C:\Genlex_Linear\all_engine.py C:\Genlex_Core\singularity.all
echo.
echo --- EXECUTION COMPLETE ---
pause
