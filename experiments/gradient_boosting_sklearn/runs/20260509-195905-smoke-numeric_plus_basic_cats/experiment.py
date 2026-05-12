"""sklearn GradientBoostingRegressor smoke lane B (numeric_plus_basic_cats).

One-knob change vs lane A anchor: feature scope only -- add fold-safe one-hot
encoding of low-cardinality categoricals (property_type, transaction_type) on
top of the all_numeric features. Model hyperparameters are identical to the
anchor.
"""

from __future__ import annotations

import numpy as np
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.ensemble import GradientBoostingRegressor
from sklearn.impute import SimpleImputer
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder

TARGET_KEY = "property_value"
MODEL_FAMILY = "gradient_boosting_sklearn"
FEATURE_LANE = "numeric_plus_basic_cats"
RECIPE_VARIANT = "smoke_numeric_plus_basic_cats"
PARAMS_SUMMARY = (
    "GBR(loss=absolute_error,n_est=100,lr=0.1,max_depth=3,subsample=0.8),"
    "numeric_plus_basic_cats,ohe(property_type+transaction_type)"
)

DROP_FROM_NUMERIC = {
    "region_code",
    "parcel_ids",
    "transferred_parcel_ids",
    "commune_codes",
    "cadastral_sections",
}

CATEGORICAL_FEATURES = ["property_type", "transaction_type"]


def infer_numeric_features(records):
    frame = pd.DataFrame(records)
    features = []
    for column in frame.columns:
        if column == TARGET_KEY or column in DROP_FROM_NUMERIC:
            continue
        if column in CATEGORICAL_FEATURES:
            continue
        values = pd.to_numeric(frame[column], errors="coerce")
        if values.notna().any():
            features.append(column)
    return features


def make_feature_frame(records, numeric_columns):
    frame = pd.DataFrame(records)
    numeric = frame.reindex(columns=numeric_columns).apply(pd.to_numeric, errors="coerce")
    categorical = frame.reindex(columns=CATEGORICAL_FEATURES).astype(object).fillna("__missing__")
    return pd.concat([numeric, categorical], axis=1)


def make_target_array(records):
    return np.array([record[TARGET_KEY] for record in records], dtype=np.float64)


def build_model(numeric_columns):
    preprocessor = ColumnTransformer(
        transformers=[
            ("numeric", SimpleImputer(strategy="median"), numeric_columns),
            (
                "categorical",
                OneHotEncoder(handle_unknown="ignore", sparse_output=False),
                CATEGORICAL_FEATURES,
            ),
        ],
        remainder="drop",
    )
    return Pipeline(
        [
            ("preprocessor", preprocessor),
            (
                "model",
                GradientBoostingRegressor(
                    loss="absolute_error",
                    n_estimators=100,
                    learning_rate=0.1,
                    max_depth=3,
                    subsample=0.8,
                    random_state=42,
                ),
            ),
        ]
    )


def fit_predict(train_records, validation_records):
    numeric_columns = infer_numeric_features(train_records)
    model = build_model(numeric_columns)
    model.fit(
        make_feature_frame(train_records, numeric_columns),
        make_target_array(train_records),
    )
    return model.predict(make_feature_frame(validation_records, numeric_columns))
