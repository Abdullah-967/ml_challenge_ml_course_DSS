"""Deepen iter1: log1p target on smoke geo_signal anchor.

One-knob change vs anchor 20260509-200605-smoke-geo_signal: target transform
only. Train on log1p(property_value), predict, invert with expm1 before
returning. The commune target-mean encoding is left in raw EUR scale (same as
the anchor) so this iteration isolates the target-transform effect from the
encoding-scale choice.

property_value distribution justification: heavy right-skew (max ~38M, median
~145k); log1p compresses the long tail and may stabilize splits in early
stages even though loss=absolute_error already handles outliers.
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
RECIPE_VARIANT = "deepen_iter1_log1p_target"
PARAMS_SUMMARY = (
    "GBR(loss=absolute_error,n_est=100,lr=0.1,max_depth=3,subsample=0.8),"
    "geo_signal,commune_te(k=20),target=log1p"
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
                    n_estimators=100,
                    learning_rate=0.1,
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

    targets_log = np.log1p(make_target_array(train_records))
    model = build_model()
    model.fit(
        make_feature_frame(train_records, numeric_columns, train_te),
        targets_log,
    )
    predictions_log = model.predict(make_feature_frame(validation_records, numeric_columns, valid_te))
    predictions = np.expm1(predictions_log)
    return np.clip(predictions, 0.0, None)
