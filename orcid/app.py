import os
import sys
from typing import List, Dict, Set, Tuple

import pandas as pd

from orcid.utils import get_credentials, get_records, logging
from utils import save_summary


def load_valid_users(input_file: str) -> pd.DataFrame:
    """
    Carga y filtra usuarios con ORCID válido de forma eficiente.

    Args:
        input_file: Ruta al archivo CSV de entrada

    Returns:
        DataFrame con usuarios que tienen ORCID válido
    """
    try:
        # Leer solo las columnas necesarias
        data = pd.read_csv(input_file, usecols=["orcid", "nombre", "cedula"])

        # Filtrar usuarios con ORCID válido usando pandas (más eficiente)
        valid_users = data[data["orcid"].notna() & (data["orcid"] != "-") & (data["orcid"].astype(str) != "nan")].copy()  # No es NaN  # No es guión  # No es string "nan"

        logging.info(f"Usuarios cargados: {len(data)}, con ORCID válido: {len(valid_users)}")
        print(f"Usuarios cargados: {len(data)}, con ORCID válido: {len(valid_users)}")

        return valid_users

    except FileNotFoundError:
        logging.error(f"Archivo no encontrado: {input_file}")
        raise
    except pd.errors.EmptyDataError:
        logging.error(f"Archivo vacío: {input_file}")
        raise
    except Exception as e:
        logging.error(f"Error al cargar usuarios: {e}")
        raise


def process_users(users_df: pd.DataFrame, credentials: str) -> Tuple[List[Dict], Dict]:
    """
    Procesa usuarios y obtiene sus registros ORCID.

    Args:
        users_df: DataFrame con usuarios válidos
        credentials: Token de acceso ORCID

    Returns:
        Tupla con (datos_procesados, resumen_progreso)
    """
    output_data = []
    processed_pairs: Set[Tuple[str, str]] = set()  # Para evitar duplicados durante el procesamiento

    summary = {"complete": False, "index": 0, "total_users": len(users_df), "processed_records": 0, "errors": 0}

    print(f"Procesando {summary['total_users']} usuarios...")

    for idx, row in users_df.iterrows():
        user = {"orcid": row["orcid"], "nombre": row["nombre"], "cedula": row["cedula"]}

        try:
            # Obtener registros del usuario
            user_records = []
            get_records(user, credentials, user_records)

            # Filtrar duplicados basados en orcid_profesor y title
            for record in user_records:
                key = (record.get("orcid_profesor", ""), record.get("title", ""))
                if key not in processed_pairs:
                    processed_pairs.add(key)
                    output_data.append(record)
                    summary["processed_records"] += 1

            summary["index"] += 1

            # Mostrar progreso
            progress = (summary["index"] / summary["total_users"]) * 100
            print(f"Progreso: {summary['index']}/{summary['total_users']} ({progress:.1f}%)")

        except Exception as e:
            summary["errors"] += 1
            logging.error(f"Error procesando usuario {user['orcid']}: {e}")
            print(f"Error procesando usuario {user['nombre']}: {e}")
            continue

    summary["complete"] = True
    return output_data, summary


def save_results(output_data: List[Dict], output_file: str) -> None:
    """
    Guarda los resultados en archivo CSV.

    Args:
        output_data: Lista de diccionarios con los datos
        output_file: Ruta del archivo de salida
    """
    try:
        if not output_data:
            logging.warning("No hay datos para guardar")
            print("Advertencia: No se encontraron datos para guardar")
            # Crear archivo vacío con headers
            empty_df = pd.DataFrame(columns=["cedula", "nombre_profesor", "orcid_profesor", "title", "journal", "date", "doi", "source", "note", "url_source"])
            empty_df.to_csv(output_file, index=False)
            return

        df = pd.DataFrame(output_data)

        # Verificación final de duplicados (por seguridad)
        initial_count = len(df)
        df = df.drop_duplicates(subset=["orcid_profesor", "title"], keep="first")
        final_count = len(df)

        if initial_count != final_count:
            logging.info(f"Duplicados eliminados: {initial_count - final_count}")

        df.to_csv(output_file, index=False)
        logging.info(f"Resultados guardados en: {output_file} ({final_count} registros)")
        print(f"Resultados guardados: {final_count} registros en {output_file}")

    except Exception as e:
        logging.error(f"Error al guardar resultados: {e}")
        raise


def orcid() -> None:
    """
    Función principal optimizada para procesar registros ORCID.
    """
    # Configurar rutas
    root = os.path.dirname(os.path.dirname(__file__))
    app_root = os.path.dirname(__file__)
    input_file = os.path.join(root, "input.csv")
    output_file = os.path.join(app_root, "output.csv")

    print("Iniciando procesamiento ORCID...")
    logging.info("Iniciando procesamiento ORCID")

    try:
        # 1. Cargar usuarios válidos
        users_df = load_valid_users(input_file)

        if len(users_df) == 0:
            print("No se encontraron usuarios con ORCID válido")
            logging.warning("No se encontraron usuarios con ORCID válido")
            return

        # 2. Obtener credenciales
        print("Obteniendo credenciales ORCID...")
        credentials = get_credentials()
        logging.info("Credenciales ORCID obtenidas exitosamente")

        # 3. Procesar usuarios
        output_data, summary = process_users(users_df, credentials)

        # 4. Guardar resultados
        save_results(output_data, output_file)

        # 5. Guardar resumen
        save_summary({"orcid": summary}, root)

        # Mostrar estadísticas finales
        print(f"\nProcesamiento completado:")
        print(f"- Usuarios procesados: {summary['index']}/{summary['total_users']}")
        print(f"- Registros obtenidos: {summary['processed_records']}")
        print(f"- Errores: {summary['errors']}")

        logging.info(f"Procesamiento ORCID completado: {summary}")

    except Exception as e:
        error_msg = f"Error crítico en procesamiento ORCID: {e}"
        print(error_msg)
        logging.error(error_msg)

        # Guardar resumen con error
        error_summary = {"complete": False, "error": str(e), "index": 0}
        save_summary({"orcid": error_summary}, root)

        # Re-lanzar la excepción para que el llamador pueda manejarla
        raise
