"""XGBoost deepen recipe for the model-family MAE workflow.

Stage 2 deepen iter2. Single knob this iter: derived ratios added on top of
smoke geo_signal best (log1p reverted: deepen iter1 showed it doesn't help
xgboost with reg:absoluteerror).

Recipe carried forward from smoke geo_signal: all_numeric + commune_first +
cadastral_first as native cats, XGBoost reg:absoluteerror smoke defaults.
Added: built_per_premise, land_per_lot, commercial_share, apt_share,
houses_per_premise.
"""

from __future__ import annotations

import numpy as np
import pandas as pd
from xgboost import XGBRegressor

TARGET_KEY = "property_value"
MODEL_FAMILY = "xgboost"
FEATURE_LANE = "geo_signal"
RECIPE_VARIANT = "deepen4_log_skewed"
PARAMS_SUMMARY = (
    "XGBRegressor(reg:absoluteerror,n_est=500,lr=0.05,max_depth=4,"
    "min_child_weight=5,subsample=0.8,colsample_bytree=0.8,reg_lambda=1.0,"
    "tree_method=hist,enable_categorical=True),"
    "geo_signal+ratios+log(built,land,apt,house)"
)
USE_LOG_TARGET = False
DERIVED_RATIO_COLUMNS = (
    "built_per_premise",
    "land_per_lot",
    "commercial_share",
    "apt_share",
    "houses_per_premise",
)
LOG_SKEWED_COLUMNS = (
    "log_built_area",
    "log_land_area",
    "log_apartment_area",
    "log_house_area",
)

ID_COLUMNS = {"parcel_ids", "transferred_parcel_ids"}
GEO_MULTIVALUE_COLUMNS = ("commune_codes", "cadastral_sections")
CATEGORICAL_COLUMNS = ("commune_first", "cadastral_first")


def first_token(value):
    if value is None or (isinstance(value, float) and np.isnan(value)):
        return np.nan
    text = str(value).strip()
    if not text:
        return np.nan
    return text.split(",")[0].strip()


def add_geo_features(frame):
    frame = frame.copy()
    frame["commune_first"] = frame.get("commune_codes").map(first_token) if "commune_codes" in frame.columns else np.nan
    frame["cadastral_first"] = (
        frame.get("cadastral_sections").map(first_token) if "cadastral_sections" in frame.columns else np.nan
    )
    return frame


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


def add_log_skewed(frame):
    frame = frame.copy()
    for src, dst in (
        ("built_area", "log_built_area"),
        ("land_area", "log_land_area"),
        ("apartment_area", "log_apartment_area"),
        ("house_area", "log_house_area"),
    ):
        values = pd.to_numeric(frame.get(src), errors="coerce")
        frame[dst] = np.log1p(values.where(values >= 0))
    return frame


def infer_numeric_features(records):
    frame = pd.DataFrame(records)
    features = []
    for column in frame.columns:
        if column == TARGET_KEY or column in ID_COLUMNS:
            continue
        if column in CATEGORICAL_COLUMNS or column in GEO_MULTIVALUE_COLUMNS:
            continue
        values = pd.to_numeric(frame[column], errors="coerce")
        if values.notna().any():
            features.append(column)
    features.extend(DERIVED_RATIO_COLUMNS)
    features.extend(LOG_SKEWED_COLUMNS)
    return features


def make_feature_frame(records, numeric_columns, categorical_columns, category_levels):
    frame = add_log_skewed(add_derived_ratios(add_geo_features(pd.DataFrame(records))))
    numeric_part = (
        frame.reindex(columns=numeric_columns)
        .apply(pd.to_numeric, errors="coerce")
        .replace([np.inf, -np.inf], np.nan)
    )
    cat_part = pd.DataFrame(index=frame.index)
    for column in categorical_columns:
        levels = category_levels[column]
        series = frame[column] if column in frame.columns else pd.Series([np.nan] * len(frame), index=frame.index)
        cat_part[column] = pd.Categorical(series, categories=levels)
    return pd.concat([numeric_part, cat_part], axis=1)


def fit_category_levels(records, categorical_columns):
    frame = add_geo_features(pd.DataFrame(records))
    levels = {}
    for column in categorical_columns:
        if column in frame.columns:
            levels[column] = list(pd.Series(frame[column]).dropna().unique())
        else:
            levels[column] = []
    return levels


def make_target_array(records):
    return np.array([record[TARGET_KEY] for record in records], dtype=np.float64)


def build_model():
    return XGBRegressor(
        objective="reg:absoluteerror",
        n_estimators=500,
        learning_rate=0.05,
        max_depth=4,
        min_child_weight=5,
        subsample=0.8,
        colsample_bytree=0.8,
        reg_lambda=1.0,
        tree_method="hist",
        n_jobs=-1,
        random_state=42,
        enable_categorical=True,
    )


def fit_predict(train_records, validation_records):
    numeric_columns = infer_numeric_features(train_records)
    category_levels = fit_category_levels(train_records, CATEGORICAL_COLUMNS)
    train_frame = make_feature_frame(train_records, numeric_columns, CATEGORICAL_COLUMNS, category_levels)
    validation_frame = make_feature_frame(validation_records, numeric_columns, CATEGORICAL_COLUMNS, category_levels)
    model = build_model()
    y_train = make_target_array(train_records)
    if USE_LOG_TARGET:
        model.fit(train_frame, np.log1p(y_train))
        return np.expm1(model.predict(validation_frame))
    model.fit(train_frame, y_train)
    return model.predict(validation_frame)
