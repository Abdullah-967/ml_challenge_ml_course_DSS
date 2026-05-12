"""xgboost_v2 deepen iter3 -- single knob: + transaction_type as native cat.

Carry-forward: deepen_iter2 winner (cadastral_first kept, 53274.57).
This iter adds transaction_type as native cat.
"""

from __future__ import annotations

import numpy as np
import pandas as pd
from xgboost import XGBRegressor

TARGET_KEY = "property_value"
MODEL_FAMILY = "xgboost_v2"
FEATURE_LANE = "tier1_strong_solo"
RECIPE_VARIANT = "deepen_iter3_add_transaction_type"
PARAMS_SUMMARY = (
    "XGBRegressor(reg:absoluteerror,n_est=500,lr=0.05,max_depth=6,"
    "min_child_weight=5,subsample=0.8,colsample_bytree=0.8,reg_lambda=1.0,"
    "tree_method=hist,enable_categorical=True),tier1+geo+ttype"
)

NUMERIC_COLUMNS = ("built_area", "house_area", "area_house_5plus_rooms")
CATEGORICAL_COLUMNS = ("property_type", "commune_first", "cadastral_first", "transaction_type")


def first_token(value):
    if value is None or (isinstance(value, float) and np.isnan(value)):
        return np.nan
    text = str(value).strip()
    if not text:
        return np.nan
    return text.split(",")[0].strip()


def add_geo_first_tokens(frame):
    frame = frame.copy()
    if "commune_codes" in frame.columns:
        frame["commune_first"] = frame["commune_codes"].map(first_token)
    if "cadastral_sections" in frame.columns:
        frame["cadastral_first"] = frame["cadastral_sections"].map(first_token)
    return frame


def make_feature_frame(records, category_levels):
    frame = add_geo_first_tokens(pd.DataFrame(records))
    numeric_part = (
        frame.reindex(columns=list(NUMERIC_COLUMNS))
        .apply(pd.to_numeric, errors="coerce")
        .replace([np.inf, -np.inf], np.nan)
    )
    cat_part = pd.DataFrame(index=frame.index)
    for column in CATEGORICAL_COLUMNS:
        levels = category_levels[column]
        series = frame[column] if column in frame.columns else pd.Series([np.nan] * len(frame), index=frame.index)
        cat_part[column] = pd.Categorical(series, categories=levels)
    return pd.concat([numeric_part, cat_part], axis=1)


def fit_category_levels(records):
    frame = add_geo_first_tokens(pd.DataFrame(records))
    levels = {}
    for column in CATEGORICAL_COLUMNS:
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
        max_depth=6,
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
    category_levels = fit_category_levels(train_records)
    train_frame = make_feature_frame(train_records, category_levels)
    validation_frame = make_feature_frame(validation_records, category_levels)
    y_train = make_target_array(train_records)
    model = build_model()
    model.fit(train_frame, y_train)
    return model.predict(validation_frame)
