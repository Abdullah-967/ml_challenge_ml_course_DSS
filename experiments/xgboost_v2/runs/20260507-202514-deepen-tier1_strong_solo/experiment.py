"""xgboost_v2 deepen iter10 -- single knob: + commune target encoding (smooth=20).

Carry-forward: deepen_iter9 (ratios kept tie, 49264.60).
This iter adds commune_first target encoding (smoothed mean) on top of
keeping commune_first as native cat. Encoder fit on train fold only.
"""

from __future__ import annotations

import numpy as np
import pandas as pd
from xgboost import XGBRegressor

TARGET_KEY = "property_value"
MODEL_FAMILY = "xgboost_v2"
FEATURE_LANE = "tier1_strong_solo"
RECIPE_VARIANT = "deepen_iter10_add_commune_te20"
PARAMS_SUMMARY = (
    "XGBRegressor(reg:absoluteerror,n_est=500,lr=0.05,max_depth=6,"
    "min_child_weight=5,subsample=0.8,colsample_bytree=0.8,reg_lambda=1.0,"
    "tree_method=hist,enable_categorical=True),log1p+ratios+commune_te20"
)
TE_SMOOTHING = 20
DATE_EPOCH = pd.Timestamp("2014-01-01")
USE_LOG_TARGET = True
DERIVED_RATIO_COLUMNS = (
    "built_per_premise",
    "land_per_lot",
    "commercial_share",
    "apt_share",
    "houses_per_premise",
)

NUMERIC_COLUMNS = (
    "built_area",
    "house_area",
    "area_house_5plus_rooms",
    "land_area",
    "num_lots",
    "num_premises",
    "num_houses",
    "num_apartments",
    "num_commercial",
    "apartment_area",
    "num_house_5plus_rooms",
    "area_house_4_rooms",
    "num_house_4_rooms",
    "area_house_3_rooms",
    "num_house_3_rooms",
    "area_house_2_rooms",
    "num_house_2_rooms",
    "area_house_1_room",
    "num_house_1_room",
    "area_apt_5plus_rooms",
    "num_apt_5plus_rooms",
    "area_apt_4_rooms",
    "num_apt_4_rooms",
    "area_apt_3_rooms",
    "num_apt_3_rooms",
    "area_apt_2_rooms",
    "num_apt_2_rooms",
    "area_apt_1_room",
    "num_apt_1_room",
    "date_ordinal",
    "built_per_premise",
    "land_per_lot",
    "commercial_share",
    "apt_share",
    "houses_per_premise",
    "commune_first_target_enc",
)
CATEGORICAL_COLUMNS = ("property_type", "commune_first", "cadastral_first", "transaction_type")


def first_token(value):
    if value is None or (isinstance(value, float) and np.isnan(value)):
        return np.nan
    text = str(value).strip()
    if not text:
        return np.nan
    return text.split(",")[0].strip()


def add_geo_first_tokens(frame):
    frame = frame.copy()
    if "commune_codes" in frame.columns:
        frame["commune_first"] = frame["commune_codes"].map(first_token)
    if "cadastral_sections" in frame.columns:
        frame["cadastral_first"] = frame["cadastral_sections"].map(first_token)
    return frame


def add_date_ordinal(frame):
    frame = frame.copy()
    if "transaction_date" in frame.columns:
        first_date = frame["transaction_date"].astype(str).str.split(",").str[0].str.strip()
        parsed = pd.to_datetime(first_date, errors="coerce")
        frame["date_ordinal"] = (parsed - DATE_EPOCH).dt.days.astype("Float64")
    else:
        frame["date_ordinal"] = np.nan
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


def fit_target_encoder(train_records, column, smoothing):
    frame = add_geo_first_tokens(pd.DataFrame(train_records))
    target = pd.to_numeric(frame[TARGET_KEY], errors="coerce")
    cat = frame[column].astype("object")
    df = pd.DataFrame({"cat": cat, "y": target}).dropna()
    global_mean = df["y"].mean()
    grouped = df.groupby("cat")["y"]
    counts = grouped.count()
    means = grouped.mean()
    smoothed = (counts * means + smoothing * global_mean) / (counts + smoothing)
    return smoothed.to_dict(), global_mean


def apply_target_encoder(frame, column, encoder, fallback):
    return frame[column].astype("object").map(encoder).fillna(fallback)


def make_feature_frame(records, category_levels, target_encoders=None):
    frame = add_derived_ratios(add_date_ordinal(add_geo_first_tokens(pd.DataFrame(records))))
    if target_encoders is not None:
        for column, (encoder, fallback) in target_encoders.items():
            frame[f"{column}_target_enc"] = apply_target_encoder(frame, column, encoder, fallback)
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
    target_encoders = {
        "commune_first": fit_target_encoder(train_records, "commune_first", TE_SMOOTHING),
    }
    train_frame = make_feature_frame(train_records, category_levels, target_encoders)
    validation_frame = make_feature_frame(validation_records, category_levels, target_encoders)
    y_train = make_target_array(train_records)
    model = build_model()
    if USE_LOG_TARGET:
        model.fit(train_frame, np.log1p(y_train))
        return np.expm1(model.predict(validation_frame))
    model.fit(train_frame, y_train)
    return model.predict(validation_frame)
