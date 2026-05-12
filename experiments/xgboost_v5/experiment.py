"""Starter recipe for a model-family MAE experiment.

Each family-specific `experiments/<model_family>/experiment.py` should expose
`fit_predict(train_records, validation_records)`.

Single-knob discipline: each iteration of this file should change exactly one
knob from the previous iteration -- one feature, one hyperparameter, one
preprocessing step, or one target transform. Update `RECIPE_VARIANT` below to
name the knob being tested in this iteration so the row in `results.tsv` and
the entry in `iteration_log.md` agree on what changed. See
`plugins/model-family-mae/references/reflection_protocol.md`.
"""

from __future__ import annotations

import numpy as np
import pandas as pd
from sklearn.impute import SimpleImputer
from sklearn.linear_model import Ridge
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler

TARGET_KEY = "property_value"
MODEL_FAMILY = "linear_robust"
FEATURE_LANE = "all_numeric"
RECIPE_VARIANT = "iter1_baseline"  # one short tag for the single knob changed this iter
PARAMS_SUMMARY = "Ridge(alpha=10.0),all_numeric,variant=iter1_baseline"


def infer_numeric_features(records):
    frame = pd.DataFrame(records)
    features = []

    for column in frame.columns:
        if column == TARGET_KEY:
            continue

        values = pd.to_numeric(frame[column], errors="coerce")
        if values.notna().any():
            features.append(column)

    return features


def make_feature_frame(records, feature_columns):
    frame = pd.DataFrame(records).reindex(columns=feature_columns)
    return frame.apply(pd.to_numeric, errors="coerce")


def make_target_array(records):
    return np.array([record[TARGET_KEY] for record in records], dtype=np.float64)


def build_model():
    return Pipeline(
        [
            ("imputer", SimpleImputer(strategy="median")),
            ("scaler", StandardScaler()),
            ("model", Ridge(alpha=10.0)),
        ]
    )


def fit_predict(train_records, validation_records):
    feature_columns = infer_numeric_features(train_records)
    model = build_model()
    model.fit(
        make_feature_frame(train_records, feature_columns),
        make_target_array(train_records),
    )
    return model.predict(make_feature_frame(validation_records, feature_columns))
