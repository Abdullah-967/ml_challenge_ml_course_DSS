"""tree_bagging_rf_v2 anchor recipe.

V2 family premise: build on v1's promoted recipe (cv_mae 50663.64 seed=42,
50843.01 seed=2026, 2-seed mean 50753.32) and push beyond global champion
HGB iter21 (50934.78) by a noise-aware margin via untried RF lifts:
fold-safe group-stat ratios (built_rel_type, built_per_land), id token
counts, room-layout distribution/density, ExtraTrees variant, n_est ramp,
per-property-type sub-model architecture.

This file IS the v1 promoted recipe verbatim (random_state=42), serving as
v2's smoke anchor. Each new iteration adds exactly one knob on top.
"""

from __future__ import annotations

import numpy as np
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.ensemble import ExtraTreesRegressor, RandomForestRegressor
from sklearn.impute import SimpleImputer
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder

TARGET_KEY = "property_value"
MODEL_FAMILY = "tree_bagging_rf_v2"
FEATURE_LANE = "lane_a_log_skewed"
RECIPE_VARIANT = "v2_deepen_iter8_log_skewed_numerics"
PARAMS_SUMMARY = (
    "RandomForestRegressor(criterion=absolute_error,n_est=200,max_depth=18,"
    "min_samples_leaf=2,max_features=0.4,bootstrap=False,n_jobs=-1,random_state=42),log1p_target,smooth=10,"
    "log_skewed_numerics"
)
RF_CRITERION = "absolute_error"
RF_N_ESTIMATORS = 200
RF_MAX_DEPTH = 18
RF_MIN_SAMPLES_LEAF = 2
SUB_MODEL_N_ESTIMATORS = 100
SUB_MODEL_BLEND = 0.3
TOP_PROPERTY_TYPES = (
    "UNE MAISON",
    "UN APPARTEMENT",
    "TERRAIN DE TYPE TERRE ET PRE",
)
RF_MAX_FEATURES = 0.4
RF_BOOTSTRAP = False
USE_OHE = False
PRESENCE_FLAG_COLUMNS = (
    ("has_apt", "num_apartments"),
    ("has_house", "num_houses"),
    ("has_land", "land_area"),
    ("has_commercial", "num_commercial"),
    ("has_built", "built_area"),
)
USE_LOG_TARGET = True

ID_COLUMNS = {"parcel_ids", "transferred_parcel_ids"}
CATEGORICAL_COLUMNS = ("property_type", "transaction_type")
DERIVED_RATIO_COLUMNS = (
    "built_per_premise",
    "land_per_lot",
    "commercial_share",
    "apt_share",
    "houses_per_premise",
)
TARGET_ENC_SMOOTH = 10
MISSING_TOKEN = "__missing__"


def first_token(value):
    if value is None or (isinstance(value, float) and np.isnan(value)):
        return np.nan
    text = str(value).strip()
    if not text:
        return np.nan
    return text.split(",")[0].strip()


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


def add_presence_flags(frame):
    frame = frame.copy()
    for flag_name, source_col in PRESENCE_FLAG_COLUMNS:
        values = pd.to_numeric(frame.get(source_col), errors="coerce")
        frame[flag_name] = (values.fillna(0) > 0).astype("int8")
    return frame


def add_commune_first(frame):
    frame = frame.copy()
    src = frame.get("commune_codes") if "commune_codes" in frame.columns else pd.Series([np.nan] * len(frame), index=frame.index)
    frame["commune_first"] = src.map(first_token)
    cad = frame.get("cadastral_sections") if "cadastral_sections" in frame.columns else pd.Series([np.nan] * len(frame), index=frame.index)
    frame["cadastral_first"] = cad.map(first_token)
    return frame


def fit_commune_frequency(commune_series):
    counts = commune_series.dropna().value_counts()
    return counts.to_dict()


def apply_commune_frequency(commune_series, freq_map):
    return commune_series.map(freq_map).astype(float).fillna(0.0)


def fit_target_encoding(commune_series, target_array, smooth):
    df = pd.DataFrame({"c": commune_series.values, "y": target_array})
    df = df.dropna(subset=["c"])
    global_mean = float(np.mean(target_array))
    grouped = df.groupby("c")["y"]
    counts = grouped.count()
    means = grouped.mean()
    encoded = (counts * means + smooth * global_mean) / (counts + smooth)
    return encoded.to_dict(), global_mean


