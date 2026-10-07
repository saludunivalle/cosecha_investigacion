#!/bin/bash

# Script para configurar el entorno virtual e instalar dependencias
# Compatible con Linux, macOS y Git Bash en Windows

echo "Configurando entorno virtual para el proyecto ..."

# Verificar si Python3 está instalado
if ! command -v python3 &> /dev/null; then
    echo "Error: Python3 no está instalado. Por favor instala Python3 primero."
    exit 1
fi

# Nombre del entorno virtual
VENV_NAME="venv"

# Seleccionar las rutas según el sistema operativo.
if [ -f "$VENV_NAME/Scripts/activate" ]; then
    VENV_BIN="$VENV_NAME/Scripts"
    VENV_ACTIVATE="$VENV_BIN/activate"
    VENV_PYTHON="$VENV_BIN/python.exe"
else
    VENV_BIN="$VENV_NAME/bin"
    VENV_ACTIVATE="$VENV_BIN/activate"
    VENV_PYTHON="$VENV_BIN/python3"
fi

# Crear entorno virtual si no existe
if [ ! -d "$VENV_NAME" ]; then
    echo "Creando entorno virtual '$VENV_NAME'..."
    python3 -m venv "$VENV_NAME"
    
    if [ $? -ne 0 ]; then
        echo "Error: No se pudo crear el entorno virtual."
        exit 1
    fi
    echo "Entorno virtual creado exitosamente."
else
    echo "El entorno virtual '$VENV_NAME' ya existe."
fi

# Volver a seleccionar las rutas por si el entorno acaba de crearse.
if [ -f "$VENV_NAME/Scripts/activate" ]; then
    VENV_BIN="$VENV_NAME/Scripts"
    VENV_ACTIVATE="$VENV_BIN/activate"
    VENV_PYTHON="$VENV_BIN/python.exe"
else
    VENV_BIN="$VENV_NAME/bin"
    VENV_ACTIVATE="$VENV_BIN/activate"
    VENV_PYTHON="$VENV_BIN/python3"
fi

# Un entorno creado en Windows no puede ejecutarse desde WSL.
if [ -f "$VENV_NAME/Scripts/python.exe" ] && [ "$(uname -s)" = "Linux" ]; then
    echo "Error: '$VENV_NAME' fue creado para Windows y esta terminal es WSL."
    echo "Elimina '$VENV_NAME' y vuelve a ejecutar este script desde WSL para recrearlo."
    exit 1
fi

# Verificar que el entorno tenga pip.
if [ ! -f "$VENV_PYTHON" ] || ! "$VENV_PYTHON" -m pip --version &> /dev/null; then
    echo "Error: pip no está disponible dentro del entorno virtual '$VENV_NAME'."
    exit 1
fi

# Activar entorno virtual
echo "Activando entorno virtual..."
if [ ! -f "$VENV_ACTIVATE" ]; then
    echo "Error: No se encontró el activador del entorno virtual en '$VENV_ACTIVATE'."
    exit 1
fi
source "$VENV_ACTIVATE"

if [ $? -ne 0 ]; then
    echo "Error: No se pudo activar el entorno virtual."
    exit 1
fi

echo "Entorno virtual activado."

# Actualizar pip
echo "Actualizando pip..."
"$VENV_PYTHON" -m pip install --upgrade pip

# Instalar dependencias
if [ -f "requirements.txt" ]; then
    echo "Instalando dependencias desde requirements.txt..."
    "$VENV_PYTHON" -m pip install -r requirements.txt
    
    if [ $? -eq 0 ]; then
        echo "Todas las dependencias se instalaron correctamente."
    else
        echo "Error: Algunas dependencias no se pudieron instalar."
        exit 1
    fi
else
    echo "Advertencia: No se encontró el archivo requirements.txt"
fi

echo ""
echo "Configuración completada exitosamente."
echo ""
echo "Para usar el entorno virtual en el futuro:"
echo "   Activar en Linux/macOS: source $VENV_NAME/bin/activate"
echo "   Activar en Git Bash/Windows: source $VENV_NAME/Scripts/activate"
echo "   Desactivar: deactivate"
echo ""
echo "Para ejecutar el programa:"
echo "   Con entorno activado: python main.py"
echo "   O directamente: ./start.sh"
echo ""