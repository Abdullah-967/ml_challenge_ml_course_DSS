"""RandomForest deepen iter2 recipe.

Stage 2 deepen iter2. Single-knob: add commune_first target encoding
(smoothed=20, fold-safe). Cumulative on top of deepen iter1
(all_numeric + ratios + OHE cats).
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
RECIPE_VARIANT = "tune_iter6_max_features_0_7"
PARAMS_SUMMARY = (
    "RandomForestRegressor(criterion=absolute_error,n_est=200,max_depth=None,"
    "min_samples_leaf=2,max_features=0.7,n_jobs=-1,random_state=42),log1p_target"
)
RF_CRITERION = "absolute_error"
RF_N_ESTIMATORS = 200
RF_MAX_DEPTH = None
RF_MIN_SAMPLES_LEAF = 2
RF_MAX_FEATURES = 0.7
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
TARGET_ENC_SMOOTH = 20
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


def build_model(numeric_columns, categorical_columns):
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
                    n_estimators=RF_N_ESTIMATORS,
                    max_depth=RF_MAX_DEPTH,
                    min_samples_leaf=RF_MIN_SAMPLES_LEAF,
                    max_features=RF_MAX_FEATURES,
                    criterion=RF_CRITERION,
                    n_jobs=-1,
                    random_state=42,
                ),
            ),
        ]
    )


def fit_predict(train_records, validation_records):
    y_train = make_target_array(train_records)
    train_frame, val_frame = prepare_frames(train_records, validation_records, y_train)
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
