@echo off
REM One-time setup: create the venv and install dependencies.
setlocal
set VENV=C:\Users\HP\co544venv

if not exist "%VENV%\Scripts\python.exe" (
  echo Creating virtual environment at %VENV% ...
  python -m venv "%VENV%" || goto :fail
)

echo Installing dependencies ^(this takes a few minutes^) ...
"%VENV%\Scripts\python.exe" -m pip install --disable-pip-version-check "zenml[server]" -r requirements.txt || goto :fail

echo Initialising ZenML ...
set PYTHONIOENCODING=utf-8
"%VENV%\Scripts\zenml.exe" init || goto :fail

echo.
echo Setup complete. Now run:  dashboard.bat  (terminal 1)  and  run.bat  (terminal 2)
goto :eof

:fail
echo.
echo SETUP FAILED - see the error above.
exit /b 1