def apply_target_encoding(commune_series, encoding_map, fallback):
    return commune_series.map(encoding_map).astype(float).fillna(fallback)


def fit_group_mean(group_series, value_series):
    df = pd.DataFrame({"g": group_series.values, "v": value_series.values})
    df = df.dropna(subset=["g"])
    df["v"] = pd.to_numeric(df["v"], errors="coerce")
    df = df.dropna(subset=["v"])
    if not len(df):
        return {}, 0.0
    return df.groupby("g")["v"].mean().to_dict(), float(df["v"].mean())


def apply_group_relative(group_series, value_series, mean_map, fallback_mean):
    means = group_series.map(mean_map).astype(float).fillna(fallback_mean)
    means = means.where(means > 0, fallback_mean if fallback_mean > 0 else 1.0)
    values = pd.to_numeric(value_series, errors="coerce")
    return values / means


def add_built_rel_type(train_frame, val_frame):
    mean_map, fallback = fit_group_mean(train_frame["property_type"], train_frame.get("built_area"))
    train_frame = train_frame.copy()
    val_frame = val_frame.copy()
    train_frame["built_rel_type"] = apply_group_relative(
        train_frame["property_type"], train_frame.get("built_area"), mean_map, fallback
    )
    val_frame["built_rel_type"] = apply_group_relative(
        val_frame["property_type"], val_frame.get("built_area"), mean_map, fallback
    )
    return train_frame, val_frame


def count_tokens(value):
    if value is None or (isinstance(value, float) and np.isnan(value)):
        return 0
    text = str(value).strip()
    if not text:
        return 0
    return sum(1 for piece in text.split(",") if piece.strip())


def add_id_token_counts(train_frame, val_frame):
    train_frame = train_frame.copy()
    val_frame = val_frame.copy()
    for src_col, out_col in (
        ("parcel_ids", "parcel_id_count"),
        ("transferred_parcel_ids", "transferred_parcel_id_count"),
    ):
        train_frame[out_col] = (
            train_frame.get(src_col, pd.Series([np.nan] * len(train_frame))).map(count_tokens).astype("int32")
        )
        val_frame[out_col] = (
            val_frame.get(src_col, pd.Series([np.nan] * len(val_frame))).map(count_tokens).astype("int32")
        )
    return train_frame, val_frame


ROOM_DENSITY_PAIRS = (
    ("area_apt_1_room", "num_apt_1_room", "density_apt_1_room"),
    ("area_apt_2_rooms", "num_apt_2_rooms", "density_apt_2_rooms"),
    ("area_apt_3_rooms", "num_apt_3_rooms", "density_apt_3_rooms"),
    ("area_apt_4_rooms", "num_apt_4_rooms", "density_apt_4_rooms"),
    ("area_apt_5plus_rooms", "num_apt_5plus_rooms", "density_apt_5plus_rooms"),
    ("area_house_1_room", "num_house_1_room", "density_house_1_room"),
    ("area_house_2_rooms", "num_house_2_rooms", "density_house_2_rooms"),
    ("area_house_3_rooms", "num_house_3_rooms", "density_house_3_rooms"),
    ("area_house_4_rooms", "num_house_4_rooms", "density_house_4_rooms"),
    ("area_house_5plus_rooms", "num_house_5plus_rooms", "density_house_5plus_rooms"),
)


def add_room_density(train_frame, val_frame):
    train_frame = train_frame.copy()
    val_frame = val_frame.copy()
    for area_col, num_col, out_col in ROOM_DENSITY_PAIRS:
        train_frame[out_col] = safe_div(train_frame.get(area_col), train_frame.get(num_col))
        val_frame[out_col] = safe_div(val_frame.get(area_col), val_frame.get(num_col))
    return train_frame, val_frame


def add_target_encoding_columns(train_frame, val_frame, train_target):
    train_frame = train_frame.copy()
    val_frame = val_frame.copy()
    for src_col, out_col in (
        ("commune_first", "commune_target_enc"),
        ("cadastral_first", "cadastral_target_enc"),
        ("property_type", "property_type_target_enc"),
        ("transaction_type", "transaction_type_target_enc"),
    ):
        enc_map, global_mean = fit_target_encoding(train_frame[src_col], train_target, TARGET_ENC_SMOOTH)
        train_frame[out_col] = apply_target_encoding(train_frame[src_col], enc_map, global_mean)
        val_frame[out_col] = apply_target_encoding(val_frame[src_col], enc_map, global_mean)
    freq_map = fit_commune_frequency(train_frame["commune_first"])
    train_frame["commune_freq"] = apply_commune_frequency(train_frame["commune_first"], freq_map)
    val_frame["commune_freq"] = apply_commune_frequency(val_frame["commune_first"], freq_map)
    return train_frame, val_frame


