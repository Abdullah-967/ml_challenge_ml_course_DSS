"""xgboost_v5 deepen iter8 -- single knob: HGB blend (cross-family diversity).

Anchor: v4 W''''' (smoke 1-3, deepen 4-7 reverted/tied).
Adds an HGB(absolute_error) head; blend final = 0.5 * v4_anchor + 0.5 * hgb.
HGB uses anchor's full feature set (categoricals as ordinals via pandas
categorical codes; HGB does not natively support enable_categorical=True
the same way xgboost does, so we encode categories as integer codes).
"""

from __future__ import annotations

import numpy as np
import pandas as pd
from sklearn.ensemble import HistGradientBoostingRegressor
from xgboost import XGBRegressor

TARGET_KEY = "property_value"
MODEL_FAMILY = "xgboost_v5"
FEATURE_LANE = "v4_anchor"
RECIPE_VARIANT = "deepen_iter8_hgb_blend50"
PARAMS_SUMMARY = (
    "0.5*XGBRegressor(reg:absoluteerror,n_est=4000,lr=0.05,max_depth=6,...)"
    "+0.5*HGB(absolute_error,max_iter=1000,lr=0.05,max_leaf_nodes=63)"
)
DATE_EPOCH = pd.Timestamp("2014-01-01")
USE_LOG_TARGET = True
HGB_BLEND = 0.5

NUMERIC_COLUMNS = (
    "built_area", "house_area", "area_house_5plus_rooms", "land_area",
    "num_lots", "num_premises", "num_houses", "num_apartments", "num_commercial",
    "apartment_area", "num_house_5plus_rooms",
    "area_house_4_rooms", "num_house_4_rooms",
    "area_house_3_rooms", "num_house_3_rooms",
    "area_house_2_rooms", "num_house_2_rooms",
    "area_house_1_room", "num_house_1_room",
    "area_apt_5plus_rooms", "num_apt_5plus_rooms",
    "area_apt_4_rooms", "num_apt_4_rooms",
    "area_apt_3_rooms", "num_apt_3_rooms",
    "area_apt_2_rooms", "num_apt_2_rooms",
    "area_apt_1_room", "num_apt_1_room",
    "date_ordinal",
    "built_per_premise", "land_per_lot", "commercial_share", "apt_share", "houses_per_premise",
    "built_per_land",
    "built_rel_type",
)
CATEGORICAL_COLUMNS = (
    "property_type", "commune_first", "cadastral_first", "transaction_type",
    "dept_code", "region_code",
)


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
    frame["built_per_land"] = safe_div(frame.get("built_area"), frame.get("land_area"))
    return frame


def compute_built_rel_type_map(train_frame):
    df = pd.DataFrame({
        "type": train_frame["property_type"].astype(str),
        "built": pd.to_numeric(train_frame.get("built_area"), errors="coerce"),
    })
    df = df[(df["type"] != "nan") & df["built"].notna() & (df["built"] > 0)]
    means = df.groupby("type")["built"].mean()
    global_mean = df["built"].mean()
    return means.to_dict(), global_mean


def add_built_rel_type(frame, type_means, global_mean):
    frame = frame.copy()
    type_str = frame["property_type"].astype(str)
    type_mean_per_row = type_str.map(type_means).fillna(global_mean).astype(float)
    built = pd.to_numeric(frame.get("built_area"), errors="coerce")
    frame["built_rel_type"] = built / type_mean_per_row.replace(0, np.nan)
    return frame


def make_feature_frame_pre(records):
    return add_derived_ratios(add_date_ordinal(add_geo_first_tokens(pd.DataFrame(records))))


def materialize_features(frame, category_levels):
    numeric_part = (
        frame.reindex(columns=list(NUMERIC_COLUMNS))
        .apply(pd.to_numeric, errors="coerce")
        .replace([np.inf, -np.inf], np.nan)
    )
    cat_part = pd.DataFrame(index=frame.index)
    for column in CATEGORICAL_COLUMNS:
        levels = category_levels[column]
        series = frame[column].astype(str) if column in frame.columns else pd.Series([np.nan] * len(frame), index=frame.index)
        cat_part[column] = pd.Categorical(series, categories=levels)
    return pd.concat([numeric_part, cat_part], axis=1)


