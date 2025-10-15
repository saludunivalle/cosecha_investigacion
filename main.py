#!/usr/bin/env python3
"""
Script principal para procesamiento de publicaciones académicas.

Este script procesa datos de ORCID para obtener
información de publicaciones de investigadores.
"""

import os
import sys
from dotenv import load_dotenv
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich import box

from orcid.app import orcid

# Inicializar Rich Console
console = Console()


def verify_environment() -> bool:
    """
    Verifica que las variables de entorno necesarias estén configuradas.

    Returns:
        True si todas las variables están configuradas, False en caso contrario
    """
    required_vars = ["ORCID_CLIENT_ID", "ORCID_CLIENT_SECRET"]
    missing_vars = [var for var in required_vars if not os.getenv(var)]

    if missing_vars:
        error_table = Table(show_header=False, box=box.SIMPLE)
        error_table.add_column("Variable", style="yellow")
        for var in missing_vars:
            error_table.add_row(f"✗ {var}")

        console.print(Panel(error_table, title="[bold red]❌ Error: Variables de Entorno Faltantes[/]", subtitle="Asegúrate de tener un archivo .env configurado", border_style="red"))
        return False

    return True


def main():
    """
    Función principal del programa.
    Carga variables de entorno y ejecuta el procesamiento de ORCID.
    """
    # Mostrar banner de bienvenida
    console.print(Panel.fit("[bold cyan]Procesamiento de Publicaciones Académicas[/]\n" "[dim]ORCID Data Extractor[/]", border_style="cyan", padding=(1, 2)))

    # Cargar variables de entorno desde archivo .env
    dotenv_path = os.path.join(os.path.dirname(__file__), ".env")

    if not os.path.exists(dotenv_path):
        console.print(f"[yellow]⚠ Advertencia:[/] No se encontró el archivo .env en {dotenv_path}")
        console.print("[dim]Intentando usar variables de entorno del sistema...[/]\n")

    load_dotenv(dotenv_path)

    # Verificar que las variables necesarias estén configuradas
    if not verify_environment():
        sys.exit(1)

    console.print("[green]✓[/] Variables de entorno cargadas correctamente\n")

    try:
        # Ejecutar procesamiento de ORCID
        console.rule("[bold blue]Iniciando Procesamiento ORCID[/]", style="blue")
        orcid(console)

        console.rule("[bold green]Procesamiento Completado[/]", style="green")
        console.print(Panel("[bold green]✓ Procesamiento completado exitosamente[/]", border_style="green"))

    except KeyboardInterrupt:
        console.print("\n")
        console.print(Panel("[bold yellow]⚠ Procesamiento interrumpido por el usuario[/]", border_style="yellow"))
        sys.exit(1)

    except Exception as e:
        console.print("\n")
        console.print(Panel(f"[bold red]❌ Error crítico durante el procesamiento:[/]\n\n{e}", title="Error", border_style="red"))
        sys.exit(1)


if __name__ == "__main__":
    main()
