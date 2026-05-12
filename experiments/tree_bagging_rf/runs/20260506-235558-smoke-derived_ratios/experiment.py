"""RandomForest smoke iter3 recipe.

Stage 1 smoke iter3. Single-knob lane swap: derived_ratios = all_numeric +
5 structural ratios (drops OHE cats from iter2). Tests whether interpretable
ratio features add lift on RF beyond raw counts/areas.
"""

from __future__ import annotations

import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestRegressor
from sklearn.impute import SimpleImputer
from sklearn.pipeline import Pipeline

TARGET_KEY = "property_value"
MODEL_FAMILY = "tree_bagging_rf"
FEATURE_LANE = "derived_ratios"
RECIPE_VARIANT = "smoke_iter3_derived_ratios"
PARAMS_SUMMARY = (
    "RandomForestRegressor(n_est=200,max_depth=18,min_samples_leaf=2,"
    "max_features=sqrt,n_jobs=-1,random_state=42),"
    "all_numeric+ratios{built_per_premise,land_per_lot,commercial_share,apt_share,houses_per_premise}"
)

ID_COLUMNS = {"parcel_ids", "transferred_parcel_ids"}
DERIVED_RATIO_COLUMNS = (
    "built_per_premise",
    "land_per_lot",
    "commercial_share",
    "apt_share",
    "houses_per_premise",
)


def safe_div(numerator, denominator):
    num = pd.to_numeric(numerator, errors="coerce")
    den = pd.to_numeric(denominator, errors="coerce")
    den = den.where(den > 0, np.nan)
    return num / den


def add_derived_ratios(frame):
    frame = frame.copy()
    frame["built_per_premise"] = safe_div(frame.get("built_area"), frame.get("num_premises"))
    frame["land_per_lot"] = safe_div(frame.get("land_area"), frame.get("num_lots"))
    frame["commercial_share"] = safe_div(frame.get("num_commercial"), frame.get("num_premises"))
    frame["apt_share"] = safe_div(frame.get("num_apartments"), frame.get("num_premises"))
    frame["houses_per_premise"] = safe_div(frame.get("num_houses"), frame.get("num_premises"))
    return frame


def infer_numeric_features(records):
    frame = pd.DataFrame(records)
    features = []
    for column in frame.columns:
        if column == TARGET_KEY or column in ID_COLUMNS:
            continue
        values = pd.to_numeric(frame[column], errors="coerce")
        if values.notna().any():
            features.append(column)
    features.extend(DERIVED_RATIO_COLUMNS)
    return features


def make_feature_frame(records, feature_columns):
    frame = add_derived_ratios(pd.DataFrame(records))
    return (
        frame.reindex(columns=feature_columns)
        .apply(pd.to_numeric, errors="coerce")
        .replace([np.inf, -np.inf], np.nan)
    )


def make_target_array(records):
    return np.array([record[TARGET_KEY] for record in records], dtype=np.float64)


def build_model():
    return Pipeline(
        [
            ("imputer", SimpleImputer(strategy="median")),
            (
                "model",
                RandomForestRegressor(
                    n_estimators=200,
                    max_depth=18,
                    min_samples_leaf=2,
                    max_features="sqrt",
                    n_jobs=-1,
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
