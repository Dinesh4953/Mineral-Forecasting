import pandas as pd

# def calculate_growth(
#     df,
#     value_column,
#     start_month=None,
#     end_month=None,
#     start_year=None,
#     end_year=None
# ):
#     old_value = None
#     new_value = None

#     if start_month and end_month:
#         old_value = df[df["month"] == start_month][value_column].sum()
#         new_value = df[df["month"] == end_month][value_column].sum()

#     elif start_year and end_year:
#         old_value = df[df["year"] == start_year][value_column].sum()
#         new_value = df[df["year"] == end_year][value_column].sum()

#     if old_value is None or old_value == 0:
#         return None

#     growth = ((new_value - old_value) / old_value) * 100
#     return round(growth, 2)

def calculate_growth(old, new):
    if old is None or old == 0:
        return None
    return round(((new - old) / old) * 100, 2)
