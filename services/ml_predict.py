import joblib
import pandas as pd
import os

MODEL_DIR = "models"

MONTH_MAP = {
    "Jan": 1, "Feb": 2, "Mar": 3, "Apr": 4,
    "May": 5, "Jun": 6, "Jul": 7, "Aug": 8,
    "Sep": 9, "Oct": 10, "Nov": 11, "Dec": 12
}
MONTH_NAMES = ["Jan","Feb","Mar","Apr","May","Jun",
               "Jul","Aug","Sep","Oct","Nov","Dec"]

def predict_future(mineral, trade, metric, start_year, start_month, months_ahead):
    model_path = f"models/{mineral}_{metric}_{trade}.pkl"
    model = joblib.load(model_path)

    start_index = start_year * 12 + (start_month - 1)

    future_indexes = [start_index + i for i in range(months_ahead)]
    preds = model.predict([[i] for i in future_indexes])

    rows = []
    for idx, val in zip(future_indexes, preds):
        year = idx // 12
        month = MONTH_NAMES[idx % 12]

        rows.append({
            "year": year,
            "month": month,
            "predicted": round(float(val), 2)
        })

    return pd.DataFrame(rows)
