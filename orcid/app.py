import os
import re
import traceback
from typing import List, Dict, Set, Tuple, Optional
from datetime import datetime

import pandas as pd
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, BarColumn, TextColumn, TimeRemainingColumn, TimeElapsedColumn, TaskProgressColumn
from rich.table import Table
from rich.panel import Panel
from rich import box

from orcid.utils import get_credentials, get_records, logging


def load_valid_users(input_file: str, console: Console) -> pd.DataFrame:
    """
    Carga y filtra usuarios con ORCID válido de forma eficiente.

    Args:
        input_file: Ruta al archivo CSV de entrada
        console: Rich Console para output

    Returns:
        DataFrame con usuarios que tienen ORCID válido
    """
    try:
        with console.status("[bold blue]Cargando usuarios del archivo CSV...", spinner="dots"):
            # Leer solo las columnas necesarias
            data = pd.read_csv(input_file, usecols=["orcid", "nombre", "cedula"])

            # Filtrar usuarios con ORCID válido usando pandas (más eficiente)
            valid_users = data[data["orcid"].notna() & (data["orcid"] != "-") & (data["orcid"].astype(str) != "nan")].copy()  # No es NaN  # No es guión  # No es string "nan"

        # Crear tabla de resumen
        summary_table = Table(show_header=False, box=box.SIMPLE)
        summary_table.add_column("Stat", style="cyan")
        summary_table.add_column("Value", style="bold green")
        summary_table.add_row("📄 Total usuarios en archivo", str(len(data)))
        summary_table.add_row("✓ Usuarios con ORCID válido", str(len(valid_users)))
        summary_table.add_row("✗ Usuarios sin ORCID", str(len(data) - len(valid_users)))

        console.print(Panel(summary_table, title="[bold]Resumen de Carga[/]", border_style="blue"))

        logging.info(f"Usuarios cargados: {len(data)}, con ORCID válido: {len(valid_users)}")

        return valid_users

    except FileNotFoundError as e:
        tb_str = traceback.format_exc()
        error_msg = f"Archivo no encontrado: {input_file}"
        logging.error(f"{error_msg}")
        logging.error(f"Traceback:\n{tb_str}")
        console.print(f"\n[bold red]❌ {error_msg}[/]")
        console.print(f"[yellow]Asegúrate de que el archivo input.csv existe en la carpeta del proyecto[/]")
        raise
    except pd.errors.EmptyDataError as e:
        tb_str = traceback.format_exc()
        error_msg = f"Archivo vacío: {input_file}"
        logging.error(f"{error_msg}")
        logging.error(f"Traceback:\n{tb_str}")
        console.print(f"\n[bold red]❌ {error_msg}[/]")
        console.print(f"[yellow]El archivo input.csv no contiene datos[/]")
        raise
    except Exception as e:
        tb_str = traceback.format_exc()
        error_msg = f"Error al cargar usuarios desde {input_file}"
        logging.error(f"{error_msg}: {e}")
        logging.error(f"Traceback completo:\n{tb_str}")
        console.print(f"\n[bold red]❌ {error_msg}[/]")
        console.print(f"[red]Tipo de error:[/] {type(e).__name__}")
        console.print(f"[red]Mensaje:[/] {str(e)}")
        console.print(f"[dim]Traceback:\n{tb_str}[/]")
        raise


