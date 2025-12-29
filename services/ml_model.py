import joblib
from sklearn.ensemble import RandomForestRegressor

def train_model(X, y, model_name):
    model = RandomForestRegressor(
        n_estimators=300,
        random_state=42
    )
    model.fit(X, y)

    path = f"models/{model_name}.pkl"
    joblib.dump(model, path)

    return path
