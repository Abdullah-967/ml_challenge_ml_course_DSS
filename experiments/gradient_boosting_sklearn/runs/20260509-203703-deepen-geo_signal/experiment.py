"""Deepen iter5: cadastral target encoding on iter3 (max_depth=4) anchor.

One-knob change vs iter3 (max_depth=4 family best): add a second fold-safe
smoothed mean-target encoding column for cadastral_sections, alongside the
existing commune target encoding. Same smoothing rule (k=20) for symmetry.
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
RECIPE_VARIANT = "deepen_iter5_cadastral_te"
PARAMS_SUMMARY = (
    "GBR(loss=absolute_error,n_est=100,lr=0.1,max_depth=4,subsample=0.8),"
    "geo_signal,commune_te(k=20)+cadastral_te(k=20)"
)

DROP_FROM_NUMERIC = {
    "region_code",
    "parcel_ids",
    "transferred_parcel_ids",
    "commune_codes",
    "cadastral_sections",
}

COMMUNE_KEY = "commune_codes"
SECTION_KEY = "cadastral_sections"
COMMUNE_TE_FEATURE = "commune_target_mean_smoothed"
SECTION_TE_FEATURE = "section_target_mean_smoothed"
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


def category_series(records, key):
    return pd.Series([record.get(key) for record in records])


def fit_smoothed_target_encoding(values, targets):
    frame = pd.DataFrame({"key": values, "target": targets})
    global_mean = float(frame["target"].mean())
    grouped = frame.groupby("key")["target"]
    counts = grouped.count().astype(float)
    means = grouped.mean()
    smoothed = (counts * means + SMOOTHING_K * global_mean) / (counts + SMOOTHING_K)
    return smoothed.to_dict(), global_mean


def apply_target_encoding(values, mapping, global_mean):
    return values.map(mapping).fillna(global_mean).to_numpy(dtype=np.float64)


def make_feature_frame(records, numeric_columns, commune_te_values, section_te_values):
    frame = pd.DataFrame(records).reindex(columns=numeric_columns)
    frame = frame.apply(pd.to_numeric, errors="coerce")
    frame[COMMUNE_TE_FEATURE] = commune_te_values
    frame[SECTION_TE_FEATURE] = section_te_values
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
    targets = make_target_array(train_records)

    train_communes = category_series(train_records, COMMUNE_KEY)
    valid_communes = category_series(validation_records, COMMUNE_KEY)
    commune_map, commune_global = fit_smoothed_target_encoding(train_communes, targets)
    train_commune_te = apply_target_encoding(train_communes, commune_map, commune_global)
    valid_commune_te = apply_target_encoding(valid_communes, commune_map, commune_global)

    train_sections = category_series(train_records, SECTION_KEY)
    valid_sections = category_series(validation_records, SECTION_KEY)
    section_map, section_global = fit_smoothed_target_encoding(train_sections, targets)
    train_section_te = apply_target_encoding(train_sections, section_map, section_global)
    valid_section_te = apply_target_encoding(valid_sections, section_map, section_global)

    model = build_model()
    model.fit(
        make_feature_frame(train_records, numeric_columns, train_commune_te, train_section_te),
        targets,
    )
    return model.predict(
        make_feature_frame(validation_records, numeric_columns, valid_commune_te, valid_section_te)
    )
