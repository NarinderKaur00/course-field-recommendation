@echo off
REM Terminal 1: start the ZenML dashboard UI. Leave this window open.
setlocal
set VENV=C:\Users\HP\co544venv
set PYTHONIOENCODING=utf-8

echo.
echo Starting the ZenML dashboard...
echo When you see "Uvicorn running", open  http://127.0.0.1:8237  in your browser.
echo Press CTRL+C to stop it.
echo.

"%VENV%\Scripts\zenml.exe" login --local --blocking
