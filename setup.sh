#!/bin/bash

# Script para configurar el entorno virtual e instalar dependencias
# Compatible con Linux y macOS

echo "Configurando entorno virtual para el proyecto Google Scholar..."

# Verificar si Python3 está instalado
if ! command -v python3 &> /dev/null; then
    echo "Error: Python3 no está instalado. Por favor instala Python3 primero."
    exit 1
fi

# Verificar si pip está instalado
if ! python3 -m pip --version &> /dev/null; then
    echo "Error: pip no está disponible. Por favor instala pip primero."
    exit 1
fi

# Nombre del entorno virtual
VENV_NAME="venv"

# Crear entorno virtual si no existe
if [ ! -d "$VENV_NAME" ]; then
    echo "Creando entorno virtual '$VENV_NAME'..."
    python3 -m venv $VENV_NAME
    
    if [ $? -ne 0 ]; then
        echo "Error: No se pudo crear el entorno virtual."
        exit 1
    fi
    echo "Entorno virtual creado exitosamente."
else
    echo "El entorno virtual '$VENV_NAME' ya existe."
fi

# Activar entorno virtual
echo "Activando entorno virtual..."
source $VENV_NAME/bin/activate

if [ $? -ne 0 ]; then
    echo "Error: No se pudo activar el entorno virtual."
    exit 1
fi

echo "Entorno virtual activado."

# Actualizar pip
echo "Actualizando pip..."
python -m pip install --upgrade pip

# Instalar dependencias
if [ -f "requirements.txt" ]; then
    echo "Instalando dependencias desde requirements.txt..."
    pip install -r requirements.txt
    
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
echo "   Activar:   source $VENV_NAME/bin/activate"
echo "   Desactivar: deactivate"
echo ""
echo "Para ejecutar el programa:"
echo "   Con entorno activado: python main.py"
echo "   O directamente: ./start.sh"
echo ""