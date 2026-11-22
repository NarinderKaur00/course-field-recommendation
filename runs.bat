@echo off
REM List every tracked pipeline run.
setlocal
set VENV=C:\Users\HP\co544venv
set PYTHONIOENCODING=utf-8

"%VENV%\Scripts\zenml.exe" pipeline runs list