def materialize_for_hgb(xgb_frame):
    """HGB needs categorical codes as integers (NaN -> -1) since it does not
    consume pandas categorical dtype with NaN identically to xgboost."""
    numeric_part = xgb_frame[list(NUMERIC_COLUMNS)].astype(float)
    cat_codes = pd.DataFrame(index=xgb_frame.index)
    for column in CATEGORICAL_COLUMNS:
        cat_codes[column] = xgb_frame[column].cat.codes.astype(np.int32)
    return pd.concat([numeric_part, cat_codes], axis=1)


def fit_category_levels(records):
    frame = add_geo_first_tokens(pd.DataFrame(records))
    levels = {}
    for column in CATEGORICAL_COLUMNS:
        if column in frame.columns:
            levels[column] = list(pd.Series(frame[column].astype(str)).dropna().unique())
        else:
            levels[column] = []
    return levels


def make_target_array(records):
    return np.array([record[TARGET_KEY] for record in records], dtype=np.float64)


def build_xgb():
    return XGBRegressor(
        objective="reg:absoluteerror",
        n_estimators=4000,
        learning_rate=0.05,
        max_depth=6,
        min_child_weight=5,
        subsample=0.8,
        colsample_bytree=0.6,
        reg_lambda=1.0,
        tree_method="hist",
        n_jobs=-1,
        random_state=42,
        enable_categorical=True,
    )


def build_hgb():
    cat_indices = list(range(len(NUMERIC_COLUMNS), len(NUMERIC_COLUMNS) + len(CATEGORICAL_COLUMNS)))
    return HistGradientBoostingRegressor(
        loss="absolute_error",
        max_iter=1000,
        learning_rate=0.05,
        max_leaf_nodes=63,
        min_samples_leaf=20,
        l2_regularization=0.1,
        random_state=42,
        categorical_features=cat_indices,
    )


def fit_predict(train_records, validation_records):
    category_levels = fit_category_levels(train_records)

    train_pre = make_feature_frame_pre(train_records)
    val_pre = make_feature_frame_pre(validation_records)

    type_means, global_mean = compute_built_rel_type_map(train_pre)
    train_pre = add_built_rel_type(train_pre, type_means, global_mean)
    val_pre = add_built_rel_type(val_pre, type_means, global_mean)

    train_frame = materialize_features(train_pre, category_levels)
    val_frame = materialize_features(val_pre, category_levels)

    y_train = make_target_array(train_records)
    y_train_log = np.log1p(y_train)

    # XGB anchor (global + per-type sub-models, exactly the v4 W''''' recipe)
    global_model = build_xgb()
    global_model.fit(train_frame, y_train_log)
    pred_global = np.expm1(global_model.predict(val_frame))

    train_types = pd.DataFrame(train_records).get("property_type", pd.Series([""] * len(train_records))).astype(str).values
    val_types = pd.DataFrame(validation_records).get("property_type", pd.Series([""] * len(validation_records))).astype(str).values

    pred_xgb = pred_global.copy()
    BLEND = 0.3
    SUB_TYPES = [
        "UNE MAISON",
        "UN APPARTEMENT",
        "TERRAIN DE TYPE TERRE ET PRE",
        "TERRAIN DE TYPE TAB",
        "ACTIVITE",
    ]
    for sub_type in SUB_TYPES:
        train_mask = train_types == sub_type
        val_mask = val_types == sub_type
        if train_mask.sum() < 100 or val_mask.sum() == 0:
            continue
        sub_train_frame = train_frame[train_mask]
        sub_y = y_train_log[train_mask]
        sub_model = build_xgb()
        sub_model.fit(sub_train_frame, sub_y)
        sub_pred_val = np.expm1(sub_model.predict(val_frame[val_mask]))
        pred_xgb[val_mask] = (1 - BLEND) * pred_global[val_mask] + BLEND * sub_pred_val

    # HGB head on log target
    train_hgb = materialize_for_hgb(train_frame)
    val_hgb = materialize_for_hgb(val_frame)
    hgb = build_hgb()
    hgb.fit(train_hgb, y_train_log)
    pred_hgb = np.expm1(hgb.predict(val_hgb))

    return HGB_BLEND * pred_hgb + (1 - HGB_BLEND) * pred_xgb
