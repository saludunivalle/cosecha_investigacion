import logging
import os
import sys
import time
import traceback
from typing import Any, Dict, List, Optional

import requests
from rich.console import Console

# Configuración de logging
log_file = os.path.join(os.path.dirname(__file__), "orcid.log")
log_folder = os.path.join(os.path.dirname(__file__), "logs")

# Rotar logs antiguos
if os.path.exists(log_file):
    if not os.path.exists(log_folder):
        os.makedirs(log_folder)
    os.rename(log_file, f"{log_folder}/orcid_{time.strftime('%Y%m%d_%H%M%S')}.log")

# Configurar el logger
logging.basicConfig(filename=log_file, filemode="w", format="[%(asctime)s - %(levelname)s] %(message)s", level=logging.INFO)

# Constantes
ORCID_API_BASE_URL = "https://pub.orcid.org/v3.0"
ORCID_TOKEN_URL = "https://orcid.org/oauth/token"
REQUEST_TIMEOUT = 30


def safe_get(data: Any, *keys: str, default: str = "") -> str:
    """
    Extrae valores anidados de diccionarios de forma segura.

    Args:
        data: Diccionario o estructura de datos a consultar
        *keys: Secuencia de claves para acceder al valor anidado
        default: Valor por defecto si no se encuentra la clave

    Returns:
        Valor encontrado o default si no existe

    Example:
        >>> data = {"a": {"b": {"c": "value"}}}
        >>> safe_get(data, "a", "b", "c")
        'value'
        >>> safe_get(data, "x", "y", default="not_found")
        'not_found'
    """
    try:
        result = data
        for key in keys:
            if result is None:
                return default
            result = result.get(key, {}) if isinstance(result, dict) else default

        # Limpiar el resultado si es string
        if isinstance(result, str):
            return result.replace("\n", " ").strip()

        return result if result != {} else default

    except (AttributeError, KeyError, TypeError):
        return default


def get_credentials() -> str:
    """
    Obtiene el token de acceso de ORCID usando credenciales de variables de entorno.

    Returns:
        Token de acceso de ORCID

    Raises:
        ValueError: Si las credenciales no están configuradas
        requests.RequestException: Si falla la autenticación
    """
    client_id = os.getenv("ORCID_CLIENT_ID")
    client_secret = os.getenv("ORCID_CLIENT_SECRET")

    if not client_id or not client_secret:
        error_msg = "Las credenciales ORCID no están configuradas. Verifica las variables de entorno ORCID_CLIENT_ID y ORCID_CLIENT_SECRET"
        logging.error(error_msg)
        raise ValueError(error_msg)

    try:
        data = {"client_id": client_id, "client_secret": client_secret, "grant_type": "client_credentials", "scope": "/read-public"}

        headers = {"Content-Type": "application/x-www-form-urlencoded", "Accept": "application/json"}

        response = requests.post(ORCID_TOKEN_URL, data=data, headers=headers, timeout=REQUEST_TIMEOUT)
        response.raise_for_status()

        token = response.json().get("access_token")
        if not token:
            raise ValueError("No se recibió token de acceso en la respuesta")

        logging.info("Token de acceso ORCID obtenido exitosamente")
        return token

    except requests.RequestException as e:
        error_msg = f"Error al obtener credenciales ORCID: {e}"
        logging.error(error_msg)
        raise


def get_title(work_summary: List[Dict]) -> str:
    """
    Extrae el título de la publicación del work summary.

    Args:
        work_summary: Lista con el resumen del trabajo desde ORCID

    Returns:
        Título de la publicación o cadena vacía
    """
    try:
        if not work_summary:
            return ""
        return safe_get(work_summary[0], "title", "title", "value")
    except Exception as e:
        logging.error(f"Error extrayendo título: {e}")
        return ""


def get_journal(work_summary: List[Dict]) -> str:
    """
    Extrae el nombre de la revista del work summary.

    Args:
        work_summary: Lista con el resumen del trabajo desde ORCID

    Returns:
        Nombre de la revista o cadena vacía
    """
    try:
        if not work_summary:
            return ""
        return safe_get(work_summary[0], "journal-title", "value")
    except Exception as e:
        logging.error(f"Error extrayendo revista: {e}")
        return ""


def get_date(work_summary: List[Dict]) -> str:
    try:
        if not work_summary:
            return ""
        pub_date = work_summary[0].get("publication-date", {})
        if not pub_date or not isinstance(pub_date, dict):
            return ""
        year = pub_date.get("year", {}).get("value", "")
        month = pub_date.get("month", {}).get("value", "")
        day = pub_date.get("day", {}).get("value", "")
        if not year:
            return ""
        if month:
            month = month.zfill(2)
        if day:
            day = day.zfill(2)
        if year and month and day:
            return f"{year}-{month}-{day}"
        elif year and month:
            return f"{year}-{month}"
        else:
            return year
    except Exception as e:
        logging.error(f"Error extrayendo fecha: {e}")
        return ""


def get_doi(work_summary: List[Dict]) -> str:
    try:
        if not work_summary:
            return ""
        external_ids = work_summary[0].get("external-ids", {}).get("external-id", [])
        for ext in external_ids:
            if ext.get("external-id-type", "").lower() == "doi":
                value = ext.get("external-id-value", "")
                if value:
                    return value
        return ""
    except Exception as e:
        logging.error(f"Error extrayendo DOI: {e}")
        return ""


