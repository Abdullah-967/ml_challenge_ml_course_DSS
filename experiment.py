"""Auto-MAE experiment.

Iter 21: iter20 (bigger HGB on log1p target) + structural ratios.
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

ROOM_COUNT_COLS = [
    "num_apt_1_room", "num_apt_2_rooms", "num_apt_3_rooms",
    "num_apt_4_rooms", "num_apt_5plus_rooms",
    "num_house_1_room", "num_house_2_rooms", "num_house_3_rooms",
    "num_house_4_rooms", "num_house_5plus_rooms",
]


def add_ratio_features(df):
    df = df.copy()
    rooms = df.reindex(columns=ROOM_COUNT_COLS).fillna(0).sum(axis=1)
    df["total_rooms"] = rooms
    built = df.get("built_area", pd.Series(np.nan, index=df.index))
    land = df.get("land_area", pd.Series(np.nan, index=df.index))
    premises = df.get("num_premises", pd.Series(np.nan, index=df.index))
    houses = df.get("num_houses", pd.Series(np.nan, index=df.index))
    apts = df.get("num_apartments", pd.Series(np.nan, index=df.index))
    df["built_per_room"] = built / (rooms + 1.0)
    df["area_per_lot"] = built / (land.fillna(0) + 1.0)
    df["house_share"] = houses / (premises.fillna(0) + 1.0)
    df["apt_share"] = apts / (premises.fillna(0) + 1.0)
    return df


def select_numeric_features(train_records):
    df = add_ratio_features(pd.DataFrame(train_records))
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

    X_train = add_ratio_features(pd.DataFrame(train_records)).reindex(columns=feature_columns)
    y_train = np.array([r[TARGET_KEY] for r in train_records], dtype=np.float64)
    X_test = add_ratio_features(pd.DataFrame(test_records)).reindex(columns=feature_columns)

    pipeline = build_pipeline(numeric_features)
    pipeline.fit(X_train, np.log1p(y_train))
    log_preds = pipeline.predict(X_test)
    return np.expm1(log_preds).tolist()
