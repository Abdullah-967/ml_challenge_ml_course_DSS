"""xgboost_v9 smoke iter1 -- top-target-correlation triplet (first principles).

Premise: approach the problem from first principles via mfm_cli.py analyze.
Analyze (hybrid) reported the top non-redundant marginal target correlations as
built_area (0.55), num_lots (0.38), num_commercial (0.34). The remaining
features drop to |r| < 0.17. Smoke Lane 1 tests this minimal first-principles
triplet as a 3-feature anchor analogous to baseline.

Single-knob discipline: subsequent iters change exactly one knob -- one
feature, one hyperparameter, or one preprocessing step. Update the constants
below before each new run.
"""

from __future__ import annotations

import numpy as np
import pandas as pd
from xgboost import XGBRegressor

TARGET_KEY = "property_value"
MODEL_FAMILY = "xgboost_v9"
FEATURE_LANE = "top_target_corr_3"
RECIPE_VARIANT = "smoke_iter1_top_target_corr_3"
PARAMS_SUMMARY = (
    "XGBRegressor(reg:absoluteerror,n_est=500,lr=0.05,max_depth=4,"
    "min_child_weight=5,subsample=0.8,colsample_bytree=0.8,reg_lambda=1.0,"
    "tree_method=hist),top_target_corr_3=[built_area,num_lots,num_commercial]"
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
