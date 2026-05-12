"""XGBoost smoke recipe for the model-family MAE workflow.

Single knob this iter: feature lane = `numeric_plus_basic_cats`.
All_numeric features + low-cardinality categoricals (property_type 25 cats,
transaction_type 6 cats) added via XGBoost native categorical support
(`enable_categorical=True`). Categories fitted inside each fold via the
training-only union; unseen validation values become NaN automatically.

Family defaults (per `references/model_families.md`): reg:absoluteerror,
n_estimators=500, learning_rate=0.05, max_depth=4, min_child_weight=5,
subsample=0.8, colsample_bytree=0.8, reg_lambda=1.0, tree_method="hist".
"""

from __future__ import annotations

import numpy as np
import pandas as pd
from xgboost import XGBRegressor

TARGET_KEY = "property_value"
MODEL_FAMILY = "xgboost"
FEATURE_LANE = "numeric_plus_basic_cats"
RECIPE_VARIANT = "smoke_numeric_plus_basic_cats"
PARAMS_SUMMARY = (
    "XGBRegressor(reg:absoluteerror,n_est=500,lr=0.05,max_depth=4,"
    "min_child_weight=5,subsample=0.8,colsample_bytree=0.8,reg_lambda=1.0,"
    "tree_method=hist,enable_categorical=True),"
    "numeric_plus_basic_cats(property_type,transaction_type)"
)

ID_COLUMNS = {"parcel_ids", "transferred_parcel_ids"}
CATEGORICAL_COLUMNS = ("property_type", "transaction_type")


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


def make_feature_frame(records, numeric_columns, categorical_columns, category_levels):
    frame = pd.DataFrame(records)
    numeric_part = (
        frame.reindex(columns=numeric_columns)
        .apply(pd.to_numeric, errors="coerce")
        .replace([np.inf, -np.inf], np.nan)
    )
    cat_part = pd.DataFrame(index=frame.index)
    for column in categorical_columns:
        levels = category_levels[column]
        series = frame[column] if column in frame.columns else pd.Series([np.nan] * len(frame), index=frame.index)
        cat_part[column] = pd.Categorical(series, categories=levels)
    return pd.concat([numeric_part, cat_part], axis=1)


def fit_category_levels(records, categorical_columns):
    frame = pd.DataFrame(records)
    levels = {}
    for column in categorical_columns:
        if column in frame.columns:
            levels[column] = list(pd.Series(frame[column]).dropna().unique())
        else:
            levels[column] = []
    return levels


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
        enable_categorical=True,
    )


def fit_predict(train_records, validation_records):
    numeric_columns = infer_numeric_features(train_records)
    category_levels = fit_category_levels(train_records, CATEGORICAL_COLUMNS)
    train_frame = make_feature_frame(train_records, numeric_columns, CATEGORICAL_COLUMNS, category_levels)
    validation_frame = make_feature_frame(validation_records, numeric_columns, CATEGORICAL_COLUMNS, category_levels)
    model = build_model()
    model.fit(train_frame, make_target_array(train_records))
    return model.predict(validation_frame)
