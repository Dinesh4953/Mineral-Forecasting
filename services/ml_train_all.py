import pandas as pd
import joblib
import os
from sklearn.linear_model import LinearRegression

DATA_DIR = "Data"
MODEL_DIR = "models"

os.makedirs(MODEL_DIR, exist_ok=True)

METRICS = {
    "month_quantity": "quantity",
    "monthly_cost": "cost"
}

TRADES = ["export", "import"]

def train_and_save(file_path, mineral, trade, target_col, metric_name):
    df = pd.read_excel(file_path)

    df.columns = (
        df.columns.astype(str)
        .str.strip()
        .str.lower()
        .str.replace(" ", "_")
    )

    # ---- CLEAN NUMERIC TARGET ----
    df[target_col] = (
        df[target_col]
        .astype(str)
        .str.replace(",", "", regex=False)
        .str.replace("\t", "", regex=False)
        .str.strip()
    )

    df[target_col] = pd.to_numeric(df[target_col], errors="coerce")

    # Drop invalid rows
    df = df.dropna(subset=[target_col, "year", "month"])

    if df.empty:
        print(f"⚠️ No valid data for {mineral} {trade} {metric_name}")
        return

    # Create time index
    df["month_index"] = df["year"] * 12 + df["month"].astype("category").cat.codes

    X = df[["month_index"]]
    y = df[target_col]

    model = LinearRegression()
    model.fit(X, y)

    model_name = f"{mineral}_{metric_name}_{trade}.pkl"
    model_path = os.path.join(MODEL_DIR, model_name)

    joblib.dump(model, model_path)
    print(f"✅ Saved: {model_path}")


# =======================
# 🚀 MAIN EXECUTION LOOP
# =======================
if __name__ == "__main__":

    for mineral in os.listdir(DATA_DIR):
        mineral_path = os.path.join(DATA_DIR, mineral)

        if not os.path.isdir(mineral_path):
            continue

        for trade in TRADES:
            file_path = os.path.join(
                mineral_path,
                f"{mineral.lower()}_{trade}.xlsx"
            )

            if not os.path.exists(file_path):
                print(f"❌ Missing file: {file_path}")
                continue

            for col, metric_name in METRICS.items():
                train_and_save(
                    file_path=file_path,
                    mineral=mineral.lower(),
                    trade=trade,
                    target_col=col,
                    metric_name=metric_name
                )
