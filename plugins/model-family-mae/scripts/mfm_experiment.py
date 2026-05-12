"""Shared experiment-loading helpers for model-family MAE scripts."""

from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path
from typing import Any

import numpy as np

TARGET_KEY = "property_value"


def load_json(path: str | Path) -> list[dict[str, Any]]:
    with Path(path).open("r", encoding="utf-8") as handle:
        return json.load(handle)


def load_experiment(module_path: str | Path):
    module_path = Path(module_path).resolve()
    sys.path.insert(0, str(module_path.parent))
    spec = importlib.util.spec_from_file_location("model_family_experiment", module_path)
    if spec is None or spec.loader is None:
        raise ImportError(f"Could not import experiment module: {module_path}")

    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)

    if not hasattr(module, "fit_predict"):
        raise AttributeError(f"{module_path} must define fit_predict(train_records, validation_records)")

    return module


def normalize_predictions(predictions):
    if isinstance(predictions, list) and predictions and isinstance(predictions[0], dict):
        predictions = [row[TARGET_KEY] for row in predictions]

    values = np.asarray(predictions, dtype=np.float64).reshape(-1)
    if not np.isfinite(values).all():
        raise ValueError("Predictions contain NaN or infinite values")
    return values
