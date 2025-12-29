# import pandas as pd
# import os

# BASE_DIR = "Data"


# def load_detailed_data(file_path):
#     df = pd.read_excel(file_path)

#     # Normalize column names
#     df.columns = (
#         df.columns.astype(str)
#         .str.strip()
#         .str.lower()
#         .str.replace(" ", "_")
#     )

#     # 🔥 CRITICAL FIX: convert string "nan" to real NaN
#     df = df.replace(["nan", "NaN", ""], pd.NA)

#     # Fix merged month cells
#     if "month" in df.columns:
#         df["month"] = df["month"].ffill()

#     # Drop rows where month is still missing
#     if "month" in df.columns:
#         df = df[df["month"].notna()]

#     return df

import pandas as pd

def load_detailed_data(file_path, month=None, year=None):
    df = pd.read_excel(file_path)

    # normalize column names
    df.columns = (
        df.columns.astype(str)
        .str.strip()
        .str.lower()
        .str.replace(" ", "_")
    )
    # 🔥 REMOVE DERIVED GROWTH COLUMNS COMPLETELY
    DROP_COLS = [
        "monthly_growth",
        "monthly_cost_growth"
    ]

    df = df.drop(columns=[c for c in DROP_COLS if c in df.columns])


    # remove rows where month is NaN
    df = df.dropna(subset=["month"])

    # filter by month (if user selected)
    if month is not None:
        df = df[
            df["month"].astype(str).str.strip().str.lower()
            == month.strip().lower()
        ]

    # filter by year (if user selected)
    if year is not None:
        df = df[df["year"] == year]

    return df
