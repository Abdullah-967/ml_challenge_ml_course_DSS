"""Auto-MAE experiment: port of experiments/hist_gradient_boosting notebook.

HistGradientBoostingRegressor on all numeric+boolean columns, with median
imputation. Reproduces the recipe that scored ~66,880 validation MAE on the
holdout split in the notebook.
"""

import numpy as np
import pandas as pd
from sklearn.ensemble import HistGradientBoostingRegressor
from sklearn.impute import SimpleImputer
from sklearn.pipeline import Pipeline

TARGET_KEY = "property_value"
RANDOM_STATE = 42


def select_feature_columns(train_records):
    df = pd.DataFrame(train_records)
    numeric = df.select_dtypes(include=["number", "bool"]).columns.tolist()
    return [c for c in numeric if c != TARGET_KEY]


def build_model():
    return Pipeline([
        ("imputer", SimpleImputer(strategy="median")),
        (
            "model",
            HistGradientBoostingRegressor(
                max_iter=300,
                learning_rate=0.05,
                l2_regularization=0.1,
                random_state=RANDOM_STATE,
                early_stopping=True,
            ),
        ),
    ])


def fit_predict(train_records, test_records):
    np.random.seed(RANDOM_STATE)
    feature_columns = select_feature_columns(train_records)
    X_train = pd.DataFrame(train_records)[feature_columns]
    y_train = np.array([r[TARGET_KEY] for r in train_records], dtype=np.float64)
    X_test = pd.DataFrame(test_records).reindex(columns=feature_columns)

    model = build_model()
    model.fit(X_train, y_train)
    return model.predict(X_test).tolist()
