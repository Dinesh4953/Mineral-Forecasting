import pandas as pd
import os
import re

def load_time_series_data(base_path, metric, trade):
    """
    metric: 'Cost' or 'Quantity'
    trade: 'Exports' or 'Imports'
    """
    folder = os.path.join(base_path, metric, trade)

    all_dfs = []

    for file in os.listdir(folder):
        if not file.endswith(".xlsx"):
            continue

        path = os.path.join(folder, file)
        df = pd.read_excel(path)

        # 🔹 Extract years from filename
        years = re.findall(r"\d{4}", file)
        if years:
            df["year"] = df["Year"] if "Year" in df.columns else None

        df.columns = (
            df.columns.astype(str)
            .str.strip()
            .str.lower()
            .str.replace(" ", "_")
        )

        all_dfs.append(df)

    final_df = pd.concat(all_dfs, ignore_index=True)
    return final_df
