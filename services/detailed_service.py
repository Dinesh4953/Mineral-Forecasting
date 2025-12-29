# import pandas as pd
# from .data_loader import load_detailed_data

# STATIC_GROWTH_COLUMNS = [
#     "monthly_growth",
#     "monthly_cost_growth",
#     "yearly_growth",
#     "yearly_cost_growth"
# ]

# MONTH_MAP = {
#     "january": "Jan",
#     "february": "Feb",
#     "march": "Mar",
#     "april": "Apr",
#     "may": "May",
#     "june": "Jun",
#     "july": "Jul",
#     "august": "Aug",
#     "september": "Sep",
#     "october": "Oct",
#     "november": "Nov",
#     "december": "Dec",
# }

# def get_detailed_data(
#     mineral,
#     trade,
#     year,
#     file_path,
#     selected_columns=None,
#     row_limit=0,
#     **kwargs
# ):
#     value_column = kwargs.get("value_column")

#     df = load_detailed_data(file_path)

#     # ✅ Filter year FIRST
#     if "year" in df.columns:
#         df = df[df["year"] == year]

#     # ✅ Convert string "nan" → real NaN
#     df = df.replace(["nan", "NaN", ""], pd.NA)

#     # ✅ Forward fill merged month cells
#     if "month" in df.columns:
#         df["month"] = df["month"].ffill()

#     # Drop static growth columns
#     df = df.drop(columns=[c for c in STATIC_GROWTH_COLUMNS if c in df.columns])

#     # Normalize value_column → selected_columns
#     if value_column and not selected_columns:
#         selected_columns = [value_column]

#     # Select required columns
#     if selected_columns:
#         keep_cols = ["month"] + [c for c in selected_columns if c in df.columns]
#         df = df[keep_cols]

#     # ✅ Normalize month names SAFELY
#     if "month" in df.columns:
#         df["month"] = (
#             df["month"]
#             .astype(str)
#             .str.strip()
#             .str.lower()
#             .map(MONTH_MAP)
#             .fillna(df["month"])   # 🔥 critical safety
#         )

#         # ✅ Aggregate rows per month
#         df = df.groupby("month", as_index=False).sum(numeric_only=True)

#         # Month ordering
#         df["month"] = pd.Categorical(
#             df["month"],
#             categories=[
#                 "Jan","Feb","Mar","Apr","May","Jun",
#                 "Jul","Aug","Sep","Oct","Nov","Dec"
#             ],
#             ordered=True
#         )
#         df = df.sort_values("month")

#     # Row limit
#     if row_limit > 0:
#         df = df.head(row_limit)

#     return df

# import pandas as pd
# from .data_loader import load_detailed_data

# STATIC_GROWTH_COLUMNS = [
#     "monthly_growth",
#     "monthly_cost_growth",
#     "yearly_growth",
#     "yearly_cost_growth"
# ]

# MONTH_MAP = {
#     "january": "Jan", "february": "Feb", "march": "Mar",
#     "april": "Apr", "may": "May", "june": "Jun",
#     "july": "Jul", "august": "Aug", "september": "Sep",
#     "october": "Oct", "november": "Nov", "december": "Dec"
# }

# def get_detailed_data(
#     year,
#     file_path,
#     selected_columns=None,
#     selected_months=None
# ):
#     df = load_detailed_data(file_path)

#     # Fix merged month cells
#     if "month" in df.columns:
#         df["month"] = df["month"].ffill()

#     # Normalize month names
#     df["month"] = (
#         df["month"]
#         .astype(str)
#         .str.strip()
#         .str.lower()
#         .map(MONTH_MAP)
#         .fillna(df["month"])
#     )

#     # Conditional filtering
#     if selected_months:
#         df = df[df["month"].isin(selected_months)]
#     else:
#         df = df[df["year"] == year]

#     # Remove static growth columns
#     df = df.drop(columns=[c for c in STATIC_GROWTH_COLUMNS if c in df.columns])

#     # Column filtering
#     if selected_columns:
#         keep_cols = ["month", "year"] + [
#             c for c in selected_columns if c in df.columns
#         ]
#         df = df[keep_cols]

#     # ✅ FIXED AGGREGATION
#     if selected_months:
#         df = df.groupby(["month", "year"], as_index=False).sum(numeric_only=True)
#     else:
#         df = df.groupby("month", as_index=False).sum(numeric_only=True)

#     # Month ordering (only needed when month shown as axis)
#     if "month" in df.columns:
#         df["month"] = pd.Categorical(
#             df["month"],
#             categories=[
#                 "Jan","Feb","Mar","Apr","May","Jun",
#                 "Jul","Aug","Sep","Oct","Nov","Dec"
#             ],
#             ordered=True
#         )

#     return df.sort_values(["month", "year"] if selected_months else "month")

import pandas as pd
from .data_loader import load_detailed_data

MONTH_MAP = {
    "january": "Jan", "february": "Feb", "march": "Mar",
    "april": "Apr", "may": "May", "june": "Jun",
    "july": "Jul", "august": "Aug", "september": "Sep",
    "october": "Oct", "november": "Nov", "december": "Dec"
}

def get_detailed_data(year, file_path, selected_columns=None, selected_months=None):

    df = load_detailed_data(file_path)

    df["month"] = (
        df["month"]
        .astype(str)
        .str.strip()
        .str.lower()
        .map(MONTH_MAP)
        .fillna(df["month"])
    )

    # filtering
    if selected_months:
        df = df[df["month"].isin(selected_months)]
    else:
        df = df[df["year"] == year]

    if selected_columns:
        df = df[["month", "year"] + selected_columns]

    # aggregation
    if selected_months:
        df = df.groupby(["month", "year"], as_index=False).sum(numeric_only=True)
    else:
        df = df.groupby("month", as_index=False).sum(numeric_only=True)

    df["month"] = pd.Categorical(
        df["month"],
        categories=["Jan","Feb","Mar","Apr","May","Jun",
                    "Jul","Aug","Sep","Oct","Nov","Dec"],
        ordered=True
    )

    return df.sort_values("month")
