"""Family workspace initialization for the model-family MAE plugin."""

from __future__ import annotations

import shutil
from pathlib import Path

from mfm_io import RESULT_FIELDS, TEMPLATE_PATH, family_dir, timestamp, write_json


def ensure_family_workspace(root: Path, family: str, overwrite: bool = False) -> Path:
    fdir = family_dir(root, family)
    create_family_workspace(fdir, family, overwrite=overwrite)
    current = fdir / "current_experiment.py"
    if overwrite or not current.exists():
        shutil.copyfile(fdir / "experiment.py", current)
    (fdir / "work_items").mkdir(parents=True, exist_ok=True)
    (fdir / "runs").mkdir(parents=True, exist_ok=True)
    return fdir


def create_family_workspace(fdir: Path, family: str, overwrite: bool = False) -> None:
    fdir.mkdir(parents=True, exist_ok=True)
    experiment_path = fdir / "experiment.py"
    if overwrite or not experiment_path.exists():
        shutil.copyfile(TEMPLATE_PATH, experiment_path)
    write_if_missing(fdir / "results.tsv", "\t".join(RESULT_FIELDS) + "\n")
    write_if_missing(fdir / "notes.md", initial_notes(family))
    write_if_missing(fdir / "iteration_log.md", initial_iteration_log(family))


def write_if_missing(path: Path, content: str) -> None:
    if not path.exists():
        path.write_text(content, encoding="utf-8")


def initial_notes(family: str) -> str:
    return (
        f"# {family} Notes\n\n"
        "## Status\n\nInitialized.\n\n"
        "## Best Result\n\nNo canonical CV run yet.\n\n"
        "## Decision\n\nRun Stage 1 smoke tests before deepening or tuning.\n\n"
        "## Next Action\n\nCreate a work item with `mfm_cli.py plan --write`.\n"
    )


def initial_iteration_log(family: str) -> str:
    return (
        f"# {family} Iteration Log\n\n"
        "Append-only. One block per canonical CV run. See the bundled "
        "`plugins/model-family-mae/references/reflection_protocol.md`.\n\n"
        "Required metadata per entry: stage, change_kind, hypothesis_unit, "
        "feature_group, anchor_run_id, change_from_previous, hypothesis, "
        "observation, comparison, significance, attribution, next_hypothesis.\n"
    )


def init_family(root: Path, family: str, overwrite: bool = False) -> Path:
    fdir = ensure_family_workspace(root, family, overwrite=overwrite)
    state_path = fdir / "state.json"
    if not state_path.exists():
        write_json(
            state_path,
            {
                "family": family,
                "active_stage": "smoke",
                "created_at": timestamp(),
                "stage_counts": {},
                "latest_run_id": None,
                "best_run_id": None,
            },
        )
    return fdir
