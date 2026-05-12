from __future__ import annotations

import sys
import shutil
import unittest
from unittest.mock import patch
from time import time_ns
from pathlib import Path


PLUGIN_ROOT = Path(__file__).resolve().parents[1]
TEST_TMP_ROOT = PLUGIN_ROOT / ".test-tmp"
sys.path.insert(0, str(PLUGIN_ROOT / "scripts"))

from mfm_io import load_tsv, read_json, write_json  # noqa: E402
from mfm_ops import analyze_features, init_family, inventory_payload, plan_work_item, prepare_run, promote_family, reflect_result  # noqa: E402
from mfm_runner import build_run_result  # noqa: E402


class ModelFamilyWorkflowTests(unittest.TestCase):
    def setUp(self) -> None:
        TEST_TMP_ROOT.mkdir(exist_ok=True)
        self._projects: list[Path] = []

    def tearDown(self) -> None:
        for project in self._projects:
            shutil.rmtree(project, ignore_errors=True)

    def temp_project(self) -> Path:
        project = TEST_TMP_ROOT / f"{self._testMethodName}-{time_ns()}"
        project.mkdir(parents=True)
        self._projects.append(project)
        return project

    def test_plan_writes_one_knob_work_item(self) -> None:
        root = self.temp_project()
        init_family(root, "xgboost")

        work_item = plan_work_item(root, "xgboost", feature_lane="geo_signal", write=True)

        work_path = root / work_item["work_item_path"]
        self.assertTrue(work_path.exists())
        self.assertEqual(work_item["stage"], "smoke")
        self.assertEqual(work_item["feature_lane"], "geo_signal")
        self.assertEqual(work_item["experiment_source"], str(Path("experiments") / "xgboost" / "current_experiment.py"))

        inventory = inventory_payload(root)
        self.assertEqual(inventory["families"][0]["pending_work_items"], [work_item["work_item_path"]])

    def test_plan_uses_family_smoke_lanes(self) -> None:
        root = self.temp_project()
        init_family(root, "xgboost")
        results_path = root / "experiments" / "xgboost" / "results.tsv"
        results_path.write_text(
            "commit_or_run_id\tstage\tmodel_family\tfeature_lane\tcv_mae\tcv_mae_std\tvalidation_mae\t"
            "runtime_seconds\tstatus\tparams_summary\tdescription\n"
            "run-1\tsmoke\txgboost\tall_numeric\t10.0\t0.1\t\t1.0\tkeep\tbaseline\tbaseline\n",
            encoding="utf-8",
        )

        work_item = plan_work_item(root, "xgboost")

        self.assertEqual(work_item["stage"], "smoke")
        self.assertEqual(work_item["feature_lane"], "numeric_plus_basic_cats")

    def test_plan_writes_hypothesis_unit_metadata(self) -> None:
        root = self.temp_project()
        init_family(root, "xgboost")

        work_item = plan_work_item(
            root,
            "xgboost",
            feature_lane="geo_signal",
            change_kind="feature",
            hypothesis_unit="commune_first_category",
            feature_group="geography",
            anchor_run_id="smoke-geo",
            write=True,
        )

        stored = read_json(root / work_item["work_item_path"])
        self.assertEqual(stored["change_kind"], "feature")
        self.assertEqual(stored["hypothesis_unit"], "commune_first_category")
        self.assertEqual(stored["feature_group"], "geography")
        self.assertEqual(stored["anchor_run_id"], "smoke-geo")

    def test_reflect_result_updates_state_once(self) -> None:
        root = self.temp_project()
        init_family(root, "linear")
        run_dir = root / "experiments" / "linear" / "runs" / "run-1"
        run_dir.mkdir(parents=True)
        (run_dir / "experiment.py").write_text("# candidate\n", encoding="utf-8")
        result_path = run_dir / "result.json"
        write_json(
            result_path,
            {
                "run_id": "run-1",
                "family": "linear",
                "stage": "smoke",
                "feature_lane": "all_numeric",
                "description": "baseline smoke",
                "params_summary": "single_knob=all_numeric",
                "status": "completed",
                "runtime_seconds": 1.25,
                "cv_mae": 10.0,
                "cv_mae_std": 0.5,
                "experiment": "experiments/linear/runs/run-1/experiment.py",
            },
        )

        first = reflect_result(root, result_path)
        second = reflect_result(root, result_path)

        self.assertEqual(first["state"]["best_run_id"], "run-1")
        self.assertEqual(second["state"]["stage_counts"], {"smoke": 1})
        self.assertEqual(len(load_tsv(root / "experiments" / "linear" / "results.tsv")), 1)
        global_rows = load_tsv(root / "experiments" / "results.tsv")
        self.assertEqual(len(global_rows), 1)
        self.assertEqual(global_rows[0]["model_family"], "linear")
        self.assertEqual(global_rows[0]["commit_or_run_id"], "run-1")
        log_text = (root / "experiments" / "linear" / "iteration_log.md").read_text(encoding="utf-8")
        self.assertEqual(log_text.count("## run-1"), 1)
        self.assertEqual((root / "experiments" / "linear" / "best_experiment.py").read_text(), "# candidate\n")

    def test_global_results_allows_same_run_id_across_families(self) -> None:
        root = self.temp_project()
        for family in ("linear", "ridge"):
            init_family(root, family)
            run_dir = root / "experiments" / family / "runs" / "shared-run"
            run_dir.mkdir(parents=True)
            (run_dir / "experiment.py").write_text(f"# {family} candidate\n", encoding="utf-8")
            write_json(
                run_dir / "result.json",
                {
                    "run_id": "shared-run",
                    "family": family,
                    "stage": "smoke",
                    "feature_lane": "all_numeric",
                    "description": f"{family} baseline smoke",
                    "params_summary": "single_knob=all_numeric",
                    "status": "completed",
                    "runtime_seconds": 1.25,
                    "cv_mae": 10.0,
                    "cv_mae_std": 0.5,
                    "experiment": str(Path("experiments") / family / "runs" / "shared-run" / "experiment.py"),
                },
            )

        reflect_result(root, root / "experiments" / "linear" / "runs" / "shared-run" / "result.json")
        reflect_result(root, root / "experiments" / "ridge" / "runs" / "shared-run" / "result.json")
        reflect_result(root, root / "experiments" / "ridge" / "runs" / "shared-run" / "result.json")

        global_rows = load_tsv(root / "experiments" / "results.tsv")
        self.assertEqual(len(global_rows), 2)
        self.assertEqual(
            {(row["model_family"], row["commit_or_run_id"]) for row in global_rows},
            {("linear", "shared-run"), ("ridge", "shared-run")},
        )

    def test_prepare_run_preserves_existing_run_copy(self) -> None:
        root = self.temp_project()
        init_family(root, "ridge")
        item = {
            "family": "ridge",
            "stage": "smoke",
            "run_id": "run-2",
            "experiment_source": "experiments/ridge/current_experiment.py",
        }
        run_dir = root / "experiments" / "ridge" / "runs" / "run-2"
        run_dir.mkdir(parents=True)
        prepared = run_dir / "experiment.py"
        prepared.write_text("# isolated edit\n", encoding="utf-8")

        _, experiment = prepare_run(root, item, overwrite=False)

        self.assertEqual(experiment.read_text(encoding="utf-8"), "# isolated edit\n")

    def test_run_result_preserves_hypothesis_unit_metadata(self) -> None:
        root = self.temp_project()
        init_family(root, "ridge")
        run_dir = root / "experiments" / "ridge" / "runs" / "run-3"
        run_dir.mkdir(parents=True)
        experiment = run_dir / "experiment.py"
        experiment.write_text("# candidate\n", encoding="utf-8")
        item = {
            "family": "ridge",
            "stage": "deepen",
            "feature_lane": "all_numeric",
            "description": "test room layout",
            "params_summary": "single_knob=room_layout_distribution",
            "run_id": "run-3",
            "change_kind": "feature",
            "hypothesis_unit": "room_layout_distribution",
            "feature_group": "room_layout",
            "anchor_run_id": "run-2",
        }

        result = build_run_result(
            root,
            root / "experiments" / "ridge" / "work_items" / "run-3.json",
            item,
            run_dir,
            experiment,
            {
                "status": "completed",
                "returncode": 0,
                "elapsed": 0.1,
                "measured": {"cv_mae": 10.0, "cv_mae_std": 0.5, "runtime_seconds": 0.1},
            },
        )

        self.assertEqual(result["hypothesis_unit"], "room_layout_distribution")
        self.assertEqual(result["feature_group"], "room_layout")
        self.assertEqual(result["anchor_run_id"], "run-2")

    def test_reflect_result_logs_hypothesis_unit_metadata(self) -> None:
        root = self.temp_project()
        init_family(root, "linear")
        run_dir = root / "experiments" / "linear" / "runs" / "run-meta"
        run_dir.mkdir(parents=True)
        (run_dir / "experiment.py").write_text("# candidate\n", encoding="utf-8")
        result_path = run_dir / "result.json"
        write_json(
            result_path,
            {
                "run_id": "run-meta",
                "family": "linear",
                "stage": "deepen",
                "feature_lane": "all_numeric",
                "change_kind": "feature",
                "hypothesis_unit": "area_density_ratios",
                "feature_group": "derived_ratios",
                "anchor_run_id": "run-anchor",
                "description": "area density ratios",
                "params_summary": "single_knob=area_density_ratios",
                "status": "completed",
                "runtime_seconds": 1.25,
                "cv_mae": 10.0,
                "cv_mae_std": 0.5,
                "experiment": "experiments/linear/runs/run-meta/experiment.py",
            },
        )

        reflect_result(root, result_path)

        log_text = (root / "experiments" / "linear" / "iteration_log.md").read_text(encoding="utf-8")
        self.assertIn("- change_kind: feature", log_text)
        self.assertIn("- hypothesis_unit: area_density_ratios", log_text)
        self.assertIn("- feature_group: derived_ratios", log_text)
        self.assertIn("- anchor_run_id: run-anchor", log_text)

    def test_analyze_features_reports_numeric_redundancy(self) -> None:
        root = self.temp_project()
        dataset_dir = root / "dataset"
        dataset_dir.mkdir(parents=True)
        write_json(
            dataset_dir / "train.json",
            [
                {
                    "property_value": 100000.0,
                    "built_area": 50.0,
                    "num_lots": 1,
                    "num_apartments": 1,
                    "apartment_area": 50.0,
                    "num_apt_1_room": 1,
                    "area_apt_1_room": 50.0,
                    "num_apt_2_rooms": 0,
                    "area_apt_2_rooms": 0.0,
                    "future_sale": False,
                    "property_type": "Appartement",
                },
                {
                    "property_value": 200000.0,
                    "built_area": 80.0,
                    "num_lots": 1,
                    "num_apartments": 2,
                    "apartment_area": 80.0,
                    "num_apt_1_room": 1,
                    "area_apt_1_room": 40.0,
                    "num_apt_2_rooms": 1,
                    "area_apt_2_rooms": 40.0,
                    "future_sale": False,
                    "property_type": "Appartement",
                },
                {
                    "property_value": 300000.0,
                    "built_area": 110.0,
                    "num_lots": 2,
                    "num_apartments": 3,
                    "apartment_area": 110.0,
                    "num_apt_1_room": 1,
                    "area_apt_1_room": 30.0,
                    "num_apt_2_rooms": 2,
                    "area_apt_2_rooms": 80.0,
                    "future_sale": False,
                    "property_type": "Appartement",
                },
                {
                    "property_value": 400000.0,
                    "built_area": 150.0,
                    "num_lots": 2,
                    "num_apartments": 4,
                    "apartment_area": 150.0,
                    "num_apt_1_room": 1,
                    "area_apt_1_room": 30.0,
                    "num_apt_2_rooms": 3,
                    "area_apt_2_rooms": 120.0,
                    "future_sale": True,
                    "property_type": "Appartement",
                },
            ],
        )

        payload = analyze_features(root, family="ridge", method="corr-lite", top_pairs=10, top_target=3, min_abs_corr=0.8)

        self.assertTrue(payload["diagnostic_only"])
        self.assertEqual(payload["method"], "corr-lite")
        self.assertEqual(payload["rows_used"], 4)
        self.assertEqual(payload["skipped_rows"], 0)
        self.assertTrue(
            any(
                {row["left"], row["right"]} == {"num_apartments", "apartment_area"}
                and row["abs_correlation"] >= 0.99
                for row in payload["high_correlation_pairs"]
            )
        )
        self.assertEqual(payload["suggested_work_items"][0]["hypothesis_unit"], "room_layout_distribution")
        self.assertIn("drop_sparse_room_layout", {row["hypothesis_unit"] for row in payload["suggested_work_items"]})

    def test_analyze_features_poly_prune_reports_dependency_gap_cleanly(self) -> None:
        root = self.temp_project()
        dataset_dir = root / "dataset"
        dataset_dir.mkdir(parents=True)
        write_json(
            dataset_dir / "train.json",
            [
                {"property_value": 10.0, "built_area": 1.0, "num_lots": 1, "num_premises": 1, "future_sale": False},
                {"property_value": 20.0, "built_area": 2.0, "num_lots": 1, "num_premises": 2, "future_sale": False},
                {"property_value": 30.0, "built_area": 3.0, "num_lots": 2, "num_premises": 2, "future_sale": True},
                {"property_value": 40.0, "built_area": 4.0, "num_lots": 2, "num_premises": 3, "future_sale": True},
            ],
        )

        real_import = __import__

        def block_sklearn_import(name, *args, **kwargs):
            if name.startswith("sklearn"):
                raise ModuleNotFoundError("No module named 'sklearn'", name="sklearn")
            return real_import(name, *args, **kwargs)

        with patch("builtins.__import__", side_effect=block_sklearn_import):
            payload = analyze_features(root, family="ridge", method="poly-prune-lite")

        self.assertEqual(payload["method"], "poly-prune-lite")
        self.assertEqual(payload["poly_prune_lite"]["status"], "unavailable")
        self.assertIn("Optional dependency unavailable", payload["poly_prune_lite"]["reason"])
        self.assertTrue(payload["suggested_work_items"])


    def test_promote_requires_explicit_run_id(self) -> None:
        root = self.temp_project()
        init_family(root, "linear")

        with self.assertRaises(SystemExit) as raised:
            promote_family(root, "linear")

        self.assertIn("--run-id", str(raised.exception))

    def test_promote_reports_explicit_run_without_generating_artifacts(self) -> None:
        root = self.temp_project()
        init_family(root, "linear")
        fdir = root / "experiments" / "linear"
        run_dir = fdir / "runs" / "run-promote"
        run_dir.mkdir(parents=True)
        experiment = run_dir / "experiment.py"
        experiment.write_text("# selected candidate\n", encoding="utf-8")
        (fdir / "best_experiment.py").write_text("# stale checkpoint\n", encoding="utf-8")
        result_path = run_dir / "result.json"
        write_json(
            result_path,
            {
                "run_id": "run-promote",
                "family": "linear",
                "stage": "confirm",
                "feature_lane": "all_numeric",
                "description": "confirmed candidate",
                "params_summary": "single_knob=confirm_candidate",
                "status": "completed",
                "runtime_seconds": 1.25,
                "cv_mae": 9.5,
                "cv_mae_std": 0.4,
                "experiment": str(Path("experiments") / "linear" / "runs" / "run-promote" / "experiment.py"),
            },
        )
        reflect_result(root, result_path, status="confirm")

        payload = promote_family(root, "linear", run_id="run-promote")

        self.assertEqual(payload["run_id"], "run-promote")
        self.assertEqual(payload["experiment"], str(Path("experiments") / "linear" / "runs" / "run-promote" / "experiment.py"))
        self.assertEqual(payload["decision_required"], "human_review")
        self.assertNotIn("prediction_json", payload)
        self.assertNotIn("prediction_zip", payload)
        self.assertFalse((fdir / "predicted.json").exists())
        self.assertFalse((fdir / "predicted.zip").exists())


if __name__ == "__main__":
    unittest.main()