def get_url_source(work_summary: List[Dict]) -> str:
    try:
        if not work_summary:
            return ""
        url = work_summary[0].get("url", None)
        if url:
            return url.get("value", "") if isinstance(url, dict) else url
        external_ids = work_summary[0].get("external-ids", {}).get("external-id", [])
        for ext in external_ids:
            if ext.get("external-id-type", "").lower() == "doi":
                ext_url = ext.get("external-id-url", {})
                if isinstance(ext_url, dict):
                    value = ext_url.get("value", "")
                    if value:
                        return value
                elif isinstance(ext_url, str):
                    if ext_url:
                        return ext_url
        return ""
    except Exception as e:
        logging.error(f"Error extrayendo URL de origen: {e}")
        return ""


def _create_error_record(user: Dict, error_msg: str) -> Dict:
    """
    Crea un registro de error estandarizado.

    Args:
        user: Diccionario con datos del usuario
        error_msg: Mensaje de error

    Returns:
        Diccionario con registro de error
    """
    return {
        "cedula": user.get("cedula", ""),
        "nombre_profesor": user.get("nombre", ""),
        "orcid_profesor": user.get("orcid", ""),
        "title": "",
        "journal": "",
        "date": "",
        "doi": "",
        "source": "ORCID",
        "note": error_msg[:100],  # Limitar longitud
        "url_source": "",
    }


def _create_work_record(user: Dict, work_summary: List[Dict]) -> Dict:
    """
    Crea un registro de publicación desde el work summary.

    Args:
        user: Diccionario con datos del usuario
        work_summary: Lista con el resumen del trabajo desde ORCID

    Returns:
        Diccionario con registro de publicación
    """
   # print(work_summary)
    #print("DEBUG date", get_date(work_summary))
    #print("DEBUG doi", get_doi(work_summary))
    #print("DEBUG url_source", get_url_source(work_summary))
    return {
        "cedula": user.get("cedula", ""),
        "nombre_profesor": user.get("nombre", ""),
        "orcid_profesor": user.get("orcid", ""),
        "title": get_title(work_summary),
        "journal": get_journal(work_summary),
        "date": get_date(work_summary),
        "doi": get_doi(work_summary),
        "source": "ORCID",
        "note": "",
        "url_source": get_url_source(work_summary),
    }


def get_records(user: Dict, access_token: str, file_output: List[Dict], console: Optional[Console] = None) -> None:
    """
    Obtiene registros de publicaciones para un usuario ORCID.

    Args:
        user: Diccionario con datos del usuario (orcid, nombre, cedula)
        access_token: Token de acceso ORCID
        file_output: Lista donde se agregan los registros obtenidos
        console: Rich Console para output (opcional)
    """
    orcid = user.get("orcid")
    nombre = user.get("nombre", "Desconocido")

    if not orcid:
        logging.error(f"ORCID vacío para usuario: {nombre}")
        return

    try:
        # Configurar headers para la API
        headers = {"Content-Type": "application/json", "Accept": "application/json", "Authorization": f"Bearer {access_token}"}

        # Obtener trabajos del usuario
        works_url = f"{ORCID_API_BASE_URL}/{orcid}/works"
        response = requests.get(works_url, headers=headers, timeout=REQUEST_TIMEOUT)
        response.raise_for_status()

        # Procesar trabajos
        data = response.json()
        works = data.get("group", [])

        if console:
            console.print(f"  [dim]→ {nombre} ([cyan]{orcid}[/]): [green]{len(works)}[/] trabajos[/]")
        
        logging.info(f"ORCID {orcid}: {len(works)} trabajos encontrados")

        if not works:
            logging.info(f"No se encontraron trabajos para ORCID: {orcid}")
            file_output.append(_create_error_record(user, "NO WORKS FOUND"))
            return

        # Procesar cada trabajo
        for work in works:
            try:
                work_summary = work.get("work-summary", [])
                if not work_summary:
                    continue

                record = _create_work_record(user, work_summary)
                file_output.append(record)

            except Exception as work_error:
                logging.error(f"Error procesando trabajo para ORCID {orcid}: {work_error}")
                continue

    except requests.Timeout:
        error_msg = f"Timeout conectando a ORCID para {orcid}"
        if console:
            console.print(f"  [yellow]⏱️  Timeout: {nombre}[/]")
        logging.error(error_msg)
        file_output.append(_create_error_record(user, f"ERROR: {error_msg}"))

    except requests.RequestException as e:
        error_msg = f"Error de red para ORCID {orcid}: {e}"
        if console:
            console.print(f"  [red]🌐 Error de red: {nombre}[/]")
        logging.error(error_msg)
        file_output.append(_create_error_record(user, f"ERROR: {str(e)}"))

    except Exception as e:
        error_msg = f"Error inesperado para ORCID {orcid}: {e}"
        if console:
            console.print(f"  [red]❌ Error: {nombre}[/]")
        logging.error(error_msg)
        if logging.getLogger().isEnabledFor(logging.DEBUG):
            traceback.print_exc()
        file_output.append(_create_error_record(user, f"ERROR: {str(e)}"))