def process_users(users_df: pd.DataFrame, credentials: str, console: Console) -> Tuple[List[Dict], Dict]:
    """
    Procesa usuarios y obtiene sus registros ORCID.

    Args:
        users_df: DataFrame con usuarios válidos
        credentials: Token de acceso ORCID
        console: Rich Console para output

    Returns:
        Tupla con (datos_procesados, resumen_progreso)
    """
    output_data = []
    processed_pairs: Set[Tuple[str, str]] = set()  # Para evitar duplicados durante el procesamiento

    summary = {"complete": False, "index": 0, "total_users": len(users_df), "processed_records": 0, "errors": 0}

    # Configurar barra de progreso con columnas personalizadas y compactas
    with Progress(
        SpinnerColumn(),
        TextColumn("[bold blue]{task.description}"),
        BarColumn(complete_style="green", finished_style="bold green"),
        TaskProgressColumn(),
        TextColumn("•"),
        TextColumn("[cyan]⏱️ "),
        TimeElapsedColumn(),
        TextColumn("•"),
        TextColumn("[yellow]⏳ "),
        TimeRemainingColumn(),
        console=console,
        expand=False,
    ) as progress:

        task = progress.add_task(f"[cyan]Procesando usuarios ORCID...", total=summary["total_users"])

        for idx, row in users_df.iterrows():
            user = {"orcid": row["orcid"], "nombre": row["nombre"], "cedula": row["cedula"]}

            try:
                # Obtener registros del usuario
                user_records = []
                get_records(user, credentials, user_records, progress.console)

                # Filtrar duplicados basados en orcid_profesor y title
                for record in user_records:
                    key = (record.get("orcid_profesor", ""), record.get("title", ""))
                    if key not in processed_pairs:
                        processed_pairs.add(key)
                        output_data.append(record)
                        summary["processed_records"] += 1

                summary["index"] += 1
                progress.update(task, advance=1)

            except Exception as e:
                summary["errors"] += 1
                # Capturar traceback completo
                tb_str = traceback.format_exc()
                error_msg = f"Error procesando usuario {user['nombre']} ({user['orcid']})"
                
                # Log detallado del error con traceback
                logging.error(f"{error_msg}: {e}")
                logging.error(f"Traceback completo:\n{tb_str}")
                
                # Mostrar en consola de forma más verbose
                progress.console.print(f"\n[bold red]❌ {error_msg}[/]")
                progress.console.print(f"[red]Tipo de error:[/] {type(e).__name__}")
                progress.console.print(f"[red]Mensaje:[/] {str(e)}")
                progress.console.print(f"[dim]Ver logs para traceback completo[/]\n")
                
                summary["index"] += 1
                progress.update(task, advance=1)
                continue

    summary["complete"] = True
    return output_data, summary


def clean_illegal_characters(value):
    """
    Elimina caracteres ilegales para Excel (caracteres de control ASCII 0-31 y 127).
    
    Args:
        value: Valor a limpiar
        
    Returns:
        String limpio o el valor original si no es string
    """
    if isinstance(value, str):
        # Eliminar caracteres de control (ASCII 0-31 y 127)
        # Excepto \t (tab=9), \n (newline=10), \r (carriage return=13)
        return re.sub(r'[\x00-\x08\x0B-\x0C\x0E-\x1F\x7F]', '', value)
    return value


def save_results(output_data: List[Dict], output_file: str, console: Console) -> None:
    """
    Guarda los resultados en archivo XLSX.

    Args:
        output_data: Lista de diccionarios con los datos
        output_file: Ruta del archivo de salida
        console: Rich Console para output
    """
    try:
        with console.status("[bold green]Guardando resultados...", spinner="dots"):
            if not output_data:
                logging.warning("No hay datos para guardar")
                console.print("[yellow]⚠ Advertencia:[/] No se encontraron datos para guardar")
                # Crear archivo vacío con headers
                empty_df = pd.DataFrame(columns=["cedula", "nombre_profesor", "orcid_profesor", "title", "journal", "date", "doi", "source", "note", "url_source"])
                empty_df.to_excel(output_file, index=False, engine='openpyxl')
                return

            df = pd.DataFrame(output_data)

            # Verificación final de duplicados (por seguridad)
            initial_count = len(df)
            df = df.drop_duplicates(subset=["orcid_profesor", "title"], keep="first")
            final_count = len(df)

            if initial_count != final_count:
                logging.info(f"Duplicados eliminados: {initial_count - final_count}")
                console.print(f"[dim]🗑️  Duplicados eliminados: {initial_count - final_count}[/]")

            # Limpiar caracteres ilegales de todas las columnas de tipo string
            for col in df.columns:
                if df[col].dtype == 'object':  # Columnas de texto
                    df[col] = df[col].apply(clean_illegal_characters)
            
            df.to_excel(output_file, index=False, engine='openpyxl')
            logging.info(f"Resultados guardados en: {output_file} ({final_count} registros)")

        console.print(f"[green]✓[/] Resultados guardados: [bold]{final_count}[/] registros en [cyan]{output_file}[/]")

    except Exception as e:
        # Capturar traceback completo
        tb_str = traceback.format_exc()
        error_msg = f"Error al guardar resultados en {output_file}"
        
        # Log detallado con traceback
        logging.error(f"{error_msg}: {e}")
        logging.error(f"Traceback completo:\n{tb_str}")
        
        # Mostrar en consola de forma verbose
        console.print(f"\n[bold red]❌ {error_msg}[/]")
        console.print(f"[red]Tipo de error:[/] {type(e).__name__}")
        console.print(f"[red]Mensaje:[/] {str(e)}")
        console.print(f"[yellow]Traceback:[/]")
        console.print(f"[dim]{tb_str}[/]")
        
        raise


