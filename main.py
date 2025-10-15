#!/usr/bin/env python3
"""
Script principal para procesamiento de publicaciones académicas.

Este script procesa datos de ORCID y Google Scholar para obtener
información de publicaciones de investigadores.
"""

import os
import sys
from dotenv import load_dotenv

from orcid.app import orcid


def verify_environment() -> bool:
    """
    Verifica que las variables de entorno necesarias estén configuradas.

    Returns:
        True si todas las variables están configuradas, False en caso contrario
    """
    required_vars = ["ORCID_CLIENT_ID", "ORCID_CLIENT_SECRET"]
    missing_vars = [var for var in required_vars if not os.getenv(var)]

    if missing_vars:
        print("Error: Faltan las siguientes variables de entorno:")
        for var in missing_vars:
            print(f"  - {var}")
        print("\nAsegúrate de tener un archivo .env con estas variables configuradas.")
        return False

    return True


def main():
    """
    Función principal del programa.
    Carga variables de entorno y ejecuta el procesamiento de ORCID y Scholar.
    """
    # Cargar variables de entorno desde archivo .env
    dotenv_path = os.path.join(os.path.dirname(__file__), ".env")

    if not os.path.exists(dotenv_path):
        print(f"Advertencia: No se encontró el archivo .env en {dotenv_path}")
        print("Intentando usar variables de entorno del sistema...")

    load_dotenv(dotenv_path)

    # Verificar que las variables necesarias estén configuradas
    if not verify_environment():
        sys.exit(1)

    print("Variables de entorno cargadas correctamente")
    print("=" * 60)

    try:
        # Ejecutar procesamiento de ORCID
        print("\n Iniciando procesamiento ORCID...")
        orcid()
        print("\n" + "=" * 60)
        print("Procesamiento completado exitosamente")

    except KeyboardInterrupt:
        print("\n\nProcesamiento interrumpido por el usuario")
        sys.exit(1)

    except Exception as e:
        print(f"\n\nError crítico durante el procesamiento: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
