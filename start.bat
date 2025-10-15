@echo off
REM Script para ejecutar el programa con entorno virtual
echo Iniciando...

REM Verificar si existe el entorno virtual
if not exist "venv" (
    echo Error: No se encontró el entorno virtual 'venv'.
    echo Por favor ejecuta primero: setup.bat
    pause
    exit /b 1
)

REM Activar entorno virtual
echo Activando entorno virtual...
call venv\Scripts\activate.bat

if errorlevel 1 (
    echo Error: No se pudo activar el entorno virtual.
    pause
    exit /b 1
)

REM Ejecutar el programa principal
echo Ejecutando main.py...
venv\Scripts\python main.py

REM Desactivar entorno virtual al finalizar
deactivate
echo Programa finalizado.
pause