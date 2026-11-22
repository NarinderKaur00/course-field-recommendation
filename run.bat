@echo off
REM Terminal 2: run every pipeline end to end, then print the comparison table.
REM Optionally pass a different dataset:  run.bat .\data\Other.csv
setlocal
set VENV=C:\Users\HP\co544venv
set PYTHONIOENCODING=utf-8

"%VENV%\Scripts\python.exe" run_all_pipelines.py %*
