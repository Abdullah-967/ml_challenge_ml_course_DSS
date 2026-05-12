"""xgboost_v2 smoke iter3 -- tier3_weak_solo lane.

Data-driven scout: all remaining cols with weak/negative solo signal
(improvement <=0 vs median). Tests whether the long-tail composes into
something meaningful, including the geo cols (commune_codes,
cadastral_sections) that were dominant for the original xgboost family
despite poor solo scores.

Disjoint from tier1/tier2. Excludes constants (dept/region cols,
n_unique=1) and IDs (parcel_ids, transferred_parcel_ids). Excludes
transaction_date (2181 unique strings, no useful raw treatment).

Multi-value strings commune_codes/cadastral_sections passed via first_token
as native xgboost categoricals (same primitive treatment used in EDA).
"""

from __future__ import annotations

import numpy as np
import pandas as pd
from xgboost import XGBRegressor

TARGET_KEY = "property_value"
MODEL_FAMILY = "xgboost_v2"
FEATURE_LANE = "tier3_weak_solo"
RECIPE_VARIANT = "smoke_tier3_weak_solo"
PARAMS_SUMMARY = (
    "XGBRegressor(reg:absoluteerror,n_est=500,lr=0.05,max_depth=6,"
    "min_child_weight=5,subsample=0.8,colsample_bytree=0.8,reg_lambda=1.0,"
    "tree_method=hist,enable_categorical=True),tier3_weak_solo"
)

NUMERIC_COLUMNS = (
    "num_apartments",
    "area_apt_1_room",
    "num_apt_1_room",
    "num_lots",
    "num_dependencies",
    "area_house_4_rooms",
    "area_apt_2_rooms",
    "num_apt_2_rooms",
    "num_house_4_rooms",
    "area_apt_5plus_rooms",
    "area_apt_4_rooms",
    "area_apt_3_rooms",
    "num_apt_5plus_rooms",
    "num_apt_3_rooms",
    "year",
    "num_house_2_rooms",
    "num_house_1_room",
    "area_house_2_rooms",
    "num_apt_4_rooms",
    "area_house_1_room",
    "future_sale",
    "num_sections",
    "area_house_3_rooms",
    "num_communes",
    "num_house_3_rooms",
    "month",
    "num_parcels",
    "land_area",
    "num_commercial",
)
CATEGORICAL_COLUMNS = ("transaction_type", "commune_first", "cadastral_first")


def first_token(value):
    if value is None or (isinstance(value, float) and np.isnan(value)):
        return np.nan
    text = str(value).strip()
    if not text:
        return np.nan
    return text.split(",")[0].strip()


def add_geo_first_tokens(frame):
    frame = frame.copy()
    frame["commune_first"] = frame.get("commune_codes").map(first_token) if "commune_codes" in frame.columns else np.nan
    frame["cadastral_first"] = (
        frame.get("cadastral_sections").map(first_token) if "cadastral_sections" in frame.columns else np.nan
    )
    return frame


def make_feature_frame(records, category_levels):
    frame = add_geo_first_tokens(pd.DataFrame(records))
    numeric_part = (
        frame.reindex(columns=list(NUMERIC_COLUMNS))
        .apply(pd.to_numeric, errors="coerce")
        .replace([np.inf, -np.inf], np.nan)
    )
    cat_part = pd.DataFrame(index=frame.index)
    for column in CATEGORICAL_COLUMNS:
        levels = category_levels[column]
        series = frame[column] if column in frame.columns else pd.Series([np.nan] * len(frame), index=frame.index)
        cat_part[column] = pd.Categorical(series, categories=levels)
    return pd.concat([numeric_part, cat_part], axis=1)


def fit_category_levels(records):
    frame = add_geo_first_tokens(pd.DataFrame(records))
    levels = {}
    for column in CATEGORICAL_COLUMNS:
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
        max_depth=6,
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
    category_levels = fit_category_levels(train_records)
    train_frame = make_feature_frame(train_records, category_levels)
    validation_frame = make_feature_frame(validation_records, category_levels)
    y_train = make_target_array(train_records)
    model = build_model()
    model.fit(train_frame, y_train)
    return model.predict(validation_frame)
