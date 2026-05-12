"""Inventory and work-item planning for model-family MAE runs."""

from __future__ import annotations

from collections import Counter
from pathlib import Path
from typing import Any

from mfm_io import DEFAULT_SMOKE_LANES, SMOKE_LANES_BY_FAMILY, load_tsv, relative_to_root, timestamp, write_json
from mfm_workspace import ensure_family_workspace


def inventory_payload(root: Path) -> dict[str, Any]:
    experiments = root / "experiments"
    families = []
    if experiments.exists():
        families = [family_inventory(root, item) for item in sorted(experiments.iterdir()) if is_family_dir(item)]
    return {
        "project_root": str(root),
        "root_results_exists": (root / "results.tsv").exists(),
        "families": families,
    }


def is_family_dir(path: Path) -> bool:
    return path.is_dir() and not path.name.startswith("_")


def family_inventory(root: Path, fdir: Path) -> dict[str, Any]:
    rows = load_tsv(fdir / "results.tsv")
    return {
        "family": fdir.name,
        "has_state": (fdir / "state.json").exists(),
        "has_current_experiment": (fdir / "current_experiment.py").exists(),
        "has_best_experiment": (fdir / "best_experiment.py").exists(),
        "result_count": len(rows),
        "stage_counts": stage_counts(rows),
        "latest_result": rows[-1] if rows else None,
        "pending_work_items": pending_work_items(root, fdir),
    }


def pending_work_items(root: Path, fdir: Path) -> list[str]:
    work_dir = fdir / "work_items"
    if not work_dir.exists():
        return []
    return [relative_to_root(path, root) for path in sorted(work_dir.glob("*.json"))]


def stage_counts(rows: list[dict[str, str]]) -> dict[str, int]:
    return dict(Counter(row.get("stage", "") for row in rows if row.get("stage")))


def plan_work_item(
    root: Path,
    family: str,
    feature_lane: str | None = None,
    change_kind: str | None = None,
    hypothesis_unit: str | None = None,
    feature_group: str | None = None,
    anchor_run_id: str | None = None,
    description: str | None = None,
    params_summary: str | None = None,
    seed: int = 42,
    write: bool = False,
) -> dict[str, Any]:
    fdir = ensure_family_workspace(root, family)
    rows = load_tsv(fdir / "results.tsv")
    stage = next_stage(rows, family)
    lane = feature_lane or next_smoke_lane(rows, family)
    run_id = f"{timestamp()}-{stage}-{lane}".replace("/", "-")
    work_item = build_work_item(
        fdir,
        root,
        family,
        stage,
        lane,
        run_id,
        description,
        params_summary,
        seed,
        change_kind=change_kind,
        hypothesis_unit=hypothesis_unit,
        feature_group=feature_group,
        anchor_run_id=anchor_run_id,
    )
    if write:
        path = fdir / "work_items" / f"{run_id}.json"
        write_json(path, work_item)
        work_item["work_item_path"] = relative_to_root(path, root)
    return work_item


def build_work_item(
    fdir: Path,
    root: Path,
    family: str,
    stage: str,
    lane: str,
    run_id: str,
    description: str | None,
    params_summary: str | None,
    seed: int,
    change_kind: str | None = None,
    hypothesis_unit: str | None = None,
    feature_group: str | None = None,
    anchor_run_id: str | None = None,
) -> dict[str, Any]:
    work_item = {
        "family": family,
        "stage": stage,
        "feature_lane": lane,
        "description": description or f"{stage} test for {family} using {lane}",
        "params_summary": params_summary or f"single_knob={lane}",
        "seed": seed,
        "run_id": run_id,
        "experiment_source": relative_to_root(fdir / "current_experiment.py", root),
        "created_at": timestamp(),
    }
    optional_fields = {
        "change_kind": change_kind,
        "hypothesis_unit": hypothesis_unit,
        "feature_group": feature_group,
        "anchor_run_id": anchor_run_id,
    }
    work_item.update({key: value for key, value in optional_fields.items() if value})
    return work_item


def smoke_lanes_for_family(family: str) -> list[str]:
    return SMOKE_LANES_BY_FAMILY.get(family, DEFAULT_SMOKE_LANES)


def next_stage(rows: list[dict[str, str]], family: str) -> str:
    counts = Counter(row.get("stage", "") for row in rows if row.get("stage"))
    return "smoke" if counts.get("smoke", 0) < len(smoke_lanes_for_family(family)) else "deepen"


def next_smoke_lane(rows: list[dict[str, str]], family: str) -> str:
    smoke_lanes = smoke_lanes_for_family(family)
    completed = {row.get("feature_lane", "") for row in rows if row.get("stage") == "smoke"}
    for lane in smoke_lanes:
        if lane not in completed:
            return lane
    return smoke_lanes[0]
