@echo off
REM Regenerate the 200 SYNTHETIC students (data/Grade_CS_Students_augmented.csv).
setlocal
set VENV=C:\Users\HP\co544venv
set PYTHONIOENCODING=utf-8

"%VENV%\Scripts\python.exe" scripts\generate_synthetic_students.py %*
