"""Shared paths and file helpers for the model-family MAE plugin."""

from __future__ import annotations

import csv
import json
import math
from datetime import datetime
from pathlib import Path
from typing import Any


RESULT_FIELDS = [
    "commit_or_run_id",
    "stage",
    "model_family",
    "feature_lane",
    "cv_mae",
    "cv_mae_std",
    "validation_mae",
    "runtime_seconds",
    "status",
    "params_summary",
    "description",
]

DEFAULT_SMOKE_LANES = ["all_numeric", "numeric_plus_basic_cats", "geo_signal"]

SMOKE_LANES_BY_FAMILY = {
    "linear_robust": ["baseline_numeric", "all_numeric", "numeric_plus_basic_cats"],
    "linear": ["baseline_numeric", "all_numeric", "numeric_plus_basic_cats"],
    "ridge": ["baseline_numeric", "all_numeric", "numeric_plus_basic_cats"],
    "tree_bagging": ["baseline_numeric", "all_numeric", "derived_ratios"],
    "boosting": ["all_numeric", "numeric_plus_basic_cats", "geo_signal"],
    "hist_gradient_boosting": ["all_numeric", "numeric_plus_basic_cats", "geo_signal"],
    "xgboost": ["all_numeric", "numeric_plus_basic_cats", "geo_signal"],
    "xgboost_v3": ["baseline_three_only"],
    "xgboost_v4": ["v2_plus_geo_hierarchy", "v2_plus_temporal_cats", "v2_plus_fold_te"],
    "median_quantile": ["baseline_numeric", "all_numeric", "numeric_plus_basic_cats"],
}

PLUGIN_ROOT = Path(__file__).resolve().parents[1]
EVAL_SCRIPT = PLUGIN_ROOT / "scripts" / "eval_family.py"
TEMPLATE_PATH = PLUGIN_ROOT / "templates" / "experiment_template.py"


def read_json(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as handle:
        json.dump(payload, handle, indent=2)
        handle.write("\n")


def project_root(path: str) -> Path:
    return Path(path).resolve()


def family_dir(root: Path, family: str) -> Path:
    return root / "experiments" / family


def timestamp() -> str:
    return datetime.now().strftime("%Y%m%d-%H%M%S")


def load_tsv(path: Path) -> list[dict[str, str]]:
    if not path.exists() or path.stat().st_size == 0:
        return []
    with path.open("r", encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def append_tsv(path: Path, row: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    write_header = not path.exists() or path.stat().st_size == 0
    with path.open("a", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=RESULT_FIELDS, delimiter="\t", extrasaction="ignore")
        if write_header:
            writer.writeheader()
        writer.writerow({field: row.get(field, "") for field in RESULT_FIELDS})


def relative_to_root(path: Path, root: Path) -> str:
    try:
        return str(path.relative_to(root))
    except ValueError:
        return str(path)


def rounded(value: Any) -> str:
    if value is None or value == "":
        return ""
    if isinstance(value, float) and math.isnan(value):
        return ""
    return f"{float(value):.6f}"


def write_json_or_print(payload: dict[str, Any], output: str | None) -> None:
    if output:
        write_json(Path(output), payload)
    else:
        print(json.dumps(payload, indent=2))
