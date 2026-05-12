"""xgboost_v3 deepen iter5 -- single knob: lr=0.03 + n_est=1000 (capacity_pair).

Carry-forward W: deepen_iter4 (cv 62450.70, max_depth=4).
This iter slows learning: lr=0.05 -> 0.03, n_est=500 -> 1000.
"""

from __future__ import annotations

import numpy as np
import pandas as pd
from xgboost import XGBRegressor

TARGET_KEY = "property_value"
MODEL_FAMILY = "xgboost_v3"
FEATURE_LANE = "baseline_three_only"
RECIPE_VARIANT = "deepen_iter5_lr03_nest1000"
PARAMS_SUMMARY = (
    "XGBRegressor(reg:absoluteerror,n_est=1000,lr=0.03,max_depth=4,"
    "min_child_weight=5,subsample=0.8,colsample_bytree=0.8,reg_lambda=1.0,"
    "tree_method=hist),baseline_three_only"
)

NUMERIC_COLUMNS = ("built_area", "num_lots", "num_commercial")


def make_feature_frame(records):
    frame = pd.DataFrame(records).reindex(columns=list(NUMERIC_COLUMNS))
    return (
        frame.apply(pd.to_numeric, errors="coerce")
        .replace([np.inf, -np.inf], np.nan)
    )


def make_target_array(records):
    return np.array([record[TARGET_KEY] for record in records], dtype=np.float64)


def build_model():
    return XGBRegressor(
        objective="reg:absoluteerror",
        n_estimators=1000,
        learning_rate=0.03,
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
    train_frame = make_feature_frame(train_records)
    validation_frame = make_feature_frame(validation_records)
    y_train = make_target_array(train_records)
    model = build_model()
    model.fit(train_frame, y_train)
    return model.predict(validation_frame)
