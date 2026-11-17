@echo off
setlocal
cd /d "%~dp0"
if exist ".venv\Scripts\python.exe" (
  ".venv\Scripts\python.exe" app.py
  if errorlevel 1 pause
  exit /b
)
echo Primero ejecuta instalar.cmd para preparar Python.
pause
