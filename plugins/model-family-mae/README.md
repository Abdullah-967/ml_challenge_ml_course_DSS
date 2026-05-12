# model-family-mae plugin

A plugin for long-running `property_value` MAE exploration. It keeps model
family search split into a small control plane, isolated run workers, and
explicit reflection/promotion gates.

## Architecture

- `mfm-orchestrator`: session inventory, active-family coordination, and user-facing status.
- `mfm-planner`: stage gates and one-knob work-item creation.
- `mfm-analysis`: optional train-only feature diagnostics that suggest next hypothesis units.
- `mfm-worker`: exactly one isolated CV run.
- `mfm-reflector`: canonical family/global `results.tsv`, `iteration_log.md`, and `state.json` updates.
- `mfm-promoter`: confirmation checks and promotable-candidate reports.

`model-family-mae` remains as a compatibility wrapper for older prompts and
routes to the focused skills.

## Install Surface

The plugin manifest lives at:

```text
plugins/model-family-mae/.codex-plugin/plugin.json
plugins/model-family-mae/.claude-plugin/plugin.json
```

If this repository uses a local marketplace file, register the plugin there and
reload plugin discovery:

```text
.agents/plugins/marketplace.json
.claude/plugins/marketplace.json
```

## Main Workflow

Run commands from the repository root:

```powershell
python "plugins/model-family-mae/scripts/mfm_cli.py" inventory
python "plugins/model-family-mae/scripts/mfm_cli.py" init "xgboost"
python "plugins/model-family-mae/scripts/mfm_cli.py" analyze --family "xgboost"
python "plugins/model-family-mae/scripts/mfm_cli.py" analyze --family "ridge" --method "poly-prune-lite"
python "plugins/model-family-mae/scripts/mfm_cli.py" plan --family "xgboost" --write
python "plugins/model-family-mae/scripts/mfm_cli.py" run "experiments/xgboost/work_items/<item>.json"
python "plugins/model-family-mae/scripts/mfm_cli.py" reflect "experiments/xgboost/runs/<run_id>/result.json"
python "plugins/model-family-mae/scripts/mfm_cli.py" promote "xgboost" --run-id "<confirmed_run_id>"
```

Workers do not edit `current_experiment.py` or `best_experiment.py`. A work item
may prepare an isolated run copy, and `mfm_cli.py run` preserves that copy unless
`--overwrite-experiment` is set intentionally.

```text
experiments/
  results.tsv                # reflected runs across all families

experiments/<family>/
  state.json
  experiment.py              # initializer seed copy for compatibility
  current_experiment.py      # family anchor source for new work items
  best_experiment.py         # best-known checkpoint, not a promotion target
  results.tsv
  iteration_log.md
  work_items/
    <run_id>.json
  runs/
    <run_id>/
      experiment.py
      result.json
      stdout.log
      stderr.log
```

Promotion is explicit: `mfm-promoter` must name a reflected confirmation run
with `--run-id`. It never infers the candidate from `best_experiment.py`.

## Post-Experiment Review and Tracking

After a run has been reflected, a human reviews the plugin evidence before any
global winner is recorded. The review compares the candidate against the current
global champion using the pooled-std-aware noise band, requires second-seed
confirmation for promotion, and parks within-noise ties as runner-up evidence.

`mfm_cli.py promote` is the plugin's promotion report step. It requires an
explicit reflected `--run-id`, validates that the row is confirm/promotable, and
returns the candidate run, experiment path, CV evidence, and next human-review
step. It does not write prediction artifacts, replace the top-level global
champion, or register a DagsHub/MLflow run.

The human reviews that promotion report and either accepts the candidate as the
new global winner or ignores/parks it as runner-up evidence. If accepted, record
the winner in a dedicated notebook at `experiments/<family>/<family>.ipynb`.
That notebook is a DagsHub/MLflow tracking artifact: it mirrors the accepted
recipe, reruns the documented validation, logs parameters and CV metrics,
generates prediction artifacts, and logs model and prediction artifacts.

Git remains the source of truth for promoted code and repository artifacts.
DagsHub/MLflow is the monitoring and reproducibility layer for the
human-accepted winner; it does not replace reflection or the human review gate.

## Stable Assets

The top-level CLI is the preferred workflow surface. These lower-level assets
remain available for compatibility and direct inspection:

```text
scripts/init_family.py
scripts/eval_family.py
templates/
references/
```

Feature/preprocessing work items can include `change_kind`, `hypothesis_unit`,
`feature_group`, and `anchor_run_id`; see
`references/feature_search_space.md`.

`mfm_cli.py analyze` is intentionally outside the decision path. It reads
`dataset/train.json` only, reports numeric correlation clusters, and, in hybrid
or `poly-prune-lite` mode, can run a bounded train-only polynomial pruning pass
that replaces holdout MSE with CV MAE. It never edits experiments, writes
reflection, or replaces canonical CV evidence.

## Hook

`hooks/log_eval.ps1` records evaluator and `mfm_cli.py run` invocations to:

```text
experiments/_mfm_hook.log
```

The hook is audit-only. Reflection and state changes still require
`mfm_cli.py reflect`.
