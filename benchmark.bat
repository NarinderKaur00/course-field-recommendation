@echo off
REM Benchmark every classical ML model. Add --augmented for the 535-row set.
setlocal
set VENV=C:\Users\HP\co544venv
set PYTHONIOENCODING=utf-8

"%VENV%\Scripts\python.exe" run_benchmark_pipeline.py %*
