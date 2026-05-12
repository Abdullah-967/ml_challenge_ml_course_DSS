"""sklearn GradientBoostingRegressor smoke anchor (lane: all_numeric).

Single-knob discipline: each iteration changes exactly one knob from this
anchor -- one feature, one hyperparameter, one preprocessing step, or one
target transform. Update RECIPE_VARIANT and PARAMS_SUMMARY in run-local copies
to name the knob. See plugins/model-family-mae/references/reflection_protocol.md.
"""

from __future__ import annotations

import numpy as np
import pandas as pd
from sklearn.ensemble import GradientBoostingRegressor
from sklearn.impute import SimpleImputer
from sklearn.pipeline import Pipeline

TARGET_KEY = "property_value"
MODEL_FAMILY = "gradient_boosting_sklearn"
FEATURE_LANE = "all_numeric"
RECIPE_VARIANT = "smoke_all_numeric"
PARAMS_SUMMARY = (
    "GBR(loss=absolute_error,n_est=100,lr=0.1,max_depth=3,subsample=0.8),"
    "all_numeric,impute=median"
)

# region_code is constant in the training set (single region Nouvelle-Aquitaine,
# single dept Vienne); drop after dataset inspection so the model does not waste
# splits on a constant column.
DROP_FROM_NUMERIC = {"region_code"}


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


def make_feature_frame(records, feature_columns):
    frame = pd.DataFrame(records).reindex(columns=feature_columns)
    return frame.apply(pd.to_numeric, errors="coerce")


def make_target_array(records):
    return np.array([record[TARGET_KEY] for record in records], dtype=np.float64)


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
    feature_columns = infer_numeric_features(train_records)
    model = build_model()
    model.fit(
        make_feature_frame(train_records, feature_columns),
        make_target_array(train_records),
    )
    return model.predict(make_feature_frame(validation_records, feature_columns))
