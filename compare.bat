@echo off
REM Print the model comparison table from the ZenML artifact store.
setlocal
set VENV=C:\Users\HP\co544venv
set PYTHONIOENCODING=utf-8

"%VENV%\Scripts\python.exe" compare_results.py
