"""xgboost_v9 deepen iter1 -- backward-selection anchor (10-feature pool).

Smoke takeaway: built_area is the keystone (Lane 2 area-only 61254 ties Lane 1
top-corr 62279 within noise; Lane 3 count-only 72561 collapses). To search
beyond the 3-feature regime via backward selection, this iter establishes the
anchor MAE on a 10-feature pool selected from mfm analyze: one representative
per redundancy group plus the top non-redundant target-correlated features.

Pool: built_area, land_area, house_area, apartment_area, num_lots,
num_commercial, num_apt_2_rooms, num_house_2_rooms, year, month.

Subsequent deepen iters drop exactly one feature each (one-knob discipline)
and compare delta MAE against this anchor. Features whose removal improves or
ties within noise become candidates for permanent removal.
"""

from __future__ import annotations

import numpy as np
import pandas as pd
from xgboost import XGBRegressor

TARGET_KEY = "property_value"
MODEL_FAMILY = "xgboost_v9"
FEATURE_LANE = "backward_select_drop_num_lots"
RECIPE_VARIANT = "deepen_iter6_drop_num_lots"
PARAMS_SUMMARY = (
    "XGBRegressor(reg:absoluteerror,n_est=500,lr=0.05,max_depth=4,"
    "min_child_weight=5,subsample=0.8,colsample_bytree=0.8,reg_lambda=1.0,"
    "tree_method=hist),pool9_drop_num_lots"
)

NUMERIC_COLUMNS = (
    "built_area",
    "land_area",
    "house_area",
    "apartment_area",
    "num_commercial",
    "num_apt_2_rooms",
    "num_house_2_rooms",
    "year",
    "month",
)


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
