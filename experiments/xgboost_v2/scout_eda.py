"""Scout EDA: per-column predictive power vs property_value (training only).

Outputs a sorted ranking of single-column signal strength to inform data-driven
smoke lane groupings. No test data touched.
"""

from __future__ import annotations

import json
import math
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.feature_selection import mutual_info_regression
from sklearn.model_selection import KFold
from sklearn.tree import DecisionTreeRegressor
from sklearn.metrics import mean_absolute_error

ROOT = Path(__file__).resolve().parents[2]
TRAIN_PATH = ROOT / "dataset" / "train.json"
TARGET = "property_value"
ID_COLS = {"parcel_ids", "transferred_parcel_ids"}


def load_train_records():
    with open(TRAIN_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


def first_token(value):
    if value is None or (isinstance(value, float) and (value != value)):
        return None
    text = str(value).strip()
    if not text:
        return None
    return text.split(",")[0].strip()


def to_numeric_frame(records):
    frame = pd.DataFrame(records)
    return frame


def column_kind(series):
    """Classify column as numeric, low_card_cat, multi_value_str, or skip."""
    if series.name == TARGET:
        return "target"
    if series.name in ID_COLS:
        return "id"
    numeric = pd.to_numeric(series, errors="coerce")
    if numeric.notna().mean() > 0.5:
        return "numeric"
    n_unique = series.dropna().astype(str).str.split(",").str[0].nunique()
    if n_unique <= 50:
        return "low_card_cat"
    return "multi_value_str"


def single_col_cv_mae(x, y, kind):
    """5-fold CV MAE using a single feature with shallow tree (depth=4)."""
    kf = KFold(n_splits=5, shuffle=True, random_state=42)
    fold_maes = []
    if kind == "numeric":
        x_arr = pd.to_numeric(x, errors="coerce").to_numpy().reshape(-1, 1)
        # Median-impute
        med = np.nanmedian(x_arr)
        x_arr = np.where(np.isnan(x_arr), med, x_arr)
    else:
        # low_card_cat or multi_value_str: factorize first token
        tokens = x.map(first_token).fillna("__missing__").astype(str)
        codes, _ = pd.factorize(tokens)
        x_arr = codes.reshape(-1, 1).astype(np.float64)
    y_arr = np.asarray(y, dtype=np.float64)
    for tr_idx, va_idx in kf.split(x_arr):
        tree = DecisionTreeRegressor(max_depth=4, min_samples_leaf=20, random_state=42)
        tree.fit(x_arr[tr_idx], y_arr[tr_idx])
        pred = tree.predict(x_arr[va_idx])
        fold_maes.append(mean_absolute_error(y_arr[va_idx], pred))
    return float(np.mean(fold_maes)), float(np.std(fold_maes))


def median_baseline_mae(y):
    kf = KFold(n_splits=5, shuffle=True, random_state=42)
    fold_maes = []
    y_arr = np.asarray(y, dtype=np.float64)
    for tr_idx, va_idx in kf.split(y_arr):
        med = np.median(y_arr[tr_idx])
        fold_maes.append(mean_absolute_error(y_arr[va_idx], np.full_like(y_arr[va_idx], med)))
    return float(np.mean(fold_maes))


def numeric_correlation(x, y):
    x_num = pd.to_numeric(x, errors="coerce")
    mask = x_num.notna() & pd.Series(y).notna()
    if mask.sum() < 30:
        return float("nan"), float("nan")
    pearson = float(x_num[mask].corr(pd.Series(y)[mask], method="pearson"))
    spearman = float(x_num[mask].corr(pd.Series(y)[mask], method="spearman"))
    return pearson, spearman


def main():
    records = load_train_records()
    frame = to_numeric_frame(records)
    y = pd.to_numeric(frame[TARGET], errors="coerce").to_numpy()
    n_total = len(frame)
    print(f"loaded {n_total} train records, {len(frame.columns)} columns")

    base_mae = median_baseline_mae(y)
    print(f"median_only_baseline_5fold_mae: {base_mae:.2f}")

    rows = []
    for col in frame.columns:
        if col == TARGET:
            continue
        kind = column_kind(frame[col])
        if kind in ("id", "target"):
            continue
        non_null_frac = frame[col].notna().mean() if kind != "numeric" else pd.to_numeric(frame[col], errors="coerce").notna().mean()
        try:
            cv_mae, cv_std = single_col_cv_mae(frame[col], y, kind)
        except Exception as exc:
            print(f"{col}: failed -> {exc}")
            continue
        if kind == "numeric":
            pearson, spearman = numeric_correlation(frame[col], y)
        else:
            pearson, spearman = float("nan"), float("nan")
        n_unique = (
            pd.to_numeric(frame[col], errors="coerce").nunique()
            if kind == "numeric"
            else frame[col].map(first_token).nunique()
        )
        improvement = base_mae - cv_mae
        rows.append({
            "column": col,
            "kind": kind,
            "n_unique": int(n_unique) if pd.notna(n_unique) else 0,
            "non_null_frac": round(non_null_frac, 3),
            "pearson_vs_target": round(pearson, 3) if not math.isnan(pearson) else None,
            "spearman_vs_target": round(spearman, 3) if not math.isnan(spearman) else None,
            "single_col_cv_mae": round(cv_mae, 1),
            "improvement_vs_median": round(improvement, 1),
        })

    df = pd.DataFrame(rows).sort_values("single_col_cv_mae", ascending=True)
    out_path = Path(__file__).resolve().parent / "scout_eda_ranking.tsv"
    df.to_csv(out_path, sep="\t", index=False)
    print()
    print(df.to_string(index=False))
    print()
    print(f"saved to {out_path}")


if __name__ == "__main__":
    main()
