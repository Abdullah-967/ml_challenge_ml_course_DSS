"""xgboost_v10 deepen iter2 -- anchor + transfer features (lift measurement).

Single-knob change vs deepen iter1: add four transfer-mode features
(n_transferred, n_parcels_kept, transfer_overlap_ratio, is_no_transfer)
derived from parcel_ids vs transferred_parcel_ids set arithmetic. Same
n_est=1000 capacity, same architecture. Compare cv_mae to iter1 (48772.08)
to measure the transfer-feature lift.
"""

from __future__ import annotations

import numpy as np
import pandas as pd
from xgboost import XGBRegressor

TARGET_KEY = "property_value"
MODEL_FAMILY = "xgboost_v10"
FEATURE_LANE = "shrunk_v6_anchor_n1000_plus_transfer"
RECIPE_VARIANT = "deepen_iter2_plus_transfer4"
PARAMS_SUMMARY = (
    "XGBRegressor(reg:absoluteerror,n_est=1000,lr=0.05,max_depth=6,"
    "mcw=5,subsample=0.8,colsample=0.6,reg_lambda=1.0,hist,enable_categorical=True),"
    "0.7*global+0.3*submodel(top5_types_min200,n_est=1000),log1p,"
    "+transfer4=[n_transferred,n_parcels_kept,transfer_overlap_ratio,is_no_transfer]"
)
DATE_EPOCH = pd.Timestamp("2014-01-01")
USE_LOG_TARGET = True

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
    # Transfer-mode features (deepen iter2 single-knob addition).
    "n_transferred", "n_parcels_kept", "transfer_overlap_ratio", "is_no_transfer",
)
CATEGORICAL_COLUMNS = (
    "property_type", "commune_first", "cadastral_first", "transaction_type",
    "dept_code", "region_code",
)

SUB_MODEL_TOP_K = 5
SUB_MODEL_MIN_COUNT = 200
SUB_MODEL_BLEND = 0.3
N_ESTIMATORS = 1000


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


def _to_id_set(value):
    if value is None:
        return set()
    if isinstance(value, float) and np.isnan(value):
        return set()
    if isinstance(value, list):
        return {
            str(x).strip()
            for x in value
            if x is not None and str(x).strip() and str(x).strip() != "None"
        }
    text = str(value).strip()
    if not text or text == "None":
        return set()
    return {tok.strip() for tok in text.split(",") if tok.strip() and tok.strip() != "None"}


def add_transfer_features(frame):
    frame = frame.copy()
    pi_sets = frame.get("parcel_ids", pd.Series([None] * len(frame))).map(_to_id_set)
    tpi_sets = frame.get(
        "transferred_parcel_ids", pd.Series([None] * len(frame))
    ).map(_to_id_set)
    n_tpi = tpi_sets.map(len)
    inter = [len(p & t) for p, t in zip(pi_sets, tpi_sets)]
    union = [len(p | t) for p, t in zip(pi_sets, tpi_sets)]
    overlap_ratio = [
        (inter[i] / union[i]) if union[i] > 0 else np.nan for i in range(len(frame))
    ]
    frame["n_transferred"] = n_tpi.astype(float)
    frame["n_parcels_kept"] = pd.Series(inter, index=frame.index, dtype=float)
    frame["transfer_overlap_ratio"] = pd.Series(overlap_ratio, index=frame.index, dtype=float)
    frame["is_no_transfer"] = (n_tpi == 0).astype(float)
    return frame


def make_feature_frame_pre(records):
    return add_transfer_features(
        add_derived_ratios(add_date_ordinal(add_geo_first_tokens(pd.DataFrame(records))))
    )


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


def build_model():
    return XGBRegressor(
        objective="reg:absoluteerror",
        n_estimators=N_ESTIMATORS,
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


def top_k_types(records, k=SUB_MODEL_TOP_K, min_count=SUB_MODEL_MIN_COUNT):
    series = pd.DataFrame(records).get("property_type", pd.Series([], dtype=object)).astype(str)
    counts = series[series != "nan"].value_counts()
    counts = counts[counts >= min_count]
    return list(counts.head(k).index)


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
    y_train_log = np.log1p(y_train) if USE_LOG_TARGET else y_train

    global_model = build_model()
    global_model.fit(train_frame, y_train_log)
    pred_global_log = global_model.predict(val_frame)
    pred_global = np.expm1(pred_global_log) if USE_LOG_TARGET else pred_global_log

    train_types = pd.DataFrame(train_records).get(
        "property_type", pd.Series([""] * len(train_records))
    ).astype(str).values
    val_types = pd.DataFrame(validation_records).get(
        "property_type", pd.Series([""] * len(validation_records))
    ).astype(str).values

    final_pred = pred_global.copy()
    sub_types = top_k_types(train_records)
    for sub_type in sub_types:
        train_mask = train_types == sub_type
        val_mask = val_types == sub_type
        if train_mask.sum() < 100 or val_mask.sum() == 0:
            continue
        sub_train_frame = train_frame[train_mask]
        sub_y = y_train_log[train_mask]
        sub_model = build_model()
        sub_model.fit(sub_train_frame, sub_y)
        sub_pred_log = sub_model.predict(val_frame[val_mask])
        sub_pred = np.expm1(sub_pred_log) if USE_LOG_TARGET else sub_pred_log
        final_pred[val_mask] = (
            (1 - SUB_MODEL_BLEND) * pred_global[val_mask]
            + SUB_MODEL_BLEND * sub_pred
        )
    return final_pred
