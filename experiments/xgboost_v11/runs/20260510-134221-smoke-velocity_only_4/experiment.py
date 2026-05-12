"""xgboost_v11 smoke iter1 -- commune-time velocity (signal isolation).

Premise: explore axis B (commune-time market velocity) to break the v6/v7
plateau. v10 ruled out transferred_parcel_ids (axis A). Inspection shows
64 communes spanning 2014-2021, with median gap of 1 day in active communes;
mean price differs by 76k between active (>=50 txns) and quiet communes --
a real intensity signal not captured by `commune_first` alone (which encodes
identity but not temporal density).

Fold-safe construction: history per commune is built from the TRAINING fold
only. For each row, lookup uses dates STRICTLY LESS than the row's own date,
so training rows naturally exclude themselves and validation rows see only
training-fold history.

Smoke Lane 1 (this file, baseline-3-style): pure XGB on 4 velocity features.
Tests whether commune-time density predicts in isolation. Lanes 2/3 will
re-anchor and measure incremental lift on the shrunk v6 recipe.
"""

from __future__ import annotations

import numpy as np
import pandas as pd
from xgboost import XGBRegressor

TARGET_KEY = "property_value"
MODEL_FAMILY = "xgboost_v11"
FEATURE_LANE = "velocity_only_4"
RECIPE_VARIANT = "smoke_iter1_velocity_only_4"
PARAMS_SUMMARY = (
    "XGBRegressor(reg:absoluteerror,n_est=500,lr=0.05,max_depth=4,"
    "min_child_weight=5,subsample=0.8,colsample_bytree=0.8,reg_lambda=1.0,"
    "tree_method=hist),velocity_only_4=[n_txns_prev_60d,n_txns_prev_180d,"
    "avg_built_area_prev_60d,days_since_last_txn]"
)
DATE_EPOCH = pd.Timestamp("2014-01-01")
WIN_60 = 60
WIN_180 = 180
NO_PRIOR_DAYS = 9999.0  # sentinel for "no prior transaction in commune"

NUMERIC_COLUMNS = (
    "n_txns_prev_60d",
    "n_txns_prev_180d",
    "avg_built_area_prev_60d",
    "days_since_last_txn",
)


def first_token(value):
    if value is None or (isinstance(value, float) and np.isnan(value)):
        return None
    text = str(value).strip()
    if not text or text == "None":
        return None
    return text.split(",")[0].strip()


def make_target_array(records):
    return np.array([record[TARGET_KEY] for record in records], dtype=np.float64)


def _extract_commune_date_built(records):
    df = pd.DataFrame(records)
    commune = df.get("commune_codes", pd.Series([None] * len(df))).map(first_token)
    raw_date = (
        df.get("transaction_date", pd.Series([None] * len(df)))
        .astype(str)
        .str.split(",")
        .str[0]
        .str.strip()
    )
    parsed = pd.to_datetime(raw_date, errors="coerce")
    date_ord = (parsed - DATE_EPOCH).dt.days.astype("Float64")
    built = pd.to_numeric(df.get("built_area"), errors="coerce")
    return commune.values, date_ord.to_numpy(dtype=float, na_value=np.nan), built.to_numpy(dtype=float, na_value=np.nan)


def build_history(train_records):
    """Build per-commune sorted (date_ord, built_area) arrays from training fold only."""
    communes, dates, builts = _extract_commune_date_built(train_records)
    history = {}
    df = pd.DataFrame({"c": communes, "d": dates, "b": builts}).dropna(subset=["c", "d"])
    for c, sub in df.groupby("c"):
        sub_sorted = sub.sort_values("d")
        history[c] = (sub_sorted["d"].to_numpy(), sub_sorted["b"].to_numpy())
    return history


def velocity_features(records, history):
    """Compute 4 velocity features for each row using the per-commune training history.

    Lookup is strictly less-than the row's own date, so rows in the training
    fold naturally exclude themselves.
    """
    communes, dates, _ = _extract_commune_date_built(records)
    n_60 = np.full(len(records), np.nan)
    n_180 = np.full(len(records), np.nan)
    avg_60 = np.full(len(records), np.nan)
    days_since = np.full(len(records), np.nan)

    for i, (c, d) in enumerate(zip(communes, dates)):
        if c is None or pd.isna(d) or c not in history:
            continue
        h_dates, h_builts = history[c]
        idx = np.searchsorted(h_dates, d, side="left")  # h_dates[0:idx] < d
        if idx == 0:
            n_60[i] = 0
            n_180[i] = 0
            days_since[i] = NO_PRIOR_DAYS
            continue
        win60_lo = np.searchsorted(h_dates[:idx], d - WIN_60, side="left")
        win180_lo = np.searchsorted(h_dates[:idx], d - WIN_180, side="left")
        n_60[i] = idx - win60_lo
        n_180[i] = idx - win180_lo
        if n_60[i] > 0:
            window = h_builts[win60_lo:idx]
            valid = window[~np.isnan(window)]
            avg_60[i] = float(np.mean(valid)) if valid.size else np.nan
        days_since[i] = d - h_dates[idx - 1]

    return pd.DataFrame(
        {
            "n_txns_prev_60d": n_60,
            "n_txns_prev_180d": n_180,
            "avg_built_area_prev_60d": avg_60,
            "days_since_last_txn": days_since,
        }
    )


def make_feature_frame(records, history):
    return velocity_features(records, history).reindex(columns=list(NUMERIC_COLUMNS))


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
    history = build_history(train_records)
    train_frame = make_feature_frame(train_records, history)
    val_frame = make_feature_frame(validation_records, history)
    y_train = make_target_array(train_records)
    model = build_model()
    model.fit(train_frame, y_train)
    return model.predict(val_frame)
