"""Isolated work-item execution for model-family MAE runs."""

from __future__ import annotations

import json
import shutil
import subprocess
import sys
import time
from pathlib import Path
from typing import Any

from mfm_io import EVAL_SCRIPT, family_dir, read_json, relative_to_root, timestamp, write_json


def execute_work_item(
    root: Path,
    work_item_path: str | Path,
    timeout_seconds: int = 600,
    overwrite_experiment: bool = False,
) -> dict[str, Any]:
    item_path = resolve_path(root, work_item_path)
    item = read_json(item_path)
    run_dir, run_experiment = prepare_run(root, item, overwrite_experiment)
    completed = run_evaluator(root, item, run_experiment, run_dir, timeout_seconds)
    result = build_run_result(root, item_path, item, run_dir, run_experiment, completed)
    result_path = run_dir / "result.json"
    write_json(result_path, result)
    return {"result_json": relative_to_root(result_path, root), **result}


def resolve_path(root: Path, path: str | Path) -> Path:
    candidate = Path(path)
    return candidate if candidate.is_absolute() else root / candidate


def prepare_run(root: Path, item: dict[str, Any], overwrite: bool) -> tuple[Path, Path]:
    fdir = family_dir(root, item["family"])
    run_dir = fdir / "runs" / item.get("run_id", f"{timestamp()}-{item.get('stage', 'run')}")
    run_dir.mkdir(parents=True, exist_ok=True)
    run_experiment = run_dir / "experiment.py"
    if overwrite or not run_experiment.exists():
        source = root / item.get("experiment_source", f"experiments/{item['family']}/current_experiment.py")
        if not source.exists():
            raise SystemExit(f"experiment_source does not exist: {source}")
        shutil.copyfile(source, run_experiment)
    return run_dir, run_experiment


def run_evaluator(
    root: Path,
    item: dict[str, Any],
    experiment: Path,
    run_dir: Path,
    timeout_seconds: int,
) -> dict[str, Any]:
    started = time.perf_counter()
    try:
        proc = subprocess.run(
            eval_command(item, experiment),
            cwd=root,
            text=True,
            capture_output=True,
            timeout=timeout_seconds,
        )
        status = "completed" if proc.returncode == 0 else "failed"
        stdout, stderr, returncode = proc.stdout, proc.stderr, proc.returncode
    except subprocess.TimeoutExpired as exc:
        status = "timeout"
        stdout, stderr, returncode = exc.stdout or "", exc.stderr or "timeout", None
    write_run_logs(run_dir, stdout, stderr)
    return {
        "status": status,
        "returncode": returncode,
        "elapsed": time.perf_counter() - started,
        "measured": extract_result_json(stdout),
    }


def eval_command(item: dict[str, Any], experiment: Path) -> list[str]:
    return [
        sys.executable,
        str(EVAL_SCRIPT),
        str(experiment),
        "--stage",
        item.get("stage", "smoke"),
        "--model-family",
        item["family"],
        "--feature-lane",
        item.get("feature_lane", ""),
        "--description",
        item.get("description", ""),
        "--params-summary",
        item.get("params_summary", ""),
        "--seed",
        str(item.get("seed", 42)),
    ]


def write_run_logs(run_dir: Path, stdout: str, stderr: str) -> None:
    (run_dir / "stdout.log").write_text(stdout, encoding="utf-8")
    (run_dir / "stderr.log").write_text(stderr, encoding="utf-8")


def extract_result_json(stdout: str) -> dict[str, Any]:
    start = stdout.rfind("{")
    if start == -1:
        return {}
    try:
        return json.loads(stdout[start:])
    except json.JSONDecodeError:
        return {}


def build_run_result(
    root: Path,
    item_path: Path,
    item: dict[str, Any],
    run_dir: Path,
    experiment: Path,
    completed: dict[str, Any],
) -> dict[str, Any]:
    measured = completed["measured"]
    result = {
        "run_id": item.get("run_id", run_dir.name),
        "family": item["family"],
        "stage": item.get("stage", "smoke"),
        "feature_lane": item.get("feature_lane", ""),
        "description": item.get("description", ""),
        "params_summary": item.get("params_summary", ""),
        "seed": item.get("seed", 42),
        "status": completed["status"],
        "returncode": completed["returncode"],
        "runtime_seconds": measured.get("runtime_seconds", completed["elapsed"]),
        "cv_mae": measured.get("cv_mae"),
        "cv_mae_std": measured.get("cv_mae_std"),
        "validation_mae": measured.get("validation_mae"),
        "work_item": relative_to_root(item_path, root),
        "experiment": relative_to_root(experiment, root),
        "stdout": relative_to_root(run_dir / "stdout.log", root),
        "stderr": relative_to_root(run_dir / "stderr.log", root),
    }
    for field in ("change_kind", "hypothesis_unit", "feature_group", "anchor_run_id"):
        if item.get(field):
            result[field] = item[field]
    return result
