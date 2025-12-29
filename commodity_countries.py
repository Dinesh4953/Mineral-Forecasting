import pandas as pd
import os, requests

# ---------------- CONFIG ----------------
METRIC_CONFIG = {
    "Quantity": {
        "base_dir": "Quantity",
        "file_prefix": "Country"
    },
    "Cost": {
        "base_dir": "Cost",
        "file_prefix": "Cost"
    }
}

METRIC_LABELS = {
    "Quantity": "Quantity (in KGs)",
    "Cost": "Cost (in Crores)"
}

TRADE_CONFIG = {
    "Export": {
        "2017": {"file": "2017-2018.xlsx", "column": "Jan-Dec2017 (R)"},
        "2018": {"file": "2017-2018.xlsx", "column": "Jan-Dec2018 (R)"},
        "2019": {"file": "2018-2019.xlsx", "column": "Jan-Dec2019 (R)"},
        "2020": {"file": "2020-2021.xlsx", "column": "Jan-Dec2020 (R)"},
        "2021": {"file": "2020-2021.xlsx", "column": "Jan-Dec2021 (R)"},
        "2022": {"file": "2022-2023.xlsx", "column": "Jan-Dec2022 (R)"},
        "2023": {"file": "2022-2023.xlsx", "column": "Jan-Dec2023 (R)"},
        "2024": {"file": "2024.xlsx",      "column": "Jan-Dec2024 (R)"}
    },
    "Import": {
        "2017": {"file": "2017-2018.xlsx", "column": "Jan-Dec2017 (R)"},
        "2018": {"file": "2017-2018.xlsx", "column": "Jan-Dec2018 (R)"},
        "2019": {"file": "2018-2019.xlsx", "column": "Jan-Dec2019 (R)"},
        "2020": {"file": "2020-2021.xlsx", "column": "Jan-Dec2020 (R)"},
        "2021": {"file": "2020-2021.xlsx", "column": "Jan-Dec2021 (R)"},
        "2022": {"file": "2022-2023.xlsx", "column": "Jan-Dec2022 (R)"},
        "2023": {"file": "2022-2023.xlsx", "column": "Jan-Dec2023 (R)"},
        "2024": {"file": "2024.xlsx",      "column": "Jan-Dec2024 (R)"}
    }
}

# ---------------- HELPERS ----------------
def _detect_commodity_column(df):
    """Detect commodity column safely"""
    for col in ["HS Code", "HSCode", "Commodity", "Product"]:
        if col in df.columns:
            return col
    return None


def load_and_clean_data(file_path):
    df = pd.read_excel(file_path, header=None)

    # Actual header row
    df.columns = df.iloc[2]
    df = df.iloc[3:].reset_index(drop=True)

    # Clean columns
    df = df.loc[:, df.columns.notna()]
    df.columns = (
        df.columns.astype(str)
        .str.replace(r"\s+", " ", regex=True)
        .str.strip()
    )

    # Drop junk rows
    df.drop(columns=["S.No."], inplace=True, errors="ignore")
    df = df.dropna(subset=["Country"])

    return df


# ---------------- MAIN API ----------------
def get_country_data(metric, trade_type, year, commodity=None):
    """
    Returns:
        dataframe (country-wise),
        label,
        countries (list),
        values (list)
    """

    cfg = TRADE_CONFIG[trade_type][year]
    file_name = f"{METRIC_CONFIG[metric]['file_prefix']} {cfg['file']}"
    file_path = os.path.join(
        METRIC_CONFIG[metric]["base_dir"],
        trade_type + "s",
        file_name
    )

    df = load_and_clean_data(file_path)
    
    # ---------- COMMODITY FILTER ----------
    commodity_col = _detect_commodity_column(df)
    if commodity_col and commodity:
        df = df[df[commodity_col].astype(str) == str(commodity)]

    # ---------- METRIC FILTER ----------
    col = cfg["column"]
    df[col] = pd.to_numeric(df[col], errors="coerce")
    df = df[df[col] > 0]
    df = df[~df["Country"].astype(str).str.upper().isin(["TOTAL", "TOTAL:", "GRAND TOTAL"])]
    label = METRIC_LABELS[metric]

        # -------- FINAL TABLE (WITHOUT TOTAL) --------
    result = (
        df[["Country", col]]
        .rename(columns={col: label})
        .sort_values(label, ascending=False)
        .reset_index(drop=True)
    )

    # -------- TOTAL ROW (TABLE ONLY) --------
    total_value = result[label].sum()

    total_row = {
        "Country": "TOTAL",
        label: total_value
    }

    table_with_total = pd.concat(
        [result, pd.DataFrame([total_row])],
        ignore_index=True
    )

    # -------- CHART DATA (EXCLUDE TOTAL) --------
    countries = result["Country"].tolist()
    values = result[label].tolist()

    return table_with_total, label, countries, values

