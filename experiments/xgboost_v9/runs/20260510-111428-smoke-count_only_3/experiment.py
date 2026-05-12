"""xgboost_v9 smoke iter3 -- pure-count triplet.

Premise: same XGB recipe as iter1/iter2, single knob = swap feature set to
three pure-count features (num_lots, num_commercial, num_premises). Closes
the smoke triad: top-corr-mixed (Lane 1) vs pure-area (Lane 2) vs pure-count
(Lane 3). The triad tells us whether area or count signal type dominates.
"""

from __future__ import annotations

import numpy as np
import pandas as pd
from xgboost import XGBRegressor

TARGET_KEY = "property_value"
MODEL_FAMILY = "xgboost_v9"
FEATURE_LANE = "count_only_3"
RECIPE_VARIANT = "smoke_iter3_count_only_3"
PARAMS_SUMMARY = (
    "XGBRegressor(reg:absoluteerror,n_est=500,lr=0.05,max_depth=4,"
    "min_child_weight=5,subsample=0.8,colsample_bytree=0.8,reg_lambda=1.0,"
    "tree_method=hist),count_only_3=[num_lots,num_commercial,num_premises]"
)

NUMERIC_COLUMNS = ("num_lots", "num_commercial", "num_premises")


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
