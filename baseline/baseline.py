#!/usr/bin/env python3
"""Minimal starter baseline that writes predicted.json and predicted.zip."""

import json
import zipfile
from pathlib import Path

import numpy as np
from sklearn.linear_model import Ridge
from sklearn.preprocessing import MinMaxScaler


BASELINE_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = BASELINE_DIR.parent
DATASET_DIR = PROJECT_ROOT / "dataset"

FEATURE_KEYS = ["built_area", "num_lots", "num_commercial"]
TARGET_KEY = "property_value"

def load_json(path):
    """Load a JSON file and return the parsed Python object."""
    with open(path, "r", encoding="utf-8") as handle:
        return json.load(handle)


def fit_ridge_baseline(train_records, target_key="property_value", alpha=10.0):
    """Fit the Ridge baseline on the hardcoded starter features."""
    x_train = np.array(
        [[float(record.get(key, 0.0) or 0.0) for key in FEATURE_KEYS] for record in train_records],
        dtype=np.float64,
    )
    y_train = np.array([record[target_key] for record in train_records], dtype=np.float64)

    scaler = MinMaxScaler()
    x_train = scaler.fit_transform(x_train)

    model = Ridge(alpha=alpha)
    model.fit(x_train, y_train)
    return model, scaler


def predict_records(model, scaler, records):
    """Predict property values for a list of prepared records."""
    x_test = np.array(
        [[float(record.get(key, 0.0) or 0.0) for key in FEATURE_KEYS] for record in records],
        dtype=np.float64,
    )
    x_test = scaler.transform(x_test)
    return [float(value) for value in model.predict(x_test)]


def generate_predictions(
    train_path=DATASET_DIR / "train.json",
    test_path=DATASET_DIR / "test.json",
    prediction_json_path=BASELINE_DIR / "predicted.json",
    prediction_zip_path=BASELINE_DIR / "predicted.zip",
    target_key="property_value",
    alpha=10.0,
):
    """Train the baseline model and write predicted.json plus predicted.zip."""
    train_records = load_json(train_path)
    test_records = load_json(test_path)

    model, scaler = fit_ridge_baseline(train_records, target_key=target_key, alpha=alpha)
    predictions = [{target_key: value} for value in predict_records(model, scaler, test_records)]

    with open(prediction_json_path, "w", encoding="utf-8") as handle:
        json.dump(predictions, handle, indent=2)

    with zipfile.ZipFile(prediction_zip_path, "w", compression=zipfile.ZIP_DEFLATED) as archive:
        archive.write(prediction_json_path, arcname="predicted.json")

    return len(predictions)


def main():
    """Run the minimal starter baseline with the default file names."""
    prediction_count = generate_predictions(
        target_key="property_value",
        alpha=10.0,
    )

    print(f"Wrote {prediction_count} predictions using: {', '.join(FEATURE_KEYS)}")


if __name__ == "__main__":
    main()
