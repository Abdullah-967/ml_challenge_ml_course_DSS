"""RandomForest smoke recipe for the model-family MAE workflow.

Stage 1 smoke iter1. Single knob: feature_lane=all_numeric.
Family entry: tree_bagging_rf (sklearn RandomForestRegressor, smoke defaults
from references/model_families.md).

Excludes parcel_ids/transferred_parcel_ids (string ID concatenations that
coerce to ~1e259 -- discovered in xgboost smoke iter1). Replaces inf->NaN.
SimpleImputer(median) handles NaN since sklearn RandomForest does not accept
NaN natively.
"""

from __future__ import annotations

import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestRegressor
from sklearn.impute import SimpleImputer
from sklearn.pipeline import Pipeline

TARGET_KEY = "property_value"
MODEL_FAMILY = "tree_bagging_rf"
FEATURE_LANE = "all_numeric"
RECIPE_VARIANT = "smoke_iter1_all_numeric"
PARAMS_SUMMARY = (
    "RandomForestRegressor(n_est=200,max_depth=18,min_samples_leaf=2,"
    "max_features=sqrt,n_jobs=-1,random_state=42),all_numeric"
)

ID_COLUMNS = {"parcel_ids", "transferred_parcel_ids"}


def infer_numeric_features(records):
    frame = pd.DataFrame(records)
    features = []
    for column in frame.columns:
        if column == TARGET_KEY or column in ID_COLUMNS:
            continue
        values = pd.to_numeric(frame[column], errors="coerce")
        if values.notna().any():
            features.append(column)
    return features


def make_feature_frame(records, feature_columns):
    frame = (
        pd.DataFrame(records)
        .reindex(columns=feature_columns)
        .apply(pd.to_numeric, errors="coerce")
        .replace([np.inf, -np.inf], np.nan)
    )
    return frame


def make_target_array(records):
    return np.array([record[TARGET_KEY] for record in records], dtype=np.float64)


def build_model():
    return Pipeline(
        [
            ("imputer", SimpleImputer(strategy="median")),
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
    feature_columns = infer_numeric_features(train_records)
    model = build_model()
    model.fit(
        make_feature_frame(train_records, feature_columns),
        make_target_array(train_records),
    )
    return model.predict(make_feature_frame(validation_records, feature_columns))
