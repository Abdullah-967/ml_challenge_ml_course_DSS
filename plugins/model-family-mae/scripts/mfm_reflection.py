"""Result reflection and state updates for model-family MAE runs."""

from __future__ import annotations

import shutil
from pathlib import Path
from typing import Any

from mfm_io import append_tsv, family_dir, load_tsv, read_json, rounded, write_json
from mfm_planning import stage_counts
from mfm_runner import resolve_path


def reflect_result(root: Path, result_json: str | Path, status: str | None = None) -> dict[str, Any]:
    result_path = resolve_path(root, result_json)
    result = read_json(result_path)
    fdir = family_dir(root, result["family"])
    reflected_status = status or default_result_status(result)
    append_result_once(fdir / "results.tsv", result, reflected_status)
    append_result_once(
        root / "experiments" / "results.tsv",
        result,
        reflected_status,
        key_fields=("model_family", "commit_or_run_id"),
    )
    append_reflection(fdir / "iteration_log.md", result, reflected_status)
    state = update_state(root, fdir, result, reflected_status)
    return {
        "reflected_run_id": result["run_id"],
        "family": result["family"],
        "status": reflected_status,
        "state": state,
    }


def default_result_status(result: dict[str, Any]) -> str:
    return "keep" if result.get("status") == "completed" else result.get("status", "failed")


def append_result_once(
    path: Path,
    result: dict[str, Any],
    status: str,
    key_fields: tuple[str, ...] = ("commit_or_run_id",),
) -> None:
    row = result_row(result, status)
    existing_keys = {row_key(existing, key_fields) for existing in load_tsv(path)}
    if row_key(row, key_fields) not in existing_keys:
        append_tsv(path, row)


def row_key(row: dict[str, Any], key_fields: tuple[str, ...]) -> tuple[str, ...]:
    return tuple(str(row.get(field, "")) for field in key_fields)


def result_row(result: dict[str, Any], status: str) -> dict[str, str]:
    return {
        "commit_or_run_id": result["run_id"],
        "stage": result.get("stage", ""),
        "model_family": result["family"],
        "feature_lane": result.get("feature_lane", ""),
        "cv_mae": rounded(result.get("cv_mae")),
        "cv_mae_std": rounded(result.get("cv_mae_std")),
        "validation_mae": rounded(result.get("validation_mae")),
        "runtime_seconds": rounded(result.get("runtime_seconds")),
        "status": status,
        "params_summary": result.get("params_summary", ""),
        "description": result.get("description", ""),
    }


def append_reflection(path: Path, result: dict[str, Any], status: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if not path.exists():
        path.write_text(f"# {result['family']} Iteration Log\n\n", encoding="utf-8")
    current = path.read_text(encoding="utf-8")
    if f"## {result['run_id']}" in current:
        return
    with path.open("a", encoding="utf-8") as handle:
        handle.write(reflection_block(result, status))


def reflection_block(result: dict[str, Any], status: str) -> str:
    return (
        f"\n## {result['run_id']}\n\n"
        f"- stage: {result.get('stage', '')}\n"
        f"- feature_lane: {result.get('feature_lane', '')}\n"
        f"- change_kind: {result.get('change_kind', 'n/a')}\n"
        f"- hypothesis_unit: {result.get('hypothesis_unit', 'n/a')}\n"
        f"- feature_group: {result.get('feature_group', 'n/a')}\n"
        f"- anchor_run_id: {result.get('anchor_run_id', 'n/a')}\n"
        f"- status: {status}\n"
        f"- cv_mae: {result.get('cv_mae', '')}\n"
        f"- cv_mae_std: {result.get('cv_mae_std', '')}\n"
        f"- runtime_seconds: {result.get('runtime_seconds', '')}\n"
        f"- change_from_previous: {result.get('params_summary', '')}\n"
        f"- hypothesis: {result.get('description', '')}\n"
        "- observation: pending: interpret fold/runtime signal before next action.\n"
        "- comparison: pending: compare against previous, family best, and global best.\n"
        "- significance: pending: apply pooled-std noise rule.\n"
        "- attribution: one-knob work item; verify no bundled changes before promotion.\n"
        "- next_hypothesis: pending: one-knob next action or gate decision.\n"
    )


def update_state(root: Path, fdir: Path, result: dict[str, Any], status: str) -> dict[str, Any]:
    state_path = fdir / "state.json"
    state = read_json(state_path) if state_path.exists() else {"family": result["family"]}
    rows = load_tsv(fdir / "results.tsv")
    state["latest_run_id"] = result["run_id"]
    state["stage_counts"] = stage_counts(rows)
    state["active_stage"] = result.get("stage", state.get("active_stage", "smoke"))
    update_best_run(root, fdir, state, rows, result, status)
    write_json(state_path, state)
    return state


def update_best_run(
    root: Path,
    fdir: Path,
    state: dict[str, Any],
    rows: list[dict[str, str]],
    result: dict[str, Any],
    status: str,
) -> None:
    best = best_row(rows)
    if best:
        state["best_run_id"] = best.get("commit_or_run_id")
    if status == "keep" and is_best_result(result, best):
        state["best_run_id"] = result["run_id"]
        copy_best_experiment(root, fdir, result)


def best_row(rows: list[dict[str, str]]) -> dict[str, str] | None:
    numeric_rows = []
    for row in rows:
        try:
            numeric_rows.append((float(row.get("cv_mae", "nan")), row))
        except ValueError:
            continue
    return min(numeric_rows, key=lambda item: item[0])[1] if numeric_rows else None


def is_best_result(result: dict[str, Any], best: dict[str, str] | None) -> bool:
    if result.get("cv_mae") is None:
        return False
    return best is None or float(result["cv_mae"]) <= float(best.get("cv_mae", "inf"))


def copy_best_experiment(root: Path, fdir: Path, result: dict[str, Any]) -> None:
    experiment_path = root / result.get("experiment", "")
    if experiment_path.exists():
        shutil.copyfile(experiment_path, fdir / "best_experiment.py")
