import subprocess
subprocess.run(["pip", "install", "pandas", "scikit-learn", "requests"], check=True)

import os
import tarfile
import requests
import urllib3
import pandas as pd

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

BASE_URL = "https://www2.aueb.gr/users/ion/data/enron-spam/preprocessed/"
DATASETS = ["enron1", "enron3", "enron4", "enron5", "enron6"]
SAVE_DIR = "data"
os.makedirs(SAVE_DIR, exist_ok=True)

emails = []

for name in DATASETS:
    print(f"Baixando {name}...")
    url = BASE_URL + name + ".tar.gz"
    tar_path = os.path.join(SAVE_DIR, name + ".tar.gz")

    r = requests.get(url, stream=True, verify=False)
    with open(tar_path, "wb") as f:
        for chunk in r.iter_content(chunk_size=8192):
            f.write(chunk)

    with tarfile.open(tar_path, "r:gz") as tar:
        tar.extractall(SAVE_DIR)

    for label, folder in [(1, "spam"), (0, "ham")]:
        folder_path = os.path.join(SAVE_DIR, name, folder)
        if not os.path.exists(folder_path):
            continue
        for fname in os.listdir(folder_path):
            fpath = os.path.join(folder_path, fname)
            try:
                with open(fpath, "r", encoding="utf-8", errors="ignore") as f:
                    emails.append({"text": f.read(), "label": label})
            except:
                pass

    print(f"{name} ok!")

df = pd.DataFrame(emails)
df.to_csv(os.path.join(SAVE_DIR, "dataset.csv"), index=False)
print(f"\nDataset salvo! Total de emails: {len(df)}")
print(df["label"].value_counts())