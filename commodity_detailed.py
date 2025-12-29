import pandas as pd

DATA_PATH = "Data/Book.xlsx"   # single detailed file

def load_detailed_commodity_data():
    df = pd.read_excel(DATA_PATH)

    # Normalize column names
    df.columns = (
        df.columns
        .astype(str)
        .str.strip()
        .str.lower()
        .str.replace(" ", "_")
    )
    return df


def get_detailed_data(
    commodity,
    year,
    metric,
    selected_columns=None,
    row_limit=0
):
    df = load_detailed_commodity_data()

    # Filter commodity (note: Excel uses "commidity")
    df = df[df["commidity"].astype(str).str.lower() == commodity.lower()]

    # Filter year
    df = df[df["year"] == year]

    # Default columns by metric
    if metric.lower() == "quantity":
        default_cols = [
            "month",
            "month_quantity",
            "monthly_growth",
            "yearly_quantity",
            "yearly_growth"
        ]
        value_col = "month_quantity"
    else:
        default_cols = [
            "month",
            "monthly_cost",
            "monthly_cost_growth",
            "year_cost",
            "year_growth"
        ]
        value_col = "monthly_cost"

    # Column selection
    if selected_columns:
        keep_cols = ["month"] + [c for c in selected_columns if c in df.columns]
    else:
        keep_cols = default_cols

    df = df[keep_cols]

    # Month ordering
    if "month" in df.columns:
        df["month"] = pd.Categorical(
            df["month"],
            categories=[
                "Jan","Feb","Mar","Apr","May","Jun",
                "Jul","Aug","Sep","Oct","Nov","Dec"
            ],
            ordered=True
        )
        df = df.sort_values("month")

    # Row limit (0 = ALL)
    if row_limit > 0:
        df = df.head(row_limit)

    return df, value_col
