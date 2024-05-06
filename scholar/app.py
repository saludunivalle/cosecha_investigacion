import json
import os
import time
import traceback
from os.path import dirname

import pandas as pd

from scholar.utils import clear, estimate_remaining_time, get_essential_data, load_temporal, save_data_on_temporal, save_scholar, save_summary

root = dirname(dirname(__file__))
app_root = dirname(__file__)

with open(os.path.join(root, "summary.json"), "r") as file:
    summary = json.load(file)

scholar_summary = summary.get("scholar", {"complete": False, "index": 0})


def scholar():
    try:
        input_file = os.path.join(root, "input.csv")

        authors: list = pd.read_csv(input_file, usecols=["author_id"])["author_id"].tolist()
        authors = [u for u in authors if str(u) != "nan"]

        time_record = []
        total_time = 0
        remaining_time = 0

        clear()
        print("Iniciando proceso de búsqueda de publicaciones...")

        time.sleep(2)
        total_time += 2

        if scholar_summary["complete"]:
            scholar_summary["complete"] = False
            scholar_summary["index"] = 0
            save_summary({"scholar": scholar_summary})

        data, authors = load_temporal(authors, scholar_summary)
        latest_index = max(len(data) - 1, 0)
        google_scholar, remaining_pub = estimate_remaining_time(authors, total_time)

        latest_index = get_essential_data(google_scholar, data, scholar_summary, remaining_pub, total_time, time_record, latest_index, remaining_time)
        scholar_summary["complete"] = True
        save_scholar(data)
    except Exception as e:
        print(f"ERROR: {e}")
        traceback.print_exc()
        save_data_on_temporal(data, latest_index)
        scholar_summary["complete"] = False
    finally:
        save_summary({"scholar": scholar_summary})
