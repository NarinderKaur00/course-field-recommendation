@echo off
REM Reprint the last benchmark report without re-running anything.
setlocal
set VENV=C:\Users\HP\co544venv
set PYTHONIOENCODING=utf-8

"%VENV%\Scripts\python.exe" benchmark_report.py
