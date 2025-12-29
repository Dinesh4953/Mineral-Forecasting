import pandas as pd

MONTH_MAP = {
    "january": 1, "february": 2, "march": 3,
    "april": 4, "may": 5, "june": 6,
    "july": 7, "august": 8, "september": 9,
    "october": 10, "november": 11, "december": 12,
    "jan": 1, "feb": 2, "mar": 3,
    "apr": 4, "jun": 6, "jul": 7,
    "aug": 8, "sep": 9, "oct": 10,
    "nov": 11, "dec": 12
}

def standardize_dataframe(df, value_column):
    """
    value_column → cost or quantity column name
    """

    df = df.copy()

    # normalize column names
    df.columns = (
        df.columns.astype(str)
        .str.strip()
        .str.lower()
        .str.replace(" ", "_")
    )

    # normalize month
    df["month_num"] = (
        df["month"]
        .astype(str)
        .str.lower()
        .map(MONTH_MAP)
    )

    # drop invalid rows
    df = df.dropna(subset=["year", "month_num", value_column])

    df["year"] = df["year"].astype(int)
    df["month_num"] = df["month_num"].astype(int)

    return df

def create_time_features(df, value_column):
    """
    Creates ML-ready features
    """

    df = df.sort_values(["year", "month_num"]).reset_index(drop=True)

    # continuous time index
    df["time_index"] = df["year"] * 12 + df["month_num"]

    # lag features
    df["lag_1"] = df[value_column].shift(1)
    df["lag_3"] = df[value_column].shift(3)
    df["lag_12"] = df[value_column].shift(12)

    # rolling mean
    df["roll_3"] = df[value_column].rolling(3).mean()
    df["roll_6"] = df[value_column].rolling(6).mean()

    df = df.dropna()

    X = df[
        ["time_index", "lag_1", "lag_3", "lag_12", "roll_3", "roll_6"]
    ]
    y = df[value_column]

    return X, y, df
