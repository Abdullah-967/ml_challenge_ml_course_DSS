"""Initialize a standalone model-family experiment workspace."""

from __future__ import annotations

import argparse
from pathlib import Path

from mfm_ops import init_family


def parse_args():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("model_family", help="Snake-case family name, e.g. xgboost")
    parser.add_argument("--project-root", default=".", help="Repository root")
    parser.add_argument("--overwrite", action="store_true", help="Overwrite existing experiment.py and current_experiment.py")
    return parser.parse_args()


def main():
    args = parse_args()
    project_root = Path(args.project_root).resolve()
    family_dir = init_family(project_root, args.model_family, overwrite=args.overwrite)

    print(f"family_dir: {family_dir}")
    print(f"experiment: {family_dir / 'experiment.py'}")
    print(f"current_experiment: {family_dir / 'current_experiment.py'}")
    print(f"results: {family_dir / 'results.tsv'}")
    print(f"state: {family_dir / 'state.json'}")
    print(f"notes: {family_dir / 'notes.md'}")
    print(f"iteration_log: {family_dir / 'iteration_log.md'}")
    print(f"work_items: {family_dir / 'work_items'}")
    print(f"runs: {family_dir / 'runs'}")


if __name__ == "__main__":
    main()
