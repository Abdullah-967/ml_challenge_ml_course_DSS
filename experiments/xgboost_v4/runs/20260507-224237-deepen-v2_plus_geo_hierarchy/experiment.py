"""xgboost_v4 deepen iter5 -- single knob: built_rel_type fold-safe group stat.

Carry-forward W': iter3 built_per_land (cv 48996).
This iter adds built_rel_type = built_area / mean(built_area | property_type)
where mean is computed from train fold only.
"""

from __future__ import annotations

import numpy as np
import pandas as pd
from sklearn.impute import SimpleImputer
from sklearn.linear_model import Ridge
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler
from xgboost import XGBRegressor

TARGET_KEY = "property_value"
MODEL_FAMILY = "xgboost_v4"
FEATURE_LANE = "v2_plus_geo_hierarchy"
RECIPE_VARIANT = "deepen_iter19_ridge_residual"
PARAMS_SUMMARY = (
    "XGBRegressor(reg:absoluteerror,n_est=500,lr=0.05,max_depth=6,"
    "mcw=5,subsample=0.8,colsample=0.6,reg_lambda=1.0,hist,enable_categorical=True)+"
    "Ridge(alpha=10.0)_on_residuals"
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
        n_estimators=500,
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
    model = build_model()
    if USE_LOG_TARGET:
        model.fit(train_frame, np.log1p(y_train))
        train_pred = np.expm1(model.predict(train_frame))
        val_pred = np.expm1(model.predict(val_frame))
    else:
        model.fit(train_frame, y_train)
        train_pred = model.predict(train_frame)
        val_pred = model.predict(val_frame)

    train_residuals = y_train - train_pred
    numeric_only_train = (
        train_frame.select_dtypes(include=[np.number])
        .replace([np.inf, -np.inf], np.nan)
    )
    numeric_only_val = (
        val_frame.select_dtypes(include=[np.number])
        .replace([np.inf, -np.inf], np.nan)
    )

    ridge_pipe = Pipeline([
        ("imputer", SimpleImputer(strategy="median")),
        ("scaler", StandardScaler()),
        ("model", Ridge(alpha=10.0)),
    ])
    ridge_pipe.fit(numeric_only_train, train_residuals)
    residual_pred_val = ridge_pipe.predict(numeric_only_val)

    return val_pred + residual_pred_val
