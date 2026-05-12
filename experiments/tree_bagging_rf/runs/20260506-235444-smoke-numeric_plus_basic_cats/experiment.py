"""RandomForest smoke iter2 recipe.

Stage 1 smoke iter2. Single-knob lane swap: numeric_plus_basic_cats =
all_numeric + OHE(property_type, transaction_type). Tests low-cardinality
categorical lift on RF (no native cat support, so explicit one-hot).
"""

from __future__ import annotations

import numpy as np
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.ensemble import RandomForestRegressor
from sklearn.impute import SimpleImputer
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder

TARGET_KEY = "property_value"
MODEL_FAMILY = "tree_bagging_rf"
FEATURE_LANE = "numeric_plus_basic_cats"
RECIPE_VARIANT = "smoke_iter2_numeric_plus_basic_cats"
PARAMS_SUMMARY = (
    "RandomForestRegressor(n_est=200,max_depth=18,min_samples_leaf=2,"
    "max_features=sqrt,n_jobs=-1,random_state=42),"
    "all_numeric+OHE(property_type,transaction_type)"
)

ID_COLUMNS = {"parcel_ids", "transferred_parcel_ids"}
CATEGORICAL_COLUMNS = ("property_type", "transaction_type")
MISSING_TOKEN = "__missing__"


def infer_numeric_features(records):
    frame = pd.DataFrame(records)
    features = []
    for column in frame.columns:
        if column == TARGET_KEY or column in ID_COLUMNS:
            continue
        if column in CATEGORICAL_COLUMNS:
            continue
        values = pd.to_numeric(frame[column], errors="coerce")
        if values.notna().any():
            features.append(column)
    return features


def make_feature_frame(records, numeric_columns, categorical_columns):
    frame = pd.DataFrame(records)
    numeric = (
        frame.reindex(columns=numeric_columns)
        .apply(pd.to_numeric, errors="coerce")
        .replace([np.inf, -np.inf], np.nan)
    )
    cat = frame.reindex(columns=list(categorical_columns)).astype(object)
    for col in cat.columns:
        cat[col] = cat[col].where(cat[col].notna(), MISSING_TOKEN).astype(str)
    return pd.concat([numeric, cat], axis=1)


def make_target_array(records):
    return np.array([record[TARGET_KEY] for record in records], dtype=np.float64)


def build_model(numeric_columns, categorical_columns):
    preprocessor = ColumnTransformer(
        transformers=[
            ("num", SimpleImputer(strategy="median"), list(numeric_columns)),
            (
                "cat",
                OneHotEncoder(handle_unknown="ignore", sparse_output=False),
                list(categorical_columns),
            ),
        ]
    )
    return Pipeline(
        [
            ("preprocessor", preprocessor),
            (
                "model",
                RandomForestRegressor(
                    n_estimators=200,
                    max_depth=18,
                    min_samples_leaf=2,
                    max_features="sqrt",
                    n_jobs=-1,
                    random_state=42,
                ),
            ),
        ]
    )


def fit_predict(train_records, validation_records):
    numeric_columns = infer_numeric_features(train_records)
    train_frame = make_feature_frame(train_records, numeric_columns, CATEGORICAL_COLUMNS)
    validation_frame = make_feature_frame(validation_records, numeric_columns, CATEGORICAL_COLUMNS)
    model = build_model(numeric_columns, CATEGORICAL_COLUMNS)
    model.fit(train_frame, make_target_array(train_records))
    return model.predict(validation_frame)
