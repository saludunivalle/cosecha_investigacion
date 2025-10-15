@echo off
REM Script para configurar el entorno virtual e instalar dependencias
REM Compatible con Windows

echo Configurando entorno virtual para el proyecto Google Scholar...

REM Verificar si Python está instalado
python --version >nul 2>&1
if errorlevel 1 (
    echo Error: Python no está instalado o no está en el PATH.
    echo Por favor instala Python desde https://www.python.org/
    pause
    exit /b 1
)

REM Verificar si pip está disponible
python -m pip --version >nul 2>&1
if errorlevel 1 (
    echo Error: pip no está disponible.
    pause
    exit /b 1
)

REM Nombre del entorno virtual
set VENV_NAME=venv

REM Crear entorno virtual si no existe
if not exist "%VENV_NAME%" (
    echo Creando entorno virtual '%VENV_NAME%'...
    python -m venv %VENV_NAME%
    
    if errorlevel 1 (
        echo Error: No se pudo crear el entorno virtual.
        pause
        exit /b 1
    )
    echo Entorno virtual creado exitosamente.
) else (
    echo El entorno virtual '%VENV_NAME%' ya existe.
)

REM Activar entorno virtual
echo Activando entorno virtual...
call %VENV_NAME%\Scripts\activate.bat

if errorlevel 1 (
    echo Error: No se pudo activar el entorno virtual.
    pause
    exit /b 1
)

echo Entorno virtual activado.

REM Actualizar pip
echo Actualizando pip...
python -m pip install --upgrade pip

REM Instalar dependencias
if exist "requirements.txt" (
    echo Instalando dependencias desde requirements.txt...
    pip install -r requirements.txt
    
    if errorlevel 1 (
        echo Error: Algunas dependencias no se pudieron instalar.
        pause
        exit /b 1
    )
    echo Todas las dependencias se instalaron correctamente.
) else (
    echo Advertencia: No se encontró el archivo requirements.txt
)

echo.
echo Configuración completada exitosamente.
echo.
echo Para usar el entorno virtual en el futuro:
echo    Activar:   %VENV_NAME%\Scripts\activate.bat
echo    Desactivar: deactivate
echo.
echo Para ejecutar el programa:
echo    Con entorno activado: python main.py
echo    O directamente: start.bat
echo.
pause