"""sklearn GradientBoostingRegressor smoke lane C (geo_signal).

One-knob change vs lane A anchor: feature scope only -- add a single fold-safe
smoothed mean-target encoding of commune_codes on top of the all_numeric
anchor. Encoding is computed inside fit_predict using train_records only, so
it stays fold-safe per leakage_and_validation.md.

Smoothing rule: smoothed_mean = (n * group_mean + k * global_mean) / (n + k)
with k=20, and a global-mean fallback for communes unseen in the fold's
training split. Model hyperparameters identical to the anchor.
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
RECIPE_VARIANT = "deepen_iter13_n_est_200"
PARAMS_SUMMARY = (
    "GBR(loss=absolute_error,n_est=200,lr=0.1,max_depth=4,subsample=0.8),"
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
                    n_estimators=200,
                    learning_rate=0.1,
                    max_depth=4,
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
