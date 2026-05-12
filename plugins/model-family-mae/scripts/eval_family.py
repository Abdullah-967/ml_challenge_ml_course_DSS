"""Standalone 5-fold CV-MAE evaluator for model-family experiments."""

from __future__ import annotations

import argparse
import json
import time
from datetime import datetime
from pathlib import Path

import numpy as np
from sklearn.metrics import mean_absolute_error
from sklearn.model_selection import KFold

from mfm_experiment import TARGET_KEY, load_experiment, load_json, normalize_predictions
from mfm_io import append_tsv, rounded


def make_target_array(records):
    return np.array([record[TARGET_KEY] for record in records], dtype=np.float64)


def evaluate(module, records, n_splits, random_state):
    targets = make_target_array(records)
    kf = KFold(n_splits=n_splits, shuffle=True, random_state=random_state)
    fold_maes = []

    for fold, (train_index, validation_index) in enumerate(kf.split(np.arange(len(records)))):
        train_split = [records[index] for index in train_index]
        validation_split = [records[index] for index in validation_index]

        fold_start = time.perf_counter()
        predictions = normalize_predictions(module.fit_predict(train_split, validation_split))
        if len(predictions) != len(validation_split):
            raise ValueError(
                f"fit_predict returned {len(predictions)} predictions for "
                f"{len(validation_split)} validation records"
            )

        fold_mae = mean_absolute_error(targets[validation_index], predictions)
        fold_seconds = time.perf_counter() - fold_start
        fold_maes.append(fold_mae)
        print(f"fold_{fold}_mae: {fold_mae:,.4f} ({fold_seconds:.2f}s)")

    fold_maes = np.array(fold_maes, dtype=np.float64)
    return float(fold_maes.mean()), float(fold_maes.std(ddof=0))


def append_results(path, row):
    append_tsv(Path(path), row)


def parse_args():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("experiment", help="Path to experiments/<model_family>/experiment.py")
    parser.add_argument("--train", default="dataset/train.json", help="Training JSON path")
    parser.add_argument("--splits", type=int, default=5, help="Number of CV folds")
    parser.add_argument("--seed", type=int, default=42, help="KFold random seed")
    parser.add_argument("--results-tsv", help="Optional results.tsv path to append")
    parser.add_argument("--run-id", default="", help="Run id for results.tsv")
    parser.add_argument("--stage", default="smoke", help="Stage label for results.tsv")
    parser.add_argument("--model-family", default="", help="Model family label")
    parser.add_argument("--feature-lane", default="", help="Feature lane label")
    parser.add_argument("--status", default="keep", help="Status label for results.tsv")
    parser.add_argument("--params-summary", default="", help="Short parameter summary")
    parser.add_argument("--description", default="", help="One-sentence run description")
    return parser.parse_args()


def main():
    args = parse_args()
    start = time.perf_counter()
    module = load_experiment(args.experiment)
    records = load_json(args.train)
    cv_mae, cv_mae_std = evaluate(module, records, args.splits, args.seed)
    runtime_seconds = time.perf_counter() - start

    result = {
        "cv_mae": cv_mae,
        "cv_mae_std": cv_mae_std,
        "runtime_seconds": runtime_seconds,
        "splits": args.splits,
        "seed": args.seed,
        "experiment": str(Path(args.experiment)),
    }

    print(f"cv_mae: {cv_mae:,.6f}")
    print(f"cv_mae_std: {cv_mae_std:,.6f}")
    print(f"runtime_seconds: {runtime_seconds:.2f}")
    print(json.dumps(result, indent=2))

    if args.results_tsv:
        run_id = args.run_id or datetime.now().strftime("%Y%m%d-%H%M%S")
        append_results(
            args.results_tsv,
            {
                "commit_or_run_id": run_id,
                "stage": args.stage,
                "model_family": args.model_family or getattr(module, "MODEL_FAMILY", ""),
                "feature_lane": args.feature_lane or getattr(module, "FEATURE_LANE", ""),
                "cv_mae": rounded(cv_mae),
                "cv_mae_std": rounded(cv_mae_std),
                "runtime_seconds": rounded(runtime_seconds),
                "status": args.status,
                "params_summary": args.params_summary or getattr(module, "PARAMS_SUMMARY", ""),
                "description": args.description,
            },
        )


if __name__ == "__main__":
    main()
