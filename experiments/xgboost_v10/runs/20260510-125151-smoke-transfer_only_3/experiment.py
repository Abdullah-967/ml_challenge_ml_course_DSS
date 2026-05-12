"""xgboost_v10 smoke iter1 -- transfer-mode triplet (signal isolation).

Premise: explore an untouched feature axis (transferred_parcel_ids vs
parcel_ids set arithmetic) to break the ~47200 plateau. Train-set inspection
shows three transaction modes:
  - full_match (66.1%): parcel_ids == transferred_parcel_ids; median EUR 118k
  - no_transfer (32.4%): transferred_parcel_ids is "None"; median EUR 80k
  - partial    ( 1.5%): boundary cases; outlier-heavy

`no_transfer` correlates with future_sale (11.5% vs 1.0% baseline) -- mostly
off-plan sales. The 32% sub-population is currently captured weakly by
existing features.

Smoke Lane 1 (this file, baseline-3-style): pure 3-feature XGB on transfer
signal alone. No submodels, no log1p, no categoricals. Tests whether the
signal predicts in isolation analogous to xgboost_v3 baseline_three_only.

Subsequent lanes will test the same three features added to a smoke-shrunk
v6 anchor for incremental-lift measurement.
"""

from __future__ import annotations

import numpy as np
import pandas as pd
from xgboost import XGBRegressor

TARGET_KEY = "property_value"
MODEL_FAMILY = "xgboost_v10"
FEATURE_LANE = "transfer_only_3"
RECIPE_VARIANT = "smoke_iter1_transfer_only_3"
PARAMS_SUMMARY = (
    "XGBRegressor(reg:absoluteerror,n_est=500,lr=0.05,max_depth=4,"
    "min_child_weight=5,subsample=0.8,colsample_bytree=0.8,reg_lambda=1.0,"
    "tree_method=hist),transfer_only_3=[n_transferred,transfer_overlap_ratio,"
    "is_no_transfer]"
)

NUMERIC_COLUMNS = ("n_transferred", "transfer_overlap_ratio", "is_no_transfer")


def _to_id_set(value):
    if value is None:
        return set()
    if isinstance(value, float) and np.isnan(value):
        return set()
    if isinstance(value, list):
        return {
            str(x).strip()
            for x in value
            if x is not None and str(x).strip() and str(x).strip() != "None"
        }
    text = str(value).strip()
    if not text or text == "None":
        return set()
    return {tok.strip() for tok in text.split(",") if tok.strip() and tok.strip() != "None"}


def add_transfer_features(frame):
    frame = frame.copy()
    pi_sets = frame.get("parcel_ids", pd.Series([None] * len(frame))).map(_to_id_set)
    tpi_sets = frame.get(
        "transferred_parcel_ids", pd.Series([None] * len(frame))
    ).map(_to_id_set)

    n_pi = pi_sets.map(len)
    n_tpi = tpi_sets.map(len)
    inter = [len(p & t) for p, t in zip(pi_sets, tpi_sets)]
    union = [len(p | t) for p, t in zip(pi_sets, tpi_sets)]

    overlap_ratio = [
        (inter[i] / union[i]) if union[i] > 0 else np.nan for i in range(len(frame))
    ]

    frame["n_transferred"] = n_tpi.astype(float)
    frame["transfer_overlap_ratio"] = pd.Series(overlap_ratio, index=frame.index, dtype=float)
    frame["is_no_transfer"] = (n_tpi == 0).astype(float)
    return frame


def make_feature_frame(records):
    frame = add_transfer_features(pd.DataFrame(records))
    return (
        frame.reindex(columns=list(NUMERIC_COLUMNS))
        .apply(pd.to_numeric, errors="coerce")
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
