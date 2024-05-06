import os

import pandas as pd

from orcid.utils import get_credentials, get_records, logging
from scholar.utils import save_summary

root = os.path.dirname(os.path.dirname(__file__))
app_root = os.path.dirname(__file__)

orcid_summary = {
    "complete": False,
    "index": 0,
}

input_file = os.path.join(root, "input.csv")

# Lee el archivo CSV y carga solo la columna "orcid" en un DataFrame de pandas
data = pd.read_csv(input_file, usecols=["orcid"])
users: list = data["orcid"].tolist()
users = [u for u in users if str(u) != "nan" and str(u) != "-" and str(u) != ""]
output_file = os.path.join(app_root, "output.csv")
output_data = []


def orcid():
    global orcid_summary
    try:
        credentials = get_credentials()
        for user in users:
            if user != "-":
                get_records(user, credentials, output_data)
            orcid_summary["index"] += 1
            # break
        orcid_summary["complete"] = True
    except Exception as e:
        print(f"ERROR: {e}")
        logging.error(f"(orcid) ERROR: {e}")
    finally:
        df = pd.DataFrame(output_data)
        #  Remover duplicados teniendo en cuenta las columnas B y D
        df = df.drop_duplicates(subset=["orcid_profesor", "title"], keep="first")
        df.to_csv(output_file, index=False)
        # df.to_excel(os.path.join(root, "Publicaciones - ORCID.xlsx"), index=False, sheet_name="Publicaciones - ORCID")
        save_summary({"orcid": orcid_summary})
