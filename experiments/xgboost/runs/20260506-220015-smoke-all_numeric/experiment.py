"""XGBoost smoke recipe for the model-family MAE workflow.

Single knob this iter: feature lane = `all_numeric`.
Family defaults (per `references/model_families.md`): reg:absoluteerror,
n_estimators=500, learning_rate=0.05, max_depth=4, min_child_weight=5,
subsample=0.8, colsample_bytree=0.8, reg_lambda=1.0, tree_method="hist".
XGBoost handles NaN natively, so no imputer is needed.
"""

from __future__ import annotations

import numpy as np
import pandas as pd
from xgboost import XGBRegressor

TARGET_KEY = "property_value"
MODEL_FAMILY = "xgboost"
FEATURE_LANE = "all_numeric"
RECIPE_VARIANT = "smoke_all_numeric"
PARAMS_SUMMARY = (
    "XGBRegressor(reg:absoluteerror,n_est=500,lr=0.05,max_depth=4,"
    "min_child_weight=5,subsample=0.8,colsample_bytree=0.8,reg_lambda=1.0,"
    "tree_method=hist),all_numeric"
)

# ID-like columns that coerce to numeric but produce inf-magnitude garbage
# (concatenated parcel ids). The all_numeric lane excludes IDs by definition.
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
    frame = pd.DataFrame(records).reindex(columns=feature_columns)
    frame = frame.apply(pd.to_numeric, errors="coerce")
    return frame.replace([np.inf, -np.inf], np.nan)


def make_target_array(records):
    return np.array([record[TARGET_KEY] for record in records], dtype=np.float64)


def build_model():
    return XGBRegressor(
        objective="reg:absoluteerror",
        n_estimators=500,
        learning_rate=0.05,
        max_depth=4,
        min_child_weight=5,
        subsample=0.8,
        colsample_bytree=0.8,
        reg_lambda=1.0,
        tree_method="hist",
        n_jobs=-1,
        random_state=42,
    )


def fit_predict(train_records, validation_records):
    feature_columns = infer_numeric_features(train_records)
    model = build_model()
    model.fit(
        make_feature_frame(train_records, feature_columns),
        make_target_array(train_records),
    )
    return model.predict(make_feature_frame(validation_records, feature_columns))
