import csv
import json
import os
import random
import time
from difflib import SequenceMatcher
from os.path import dirname

import pandas as pd
from scholarly import ProxyGenerator, scholarly

root = dirname(dirname(__file__))
app_root = dirname(__file__)

clear = lambda: os.system("cls")

scraper_api_keys = ["f21beb7677b41063064a7e73ca3995dc", "d98e42fe84e51b774e5ee4776800af96", "5366a9e7706cecf43af0869353a7990a"]
proxies = [ProxyGenerator().FreeProxies(), ProxyGenerator().ScraperAPI(random.choice(scraper_api_keys))]
scholarly.use_proxy(*proxies)


def load_temporal(authors: list, scholar_summary: dict):
    try:
        data = []
        authors = authors.copy()

        if scholar_summary["index"] > 0:
            with open(os.path.join(root, "temporal.json"), "r") as temp_data:
                data = json.load(temp_data)
                authors = authors[scholar_summary["index"] :]
                # authors = authors[0:1]

        return (data, authors)
    except Exception as e:
        return ([], authors)


def get_orcid_dict():
    orcid_file = os.path.join(root, "orcid", "output.csv")
    orcid = pd.read_csv(orcid_file, usecols=["nombre_profesor", "title"])
    orcid_dict: dict = {"name-title": {}, "title-name": {}}
    for _, row in orcid.iterrows():
        name = str(row["nombre_profesor"]).lower()
        title = str(row["title"]).lower()
        orcid_dict["name-title"].setdefault(name, []).append(title)
        orcid_dict["title-name"].setdefault(title, []).append(name)
    return orcid_dict


def estimate_remaining_time(authors: list, total_time):
    orcid_dict = get_orcid_dict()
    google_scholar = []
    remaining_pub = 0

    for author_user in authors:
        start = time.time()
        search_query = scholarly.search_author_id(author_user, filled=True)
        author = search_query

        author_name = author.get("name")

        publications = author["publications"].copy()

        for pub in publications:
            pub_title = pub.get("bib").get("title")

            dict_name = orcid_dict.get("name-title").get(author_name.lower(), False)
            dict_title = orcid_dict.get("title-name").get(pub_title.lower(), False)

            if dict_name and pub_title in dict_name:
                remove_element(author["publications"], pub_title)
            elif dict_title:
                for name_user in dict_title:
                    if similar(name_user, author_name) > 0.7:
                        remove_element(author["publications"], pub_title)

        google_scholar.append(author)
        publications = author["publications"]

        clear()
        total_time += time.time() - start
        print("Calculando tiempo restante...")
        print(f"Tiempo transcurrido: {get_time(total_time)}")
        remaining_pub += len(publications)
    return google_scholar, remaining_pub


def get_essential_data(google_scholar, data, scholar_summary, remaining_pub, total_time, time_record, latest_index, remaining_time):
    try:
        for user in google_scholar:
            publications = user["publications"]
            for pub in publications:
                start_pub = time.time()
                publication: dict = scholarly.fill(pub)
                publication_bib: dict = publication.get("bib")

                remaining_pub -= 1
                actual_pub = publication_bib.get("title")

                pub_time = time.time() - start_pub
                time_record.append(pub_time)
                data.append(
                    {
                        "nombre_profesor": user["name"],
                        "orcid_profesor": "",
                        "scholar_id": user["scholar_id"],
                        "title": actual_pub,
                        "journal": publication_bib.get("journal"),
                        "date": publication_bib.get("pub_year"),
                        "doi": publication.get("author_pub_id"),
                        "source": "Google Scholar",
                        "note": "",
                        "url_source": publication.get("pub_url"),
                    }
                )
                total_time += pub_time
                remaining_time = (sum(time_record) / len(time_record)) * remaining_pub

                clear()
                print("Usuario: {}\tPublicación: {}".format(user["name"], (actual_pub[slice(0, 45)] + "...")))
                print("Tiempo transcurrido: {} \tTiempo estimado: {}".format(get_time(total_time), get_time(remaining_time)))
                print(f"Usuarios restantes: {len(google_scholar) - google_scholar.index(user)} \tPublicaciones restantes: {remaining_pub}")
            clear()
            if remaining_pub > 0:
                print("Buscando publicaciones del usuario siguiente...")
                print("Tiempo transcurrido: {}\tTiempo estimado: {}".format(get_time(total_time), get_time(remaining_time)))
            else:
                print(f"Proceso completado en {get_time(total_time)}.")
                print("Tiempo promedio por publicación: {:.2f} segundos".format(sum(time_record) / len(time_record)))
            scholar_summary["index"] += 1
            latest_index = len(data) - 1
    except Exception as e:
        print(f"ERROR: {e}")
    finally:
        return latest_index


def save_summary(summary_dict: dict):
    # abrir el archivo summary.json en modo lectura
    with open(os.path.join(root, "summary.json"), "r") as file:
        summary = json.load(file)

    # actualizar los datos con el resumen de ORCID
    summary.update(summary_dict)

    # abrir el archivo summary.json en modo escritura
    with open(os.path.join(root, "summary.json"), "w") as file:
        json.dump(summary, file, indent=4)


def save_scholar(data: list):
    orcid_file = os.path.join(root, "orcid", "output.csv")
    orcid_data = []

    with open(orcid_file, "r", newline="", encoding="utf-8") as archivo_csv:
        lector_csv = csv.DictReader(archivo_csv)
        for fila in lector_csv:
            orcid_data.append(dict(fila))

    orcid = pd.DataFrame(orcid_data)
    orcid = orcid.fillna("")
    orcid = orcid.astype({"date": str, "url_source": str})

    scholar = pd.DataFrame(data)
    scholar = scholar.drop_duplicates(subset=["scholar_id", "title"], keep="first")
    scholar = scholar.fillna("")
    scholar = scholar.astype({"date": str, "url_source": str})

    data.extend(orcid_data)

    combined = pd.DataFrame(data)
    combined = combined.drop_duplicates(subset=["orcid_profesor", "scholar_id", "title"], keep="first")
    combined = combined.fillna("")
    combined = combined.astype({"date": str, "url_source": str})

    with pd.ExcelWriter(os.path.join(root, "Publicaciones.xlsx"), engine="xlsxwriter") as writer:
        scholar.to_excel(writer, index=False, sheet_name="Publicaciones - Google Scholar")
        orcid.to_excel(writer, index=False, sheet_name="Publicaciones - ORCID")
        combined.to_excel(writer, index=False, sheet_name="Publicaciones - ORCID + Scholar")

    # writer.save()


def save_data_on_temporal(data, index):
    d = data[0:index]
    if len(d) > 0:
        with open(os.path.join(root, "temporal.json"), "w") as temp_save:
            json.dump(d, temp_save, indent=4)
    else:
        with open(os.path.join(root, "temp"), "w") as temp_save:
            json.dump(data, temp_save, indent=4)


def remove_element(lst, title):
    for i, value in enumerate(lst):
        if value["bib"]["title"] == title:
            lst.pop(i)
            break


def similar(a: str, b: str):
    a = a.lower()
    b = b.lower()
    return SequenceMatcher(None, a, b).ratio()


def get_time(seconds):
    minutes, seconds = divmod(seconds, 60)
    hours, minutes = divmod(minutes, 60)
    return "{:.0f} h {:.0f} m {:.2f} s".format(hours, minutes, seconds) if hours > 0 else "{:.0f} m {:.2f} s".format(minutes, seconds) if minutes > 0 else "{:.2f} s".format(seconds)