def infer_numeric_features(frame):
    features = []
    for column in frame.columns:
        if column == TARGET_KEY or column in ID_COLUMNS:
            continue
        if column in CATEGORICAL_COLUMNS:
            continue
        if column in ("commune_first", "commune_codes", "cadastral_first", "cadastral_sections"):
            continue
        values = pd.to_numeric(frame[column], errors="coerce")
        if values.notna().any():
            features.append(column)
    return features


def make_target_array(records):
    return np.array([record[TARGET_KEY] for record in records], dtype=np.float64)


def prepare_frames(train_records, validation_records, train_target):
    train_frame = add_presence_flags(add_derived_ratios(add_commune_first(pd.DataFrame(train_records))))
    val_frame = add_presence_flags(add_derived_ratios(add_commune_first(pd.DataFrame(validation_records))))
    train_frame, val_frame = add_built_rel_type(train_frame, val_frame)
    train_frame, val_frame = add_target_encoding_columns(train_frame, val_frame, train_target)
    return train_frame, val_frame


def select_columns(frame, numeric_columns, categorical_columns):
    numeric = (
        frame.reindex(columns=numeric_columns)
        .apply(pd.to_numeric, errors="coerce")
        .replace([np.inf, -np.inf], np.nan)
    )
    cat = frame.reindex(columns=list(categorical_columns)).astype(object)
    for col in cat.columns:
        cat[col] = cat[col].where(cat[col].notna(), MISSING_TOKEN).astype(str)
    return pd.concat([numeric, cat], axis=1)


def build_model(numeric_columns, categorical_columns, n_estimators=RF_N_ESTIMATORS):
    transformers = [("num", SimpleImputer(strategy="median"), list(numeric_columns))]
    if USE_OHE and categorical_columns:
        transformers.append(
            (
                "cat",
                OneHotEncoder(handle_unknown="ignore", sparse_output=False),
                list(categorical_columns),
            )
        )
    preprocessor = ColumnTransformer(transformers=transformers)
    return Pipeline(
        [
            ("preprocessor", preprocessor),
            (
                "model",
                RandomForestRegressor(
                    n_estimators=n_estimators,
                    max_depth=RF_MAX_DEPTH,
                    min_samples_leaf=RF_MIN_SAMPLES_LEAF,
                    max_features=RF_MAX_FEATURES,
                    criterion=RF_CRITERION,
                    bootstrap=RF_BOOTSTRAP,
                    n_jobs=-1,
                    random_state=42,
                ),
            ),
        ]
    )


LOG_SKEWED_COLUMNS = (
    "built_area",
    "land_area",
    "house_area",
    "apartment_area",
    "num_premises",
    "num_apartments",
    "num_houses",
    "num_lots",
    "num_parcels",
)


def add_log_skewed_numerics(train_frame, val_frame):
    train_frame = train_frame.copy()
    val_frame = val_frame.copy()
    for col in LOG_SKEWED_COLUMNS:
        if col not in train_frame.columns:
            continue
        train_values = pd.to_numeric(train_frame[col], errors="coerce").clip(lower=0).fillna(0)
        val_values = pd.to_numeric(val_frame[col], errors="coerce").clip(lower=0).fillna(0)
        train_frame[f"{col}_log"] = np.log1p(train_values)
        val_frame[f"{col}_log"] = np.log1p(val_values)
    return train_frame, val_frame


def fit_predict(train_records, validation_records):
    y_train = make_target_array(train_records)
    train_frame, val_frame = prepare_frames(train_records, validation_records, y_train)
    train_frame, val_frame = add_log_skewed_numerics(train_frame, val_frame)
    numeric_columns = infer_numeric_features(train_frame)
    cat_cols = CATEGORICAL_COLUMNS if USE_OHE else ()
    train_X = select_columns(train_frame, numeric_columns, cat_cols)
    val_X = select_columns(val_frame, numeric_columns, cat_cols)
    model = build_model(numeric_columns, cat_cols)
    if USE_LOG_TARGET:
        model.fit(train_X, np.log1p(y_train))
        return np.expm1(model.predict(val_X))
    model.fit(train_X, y_train)
    return model.predict(val_X)
