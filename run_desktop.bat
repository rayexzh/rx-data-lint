@echo off
setlocal
cd /d "%~dp0"
set "PYTHONPATH=%CD%\src"
python -m rxdatalint.gui
if errorlevel 1 (
  echo.
  echo RxDataLint could not start. Install Python 3.10 or later and try again.
  pause
)

