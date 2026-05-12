"""Promotion reporting for model-family MAE runs."""

from __future__ import annotations

from pathlib import Path

from mfm_io import family_dir, load_tsv, read_json, relative_to_root


PROMOTABLE_ROW_STATUSES = {"confirm", "confirmed", "promote_candidate", "promoted"}
PROMOTABLE_STAGES = {"confirm", "promote"}


def promote_family(root: Path, family: str, run_id: str | None = None) -> dict[str, str]:
    if not run_id:
        raise SystemExit("Promotion requires an explicit candidate: use promote <family> --run-id <run_id>")
    fdir = family_dir(root, family)
    result_path = fdir / "runs" / run_id / "result.json"
    result = promotable_result(result_path, family)
    row = reflected_result_row(fdir, run_id)
    validate_promotion_row(row, run_id)
    experiment = resolve_experiment(root, result, run_id)
    return {
        "family": family,
        "run_id": run_id,
        "experiment": relative_to_root(experiment, root),
        "stage": row.get("stage", ""),
        "status": row.get("status", ""),
        "cv_mae": row.get("cv_mae", ""),
        "cv_mae_std": row.get("cv_mae_std", ""),
        "runtime_seconds": row.get("runtime_seconds", ""),
        "params_summary": row.get("params_summary", ""),
        "description": row.get("description", ""),
        "decision_required": "human_review",
        "next_step": (
            "Human must accept or park this promotable candidate. "
            "If accepted, generate prediction artifacts and DagsHub/MLflow "
            "tracking from the dedicated promotion notebook."
        ),
    }


def promotable_result(result_path: Path, family: str) -> dict[str, object]:
    if not result_path.exists():
        raise SystemExit(f"Promotion candidate result does not exist: {result_path}")
    result = read_json(result_path)
    if result.get("family") != family:
        raise SystemExit(f"Promotion candidate belongs to {result.get('family')}, not {family}")
    if result.get("status") != "completed":
        raise SystemExit(f"Promotion candidate {result.get('run_id')} is not completed: {result.get('status')}")
    return result


def reflected_result_row(fdir: Path, run_id: str) -> dict[str, str]:
    for row in load_tsv(fdir / "results.tsv"):
        if row.get("commit_or_run_id") == run_id:
            return row
    raise SystemExit(f"Promotion candidate {run_id} has not been reflected in {fdir / 'results.tsv'}")


def validate_promotion_row(row: dict[str, str], run_id: str) -> None:
    stage = row.get("stage", "")
    status = row.get("status", "")
    if stage not in PROMOTABLE_STAGES and status not in PROMOTABLE_ROW_STATUSES:
        raise SystemExit(
            f"Promotion candidate {run_id} is not a confirmed/promotable row "
            f"(stage={stage or 'n/a'}, status={status or 'n/a'})"
        )


def resolve_experiment(root: Path, result: dict[str, object], run_id: str) -> Path:
    experiment_value = result.get("experiment")
    if not experiment_value:
        raise SystemExit(f"Promotion candidate {run_id} does not record an experiment path")
    experiment = root / str(experiment_value)
    if not experiment.exists():
        raise SystemExit(f"Promotion candidate experiment does not exist: {experiment}")
    return experiment
