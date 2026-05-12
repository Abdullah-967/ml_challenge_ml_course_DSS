"""RandomForest deepen iter1 recipe.

Stage 2 deepen iter1. Single-knob: add 5 structural ratios on top of smoke
iter2 best (all_numeric + OHE cats). Cumulative recipe: numeric + ratios +
OHE(property_type, transaction_type).
"""

from __future__ import annotations

import numpy as np
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.ensemble import RandomForestRegressor
from sklearn.impute import SimpleImputer
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder

TARGET_KEY = "property_value"
MODEL_FAMILY = "tree_bagging_rf"
FEATURE_LANE = "numeric_plus_basic_cats"
RECIPE_VARIANT = "deepen_iter1_add_ratios"
PARAMS_SUMMARY = (
    "RandomForestRegressor(n_est=200,max_depth=18,min_samples_leaf=2,"
    "max_features=sqrt,n_jobs=-1,random_state=42),"
    "all_numeric+ratios+OHE(property_type,transaction_type)"
)

ID_COLUMNS = {"parcel_ids", "transferred_parcel_ids"}
CATEGORICAL_COLUMNS = ("property_type", "transaction_type")
DERIVED_RATIO_COLUMNS = (
    "built_per_premise",
    "land_per_lot",
    "commercial_share",
    "apt_share",
    "houses_per_premise",
)
MISSING_TOKEN = "__missing__"


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
        if column in CATEGORICAL_COLUMNS:
            continue
        values = pd.to_numeric(frame[column], errors="coerce")
        if values.notna().any():
            features.append(column)
    features.extend(DERIVED_RATIO_COLUMNS)
    return features


def make_feature_frame(records, numeric_columns, categorical_columns):
    frame = add_derived_ratios(pd.DataFrame(records))
    numeric = (
        frame.reindex(columns=numeric_columns)
        .apply(pd.to_numeric, errors="coerce")
        .replace([np.inf, -np.inf], np.nan)
    )
    cat = frame.reindex(columns=list(categorical_columns)).astype(object)
    for col in cat.columns:
        cat[col] = cat[col].where(cat[col].notna(), MISSING_TOKEN).astype(str)
    return pd.concat([numeric, cat], axis=1)


def make_target_array(records):
    return np.array([record[TARGET_KEY] for record in records], dtype=np.float64)


def build_model(numeric_columns, categorical_columns):
    preprocessor = ColumnTransformer(
        transformers=[
            ("num", SimpleImputer(strategy="median"), list(numeric_columns)),
            (
                "cat",
                OneHotEncoder(handle_unknown="ignore", sparse_output=False),
                list(categorical_columns),
            ),
        ]
    )
    return Pipeline(
        [
            ("preprocessor", preprocessor),
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
    numeric_columns = infer_numeric_features(train_records)
    train_frame = make_feature_frame(train_records, numeric_columns, CATEGORICAL_COLUMNS)
    validation_frame = make_feature_frame(validation_records, numeric_columns, CATEGORICAL_COLUMNS)
    model = build_model(numeric_columns, CATEGORICAL_COLUMNS)
    model.fit(train_frame, make_target_array(train_records))
    return model.predict(validation_frame)
