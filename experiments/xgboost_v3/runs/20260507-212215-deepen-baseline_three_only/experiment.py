"""xgboost_v3 deepen iter1 -- single knob: log1p target transform.

Carry-forward: smoke_iter1 (cv 62517.15).
This iter wraps the target with log1p, predicts in log space, applies expm1 inverse.
"""

from __future__ import annotations

import numpy as np
import pandas as pd
from xgboost import XGBRegressor

TARGET_KEY = "property_value"
MODEL_FAMILY = "xgboost_v3"
FEATURE_LANE = "baseline_three_only"
RECIPE_VARIANT = "deepen_iter1_log1p_target"
PARAMS_SUMMARY = (
    "XGBRegressor(reg:absoluteerror,n_est=500,lr=0.05,max_depth=6,"
    "min_child_weight=5,subsample=0.8,colsample_bytree=0.8,reg_lambda=1.0,"
    "tree_method=hist),baseline_three_only,+log1p_target"
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
    )


def fit_predict(train_records, validation_records):
    train_frame = make_feature_frame(train_records)
    validation_frame = make_feature_frame(validation_records)
    y_train_raw = make_target_array(train_records)
    y_train_log = np.log1p(y_train_raw)
    model = build_model()
    model.fit(train_frame, y_train_log)
    preds_log = model.predict(validation_frame)
    return np.expm1(preds_log)
