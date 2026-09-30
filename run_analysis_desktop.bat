@echo off
setlocal
cd /d "%~dp0"
python analysis\desktop.py
if errorlevel 1 (
  echo Could not start. Python 3.10 or later with Tkinter is required.
  pause
)
