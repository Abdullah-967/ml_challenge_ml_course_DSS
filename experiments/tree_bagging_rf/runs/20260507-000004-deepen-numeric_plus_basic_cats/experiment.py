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
RECIPE_VARIANT = "deepen_iter2_commune_target_enc"
PARAMS_SUMMARY = (
    "RandomForestRegressor(n_est=200,max_depth=18,min_samples_leaf=2,"
    "max_features=sqrt,n_jobs=-1,random_state=42),"
    "all_numeric+ratios+OHE(property_type,transaction_type)+commune_target_enc20"
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


def add_commune_first(frame):
    frame = frame.copy()
    src = frame.get("commune_codes") if "commune_codes" in frame.columns else pd.Series([np.nan] * len(frame), index=frame.index)
    frame["commune_first"] = src.map(first_token)
    return frame


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
    enc_map, global_mean = fit_target_encoding(train_frame["commune_first"], train_target, TARGET_ENC_SMOOTH)
    train_frame = train_frame.copy()
    val_frame = val_frame.copy()
    train_frame["commune_target_enc"] = apply_target_encoding(train_frame["commune_first"], enc_map, global_mean)
    val_frame["commune_target_enc"] = apply_target_encoding(val_frame["commune_first"], enc_map, global_mean)
    return train_frame, val_frame


def infer_numeric_features(frame):
    features = []
    for column in frame.columns:
        if column == TARGET_KEY or column in ID_COLUMNS:
            continue
        if column in CATEGORICAL_COLUMNS or column == "commune_first" or column == "commune_codes":
            continue
        values = pd.to_numeric(frame[column], errors="coerce")
        if values.notna().any():
            features.append(column)
    return features


def make_target_array(records):
    return np.array([record[TARGET_KEY] for record in records], dtype=np.float64)


def prepare_frames(train_records, validation_records, train_target):
    train_frame = add_derived_ratios(add_commune_first(pd.DataFrame(train_records)))
    val_frame = add_derived_ratios(add_commune_first(pd.DataFrame(validation_records)))
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
    y_train = make_target_array(train_records)
    train_frame, val_frame = prepare_frames(train_records, validation_records, y_train)
    numeric_columns = infer_numeric_features(train_frame)
    train_X = select_columns(train_frame, numeric_columns, CATEGORICAL_COLUMNS)
    val_X = select_columns(val_frame, numeric_columns, CATEGORICAL_COLUMNS)
    model = build_model(numeric_columns, CATEGORICAL_COLUMNS)
    model.fit(train_X, y_train)
    return model.predict(val_X)
