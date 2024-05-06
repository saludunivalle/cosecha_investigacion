import logging
import os
import sys
import time
import traceback

import requests

log_file = os.path.join(os.path.dirname(__file__), "orcid.log")
log_folder = os.path.join(os.path.dirname(__file__), "logs")

if os.path.exists(log_file):
    if not os.path.exists(log_folder):
        os.makedirs(log_folder)
    os.rename(log_file, f"{log_folder}/orcid_{time.strftime('%Y%m%d_%H%M%S')}.log")

# Configuración del registro
logging.basicConfig(filename=log_file, filemode="w", format="[%(asctime)s - %(message)s]", level=logging.INFO)


def get_credentials():
    data = {"client_id": "APP-ZJ2G7PMAMCRMVIWD", "client_secret": "4ed3921d-0faa-47c8-ace6-9bd1c7c1fafb", "grant_type": "client_credentials", "scope": "/read-public"}
    headers = {"Content-Type": "application/x-www-form-urlencoded", "Accept": "application/json"}

    response = requests.post("https://orcid.org/oauth/token", data=data, headers=headers)
    response.raise_for_status()
    return response.json()["access_token"]


def get_title(worksumary):
    try:
        title = worksumary[0].get("title", {}).get("title", {}).get("value", "").replace("\n", " ").strip()
        return title
    except Exception as e:
        logging.error(f"(get_title) ERROR: {e}")
        return ""  # Si no se puede obtener el título, se retorna un guion


def get_journal(worksumary):
    try:
        journal_title = worksumary[0].get("journal-title", {})
        if journal_title is None:
            return "-JOURNAL TITLE NOT FOUND-"
        journal = worksumary[0].get("journal-title", {}).get("value", "").strip()
        return journal
    except Exception as e:
        traceback.print_exc()
        logging.error(f"(get_journal) ERROR: {e}")
        return ""  # Si no se puede obtener el título, se retorna un guion


def get_date(worksumary):
    try:
        publication_date = worksumary[0].get("publication-date", {})

        year = publication_date.get("year", {})
        year = year.get("value", "") if year else ""

        month = publication_date.get("month", {})
        month = month.get("value", "") if month else ""

        day = publication_date.get("day", {})
        day = day.get("value", "") if day else ""

        date = year

        if month != "" and day != "":
            date = f"{year}-{month}-{day}"
        elif month != "":
            date = f"{year}-{month}"

        return date
    except Exception as e:
        # traceback.print_exc()
        logging.error(f"(get_date) ERROR: {e}")
        return ""  # Si no se puede obtener el título, se retorna un guion


def get_doi(worksumary):
    try:
        external_id = worksumary[0].get("external-ids", {}).get("external-id", [{}])
        if len(external_id) == 0:
            return "EXTERNAL ID NOT FOUND"
        doi = worksumary[0].get("external-ids", {}).get("external-id", [{}])[0].get("external-id-value", "")
        return doi
    except Exception as e:
        logging.error(f"(get_doi) ERROR: {e}")
        return "--"  # Si no se puede obtener el título, se retorna un guion


def get_name(personal_data):
    try:
        name = personal_data.get("name", {}).get("given-names", {}).get("value", "")
        name = name.replace("-", " ").strip()
        # print("name:", name)
        family_name = str(personal_data.get("name", {}).get("family-name", {}).get("value", ""))
        family_name = family_name.replace("-", " ").strip()

        # print("family_name:", family_name)
        return f"{name} {family_name}"
    except Exception as e:
        # traceback.print_exc()
        logging.error(f"(get_name) ERROR: {e}")
        return ""  # Si no se puede obtener el título, se retorna un guion


def get_url_source(worksumary):
    try:
        url = worksumary[0].get("url", {})
        url = url.get("value", "") if url else ""
        return url
    except Exception as e:
        logging.error(f"(get_url_source) ERROR: {e}")
        return ""  # Si no se puede obtener el título, se retorna un guion


def get_records(orcid: str, access_token: str, file_output: list):
    # print(f"Getting records for ORCID: {orcid} ")
    sys.stdout.write(f"Getting records for ORCID: {orcid} ")

    try:
        headers = {"Content-Type": "application/json", "Accept": "application/json", "Authorization": f"Bearer {access_token}"}

        url = f"https://pub.orcid.org/v3.0/{orcid}/works"
        response = requests.get(url, headers=headers)
        response.raise_for_status()

        personal_req = requests.get(f"https://pub.orcid.org/v3.0/{orcid}/person", headers=headers)
        personal_req.raise_for_status()

        personal_data = personal_req.json()

        data = response.json()
        works = data.get("group", [])

        sys.stdout.write(f"»» Found {len(works)} works\n")
        logging.info(f"INFO: Getting records for ORCID: {orcid} >> Found {len(works)} works")

        if len(works) == 0:
            logging.error(f"ERROR: No works found for ORCID: {orcid}")
            record = {"orcid_profesor": orcid, "note": "NO WORKS FOUND"}
            file_output.append(record)
            return

        for work in works:
            worksummary = work.get("work-summary")
            orcid_profesor = orcid
            title = get_title(worksummary)
            journal = get_journal(worksummary)
            date = get_date(worksummary)
            doi = get_doi(worksummary)
            url_source = get_url_source(worksummary)
            record = {
                "nombre_profesor": get_name(personal_data),
                "orcid_profesor": orcid_profesor,
                "scholar_id": "",
                "title": title,
                "journal": journal,
                "date": date,
                "doi": doi,
                "source": "ORCID",
                "note": "",
                "url_source": url_source,
            }
            file_output.append(record)

    except Exception as e:
        traceback.print_exc()
        response = getattr(e, "response", {})
        err = getattr(response, "data", {}).get("user-message", str(e)).upper()
        sys.stdout.write("»» ERROR \n")
        logging.error(f"ERROR: Getting records for ORCID: {orcid} »» {err}")
        # orcid_profesor = orcid
        # title = ""
        # journal = ""
        # date = ""
        # doi = ""
        # record = {
        #     "nombre_profesor": "",
        #     "orcid_profesor": orcid_profesor,
        #     "title": title,
        #     "journal": journal,
        #     "date": date,
        #     "doi": doi,
        #     "source": "ORCID",
        #     "note": err,
        #     "url_source": "",
        # }
        # file_output.append(record)
