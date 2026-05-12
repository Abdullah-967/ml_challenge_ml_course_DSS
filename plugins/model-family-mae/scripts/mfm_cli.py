"""Command-line entrypoint for the model-family MAE plugin."""

from __future__ import annotations

import argparse

from mfm_io import project_root, write_json_or_print
from mfm_ops import analyze_features, execute_work_item, init_family, inventory_payload, plan_work_item, promote_family, reflect_result


def cmd_inventory(args: argparse.Namespace) -> int:
    write_json_or_print(inventory_payload(project_root(args.project_root)), args.output)
    return 0


def cmd_init(args: argparse.Namespace) -> int:
    print(init_family(project_root(args.project_root), args.family))
    return 0


def cmd_plan(args: argparse.Namespace) -> int:
    if not args.family:
        raise SystemExit("--family is required until automatic family selection is configured")
    payload = plan_work_item(
        project_root(args.project_root),
        family=args.family,
        feature_lane=args.feature_lane,
        change_kind=args.change_kind,
        hypothesis_unit=args.hypothesis_unit,
        feature_group=args.feature_group,
        anchor_run_id=args.anchor_run_id,
        description=args.description,
        params_summary=args.params_summary,
        seed=args.seed,
        write=args.write,
    )
    write_json_or_print(payload, args.output)
    return 0


def cmd_analyze(args: argparse.Namespace) -> int:
    payload = analyze_features(
        project_root(args.project_root),
        family=args.family,
        method=args.method,
        top_pairs=args.top_pairs,
        top_target=args.top_target,
        min_abs_corr=args.min_abs_corr,
        poly_base_feature_limit=args.poly_base_feature_limit,
        poly_min_features=args.poly_min_features,
        poly_degree=args.poly_degree,
        poly_interaction_only=args.poly_interaction_only,
    )
    write_json_or_print(payload, args.output)
    return 0


def cmd_run(args: argparse.Namespace) -> int:
    payload = execute_work_item(
        project_root(args.project_root),
        args.work_item,
        timeout_seconds=args.timeout_seconds,
        overwrite_experiment=args.overwrite_experiment,
    )
    write_json_or_print(payload, args.output)
    return 0 if payload["status"] == "completed" else 1


def cmd_reflect(args: argparse.Namespace) -> int:
    payload = reflect_result(project_root(args.project_root), args.result_json, status=args.status)
    write_json_or_print(payload, args.output)
    return 0


def cmd_promote(args: argparse.Namespace) -> int:
    payload = promote_family(project_root(args.project_root), args.family, run_id=args.run_id)
    write_json_or_print(payload, args.output)
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--project-root", default=".")
    parser.add_argument("--output")
    subcommands = parser.add_subparsers(dest="command", required=True)

    subcommands.add_parser("inventory").set_defaults(func=cmd_inventory)

    init = subcommands.add_parser("init")
    init.add_argument("family")
    init.set_defaults(func=cmd_init)

    plan = subcommands.add_parser("plan")
    plan.add_argument("--family")
    plan.add_argument("--feature-lane")
    plan.add_argument("--change-kind", help="feature, preprocessing, target, hyperparameter, capacity_pair, or diagnostic.")
    plan.add_argument("--hypothesis-unit", help="Attributable feature/preprocessing idea being tested.")
    plan.add_argument("--feature-group", help="Feature group from references/feature_search_space.md.")
    plan.add_argument("--anchor-run-id", help="Run id this candidate is based on.")
    plan.add_argument("--description")
    plan.add_argument("--params-summary")
    plan.add_argument("--seed", type=int, default=42)
    plan.add_argument("--write", action="store_true")
    plan.set_defaults(func=cmd_plan)

    analyze = subcommands.add_parser("analyze")
    analyze.add_argument("--family", help="Optional family context for more targeted suggestions.")
    analyze.add_argument("--method", default="hybrid", help="Advisory diagnostic method: corr-lite, poly-prune-lite, or hybrid. Default: hybrid.")
    analyze.add_argument("--top-pairs", type=int, default=12, help="Number of top correlated numeric feature pairs to report.")
    analyze.add_argument("--top-target", type=int, default=8, help="Number of top feature-target correlations to report.")
    analyze.add_argument("--min-abs-corr", type=float, default=0.85, help="Absolute correlation threshold for redundancy groups.")
    analyze.add_argument("--poly-base-feature-limit", type=int, default=6, help="Max numeric anchor features to seed polynomial pruning.")
    analyze.add_argument("--poly-min-features", type=int, default=3, help="Stop polynomial pruning when this many terms remain.")
    analyze.add_argument("--poly-degree", type=int, default=2, help="Polynomial degree for the bounded pruning diagnostic.")
    analyze.add_argument("--poly-interaction-only", action="store_true", help="Use interaction-only polynomial features in the bounded pruning diagnostic.")
    analyze.set_defaults(func=cmd_analyze)

    run = subcommands.add_parser("run")
    run.add_argument("work_item")
    run.add_argument("--timeout-seconds", type=int, default=600)
    run.add_argument(
        "--overwrite-experiment",
        action="store_true",
        help="Replace an existing runs/<run_id>/experiment.py before execution.",
    )
    run.set_defaults(func=cmd_run)

    reflect = subcommands.add_parser("reflect")
    reflect.add_argument("result_json")
    reflect.add_argument("--status")
    reflect.set_defaults(func=cmd_reflect)

    promote = subcommands.add_parser("promote")
    promote.add_argument("family")
    promote.add_argument("--run-id", required=True, help="Reflected confirmation run to promote.")
    promote.set_defaults(func=cmd_promote)
    return parser


def main() -> int:
    args = build_parser().parse_args()
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
