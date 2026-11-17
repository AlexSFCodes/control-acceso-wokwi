@echo off
setlocal
cd /d "%~dp0"
set "PYTHON_PROYECTO=%LocalAppData%\Programs\Python\Python311\python.exe"
if not exist ".venv\Scripts\python.exe" (
  if exist "%PYTHON_PROYECTO%" (
    "%PYTHON_PROYECTO%" -m venv .venv
  ) else (
    python -m venv .venv
  )
  if errorlevel 1 goto error
)
".venv\Scripts\python.exe" -m pip install -r requirements.txt
if errorlevel 1 goto error
echo Listo. Abre iniciar.cmd para analizar fotos.
pause
exit /b 0
:error
echo No se pudo preparar el entorno. Revisa que Python este instalado y tengas Internet.
pause
exit /b 1
