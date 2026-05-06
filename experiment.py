"""Auto-MAE experiment.

Iter 20: bigger HGB on log1p target. iter3 tried log1p on smaller HGB and
got -405; with the high-capacity model it may help more — log space scales
errors with magnitude, which suits skewed property prices.
"""

import numpy as np
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.ensemble import HistGradientBoostingRegressor
from sklearn.impute import SimpleImputer
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OrdinalEncoder

TARGET_KEY = "property_value"
RANDOM_STATE = 42

CATEGORICAL_FEATURES = ["commune_codes", "property_type"]


def select_numeric_features(train_records):
    df = pd.DataFrame(train_records)
    numeric = df.select_dtypes(include=["number", "bool"]).columns.tolist()
    return [c for c in numeric if c != TARGET_KEY]


def build_pipeline(numeric_features):
    numeric_pipe = SimpleImputer(strategy="median")
    categorical_pipe = Pipeline([
        ("imputer", SimpleImputer(strategy="most_frequent")),
        (
            "encoder",
            OrdinalEncoder(
                handle_unknown="use_encoded_value",
                unknown_value=-1,
            ),
        ),
    ])

    preprocessor = ColumnTransformer([
        ("num", numeric_pipe, numeric_features),
        ("cat", categorical_pipe, CATEGORICAL_FEATURES),
    ])

    cat_mask = [False] * len(numeric_features) + [True] * len(CATEGORICAL_FEATURES)

    model = HistGradientBoostingRegressor(
        loss="absolute_error",
        max_iter=1500,
        learning_rate=0.02,
        max_leaf_nodes=127,
        min_samples_leaf=20,
        l2_regularization=0.0,
        random_state=RANDOM_STATE,
        early_stopping=True,
        validation_fraction=0.15,
        n_iter_no_change=30,
        categorical_features=cat_mask,
    )

    return Pipeline([
        ("preprocessor", preprocessor),
        ("model", model),
    ])


def fit_predict(train_records, test_records):
    np.random.seed(RANDOM_STATE)
    numeric_features = select_numeric_features(train_records)
    feature_columns = numeric_features + CATEGORICAL_FEATURES

    X_train = pd.DataFrame(train_records).reindex(columns=feature_columns)
    y_train = np.array([r[TARGET_KEY] for r in train_records], dtype=np.float64)
    X_test = pd.DataFrame(test_records).reindex(columns=feature_columns)

    pipeline = build_pipeline(numeric_features)
    pipeline.fit(X_train, np.log1p(y_train))
    log_preds = pipeline.predict(X_test)
    return np.expm1(log_preds).tolist()
