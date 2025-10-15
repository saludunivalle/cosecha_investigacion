#!/bin/bash

# Script para ejecutar el programa con entorno virtual
echo "Iniciando..."

# Verificar si existe el entorno virtual
if [ ! -d "venv" ]; then
    echo "Error: No se encontró el entorno virtual 'venv'."
    echo "Por favor ejecuta primero: ./setup.sh"
    exit 1
fi

# Activar entorno virtual
echo "Activando entorno virtual..."
source venv/bin/activate

if [ $? -ne 0 ]; then
    echo "Error: No se pudo activar el entorno virtual."
    exit 1
fi

# Ejecutar el programa principal
echo "Ejecutando main.py..."
./venv/bin/python3 main.py

# Desactivar entorno virtual al finalizar
deactivate
echo "Programa finalizado."