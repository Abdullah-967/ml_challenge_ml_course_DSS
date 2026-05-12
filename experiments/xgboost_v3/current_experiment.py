"""xgboost_v3 smoke iter1 -- XGBoost on the Ridge baseline's 3 features only.

Family premise: test whether XGBoost trained on ONLY the 3 features used in the
project's Ridge baseline (built_area, num_lots, num_commercial) can perform
competitively. This is the family's defining constraint -- the smoke stage
runs a single lane (`baseline_three_only`) rather than three lanes because the
hypothesis IS the feature set.

Single-knob discipline: subsequent iters in this family change exactly one knob.
"""

from __future__ import annotations

import numpy as np
import pandas as pd
from xgboost import XGBRegressor

TARGET_KEY = "property_value"
MODEL_FAMILY = "xgboost_v3"
FEATURE_LANE = "baseline_three_only"
RECIPE_VARIANT = "deepen_iter9_max_depth_2"
PARAMS_SUMMARY = (
    "XGBRegressor(reg:absoluteerror,n_est=500,lr=0.05,max_depth=2,"
    "min_child_weight=5,subsample=0.8,colsample_bytree=1.0,reg_lambda=1.0,"
    "tree_method=hist),baseline_three_only=[built_area,num_lots,num_commercial]"
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
        max_depth=2,
        min_child_weight=5,
        subsample=0.8,
        colsample_bytree=1.0,
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
