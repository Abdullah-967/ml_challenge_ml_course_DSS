"""Deepen iter6: area_density_ratios on iter3 anchor.

One-knob change vs iter3: feature scope. Add a single hypothesis_unit
(area_density_ratios) consisting of three size-normalized ratios:
- built_area / num_premises (built area per declared premise)
- land_area / num_lots (land per lot)
- num_commercial / num_premises (commercial share per premise)

Denominators are protected with a small epsilon to avoid division-by-zero;
when the denominator is zero, the ratio is set to 0.0 deterministically.
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
RECIPE_VARIANT = "deepen_iter6_area_density_ratios"
PARAMS_SUMMARY = (
    "GBR(loss=absolute_error,n_est=100,lr=0.1,max_depth=4,subsample=0.8),"
    "geo_signal,commune_te(k=20),area_density_ratios"
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

RATIO_FEATURES = (
    "built_per_premise",
    "land_per_lot",
    "commercial_share",
)


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


def safe_ratio(numerator, denominator):
    n = pd.to_numeric(numerator, errors="coerce").fillna(0.0)
    d = pd.to_numeric(denominator, errors="coerce").fillna(0.0)
    out = np.where(d > 0, n / np.where(d > 0, d, 1.0), 0.0)
    return out.astype(np.float64)


def make_feature_frame(records, numeric_columns, commune_te_values):
    raw = pd.DataFrame(records)
    frame = raw.reindex(columns=numeric_columns).apply(pd.to_numeric, errors="coerce")
    frame[COMMUNE_TE_FEATURE] = commune_te_values
    frame["built_per_premise"] = safe_ratio(raw.get("built_area"), raw.get("num_premises"))
    frame["land_per_lot"] = safe_ratio(raw.get("land_area"), raw.get("num_lots"))
    frame["commercial_share"] = safe_ratio(raw.get("num_commercial"), raw.get("num_premises"))
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
