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

# Drop columns that should not enter the numeric lane:
# - region_code: constant (single region/dept).
# - parcel_ids / transferred_parcel_ids: comma-joined ID tokens that pandas
#   coerces to floats up to ~1e259, overflowing sklearn's float32 cast.
# - commune_codes / cadastral_sections: high-cardinality categorical strings
#   that may collapse to a single numeric only when one element is present;
#   handled as categoricals in the geo_signal lane, not all_numeric.
DROP_FROM_NUMERIC = {
    "region_code",
    "parcel_ids",
    "transferred_parcel_ids",
    "commune_codes",
    "cadastral_sections",
}


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
