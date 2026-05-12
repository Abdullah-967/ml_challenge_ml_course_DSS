"""Deepen iter2: capacity pair (n_estimators=300, learning_rate=0.05).

One mechanically-paired knob change vs anchor 20260509-200605-smoke-geo_signal:
n_estimators 100 -> 300 paired with learning_rate 0.1 -> 0.05 to triple the
step budget while halving step size, keeping the cumulative learning capacity
roughly comparable but with more shrinkage. Per search_policy.md, paired
capacity knobs count as one knob; the pairing is documented here.

Raw target restored after iter1 log1p tie. Same lane / feature scope as anchor.
"""

from __future__ import annotations

import numpy as np
import pandas as pd
from sklearn.ensemble import GradientBoostingRegressor
from sklearn.impute import SimpleImputer
from sklearn.pipeline import Pipeline

TARGET_KEY = "property_value"
MODEL_FAMILY = "gradient_boosting_sklearn"
FEATURE_LANE = "geo_signal"
RECIPE_VARIANT = "deepen_iter2_capacity_pair"
PARAMS_SUMMARY = (
    "GBR(loss=absolute_error,n_est=300,lr=0.05,max_depth=3,subsample=0.8),"
    "geo_signal,commune_te(k=20)"
)

DROP_FROM_NUMERIC = {
    "region_code",
    "parcel_ids",
    "transferred_parcel_ids",
    "commune_codes",
    "cadastral_sections",
}

COMMUNE_KEY = "commune_codes"
COMMUNE_TE_FEATURE = "commune_target_mean_smoothed"
SMOOTHING_K = 20.0


def infer_numeric_features(records):
    frame = pd.DataFrame(records)
    features = []
    for column in frame.columns:
        if column == TARGET_KEY or column in DROP_FROM_NUMERIC:
            continue
        values = pd.to_numeric(frame[column], errors="coerce")
        if values.notna().any():
            features.append(column)
    return features


def make_target_array(records):
    return np.array([record[TARGET_KEY] for record in records], dtype=np.float64)


def commune_series(records):
    return pd.Series([record.get(COMMUNE_KEY) for record in records])


def fit_commune_target_encoding(train_records):
    targets = make_target_array(train_records)
    communes = commune_series(train_records)
    frame = pd.DataFrame({"commune": communes, "target": targets})
    global_mean = float(frame["target"].mean())

    grouped = frame.groupby("commune")["target"]
    counts = grouped.count().astype(float)
    means = grouped.mean()
    smoothed = (counts * means + SMOOTHING_K * global_mean) / (counts + SMOOTHING_K)
    return smoothed.to_dict(), global_mean


def apply_commune_target_encoding(records, mapping, global_mean):
    return commune_series(records).map(mapping).fillna(global_mean).to_numpy(dtype=np.float64)


def make_feature_frame(records, numeric_columns, commune_te_values):
    frame = pd.DataFrame(records).reindex(columns=numeric_columns)
    frame = frame.apply(pd.to_numeric, errors="coerce")
    frame[COMMUNE_TE_FEATURE] = commune_te_values
    return frame


def build_model():
    return Pipeline(
        [
            ("imputer", SimpleImputer(strategy="median")),
            (
                "model",
                GradientBoostingRegressor(
                    loss="absolute_error",
                    n_estimators=300,
                    learning_rate=0.05,
                    max_depth=3,
                    subsample=0.8,
                    random_state=42,
                ),
            ),
        ]
    )


def fit_predict(train_records, validation_records):
    numeric_columns = infer_numeric_features(train_records)
    mapping, global_mean = fit_commune_target_encoding(train_records)
    train_te = apply_commune_target_encoding(train_records, mapping, global_mean)
    valid_te = apply_commune_target_encoding(validation_records, mapping, global_mean)

    model = build_model()
    model.fit(
        make_feature_frame(train_records, numeric_columns, train_te),
        make_target_array(train_records),
    )
    return model.predict(make_feature_frame(validation_records, numeric_columns, valid_te))