def orcid(console: Optional[Console] = None) -> None:
    """
    Función principal optimizada para procesar registros ORCID.

    Args:
        console: Rich Console para output (opcional)
    """
    if console is None:
        console = Console()

    # Configurar rutas
    root = os.path.dirname(os.path.dirname(__file__))
    input_file = os.path.join(root, "input.csv")
    
    # Generar nombre de archivo con fecha
    fecha_actual = datetime.now().strftime("%Y-%m-%d")
    output_filename = f"publicaciones_orcid_{fecha_actual}.xlsx"
    output_file = os.path.join(root, output_filename)

    logging.info("Iniciando procesamiento ORCID")

    try:
        # 1. Cargar usuarios válidos
        users_df = load_valid_users(input_file, console)

        if len(users_df) == 0:
            console.print("[yellow]⚠[/] No se encontraron usuarios con ORCID válido")
            logging.warning("No se encontraron usuarios con ORCID válido")
            return

        # 2. Obtener credenciales
        with console.status("[bold blue]Obteniendo credenciales ORCID...", spinner="dots"):
            credentials = get_credentials()
        console.print("[green]✓[/] Credenciales ORCID obtenidas exitosamente\n")
        logging.info("Credenciales ORCID obtenidas exitosamente")

        # 3. Procesar usuarios
        output_data, summary = process_users(users_df, credentials, console)

        # 4. Guardar resultados
        console.print()
        save_results(output_data, output_file, console)

        # Mostrar estadísticas finales en tabla
        stats_table = Table(title="📊 Estadísticas del Procesamiento", box=box.ROUNDED, show_header=True, header_style="bold magenta")
        stats_table.add_column("Métrica", style="cyan", no_wrap=True)
        stats_table.add_column("Valor", justify="right", style="bold green")

        stats_table.add_row("👥 Usuarios procesados", f"{summary['index']}/{summary['total_users']}")
        stats_table.add_row("📄 Registros obtenidos", str(summary["processed_records"]))
        stats_table.add_row("❌ Errores", str(summary["errors"]), style="bold yellow" if summary["errors"] > 0 else "bold green")

        success_rate = ((summary["index"] - summary["errors"]) / summary["index"] * 100) if summary["index"] > 0 else 0
        stats_table.add_row("✓ Tasa de éxito", f"{success_rate:.1f}%")

        console.print()
        console.print(stats_table)

        logging.info(f"Procesamiento ORCID completado: {summary}")

    except Exception as e:
        # Capturar traceback completo
        tb_str = traceback.format_exc()
        error_msg = f"Error crítico en procesamiento ORCID"
        
        # Log detallado con traceback completo
        logging.error(f"{error_msg}: {e}")
        logging.error(f"Traceback completo:\n{tb_str}")
        
        # Mostrar en consola de forma muy verbose
        console.print(f"\n[bold red]{'='*80}[/]")
        console.print(f"[bold red]❌ {error_msg.upper()}[/]")
        console.print(f"[bold red]{'='*80}[/]\n")
        
        console.print(f"[red]Tipo de error:[/] [bold]{type(e).__name__}[/]")
        console.print(f"[red]Mensaje:[/] [bold]{str(e)}[/]\n")
        
        console.print(f"[yellow]📋 Traceback detallado:[/]")
        console.print(Panel(tb_str, border_style="red", title="[bold red]Stack Trace[/]"))
        
        console.print(f"\n[cyan]💡 Sugerencia:[/] Revisa el archivo de logs en [bold]orcid/logs/[/] para más detalles")

        # Re-lanzar la excepción para que el llamador pueda manejarla
        raise
