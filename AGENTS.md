# AGENTS.md

This file provides Codex instructions for this repository.

## Project

This is a Tilburg ML challenge for predicting French property transaction
values (`property_value`, EUR) from cadastral, structural, and geographic
features. The decision metric is 5-fold CV MAE with:

```python
KFold(n_splits=5, shuffle=True, random_state=42)
```

The deliverable is `predicted.json`, a list of objects shaped like
`{"property_value": float}`, and `predicted.zip` with exactly one archive entry
named `predicted.json`.

## Dataset Rules

- `dataset/train.json` contains labelled training records.
- `dataset/test.json` is for final predictions only. Do not inspect it for
  feature selection, category coverage, clipping bounds, tuning, or promotion
  decisions.
- `dataset/features.json` contains feature descriptions. Consult it before
  naming feature groups.
- All preprocessing must be fold-safe. Fit imputers, encoders, target/group
  statistics, clipping bounds, and blend weights on each fold's training split.
  See `plugins/model-family-mae/references/leakage_and_validation.md`.

## Repository Layers

Top-level global champion layer:

- `experiment.py`: current global champion's
  `fit_predict(train_records, test_records)`.
- `baseline/baseline.py`: starter Ridge baseline.
- `results.tsv`: append-only global leaderboard with columns
  `commit | cv_mae | cv_mae_std | runtime_seconds | status | description`.
- `run.log`: last run's per-fold MAEs and aggregate stats.

Model-family exploration layer:

```text
experiments/<family>/
  state.json
  experiment.py
  current_experiment.py
  best_experiment.py
  results.tsv
  iteration_log.md
  notes.md
  work_items/<run_id>.json
  runs/<run_id>/
    experiment.py
    result.json
    stdout.log
    stderr.log
```

Every experiment module must expose:

```python
fit_predict(train_records, validation_records)
```

and return predictions for `validation_records`.

## Codex Plugin

The canonical workflow is the local Codex plugin at:

```text
plugins/model-family-mae/
```

It is registered through:

```text
.agents/plugins/marketplace.json
```

Use this plugin and its CLI for systematic family search. Do not hand-roll
family directories or alternate evaluators.

Run plugin commands from the repository root:

```powershell
python "plugins/model-family-mae/scripts/mfm_cli.py" inventory
python "plugins/model-family-mae/scripts/mfm_cli.py" init "<family>"
python "plugins/model-family-mae/scripts/mfm_cli.py" plan --family "<family>" --feature-lane "<lane>" --write
python "plugins/model-family-mae/scripts/mfm_cli.py" run "experiments/<family>/work_items/<run_id>.json"
python "plugins/model-family-mae/scripts/mfm_cli.py" reflect "experiments/<family>/runs/<run_id>/result.json"
python "plugins/model-family-mae/scripts/mfm_cli.py" promote "<family>" --run-id "<confirmed_run_id>"
```

Plugin skills:

- `mfm-orchestrator`: inventory, family coordination, and status.
- `mfm-planner`: stage gates and one-knob work-item creation.
- `mfm-worker`: exactly one isolated CV run.
- `mfm-reflector`: updates `results.tsv`, `iteration_log.md`, and `state.json`.
- `mfm-promoter`: confirmation checks and promotable-candidate reports.
- `model-family-mae`: compatibility wrapper for older prompts.

The plugin hook at `plugins/model-family-mae/hooks/log_eval.ps1` is audit-only.
Reflection still requires `mfm_cli.py reflect`.

## Search Discipline

- One knob per iteration. Multi-knob runs require `multi_change: true` and the
  ablation protocol before promotion.
- Reflection precedes the next decision. A run without a reflection entry is not
  a decision point.
- Use pooled-std-aware significance from the plugin references. Within-noise
  ties are ties, not contenders.
- Stage budgets: smoke = exactly 3 lanes; deepen = 10-15 single-knob
  iterations; tune/autoresearch = 10-15; confirm = at least two seeds
  (`42` plus alternate, typically `2026`).
- Promote only if a candidate beats the global best by a noise-aware margin,
  has second-seed confirmation, and has an ablation summary when multi-knob.
- Feature work must name a concrete `hypothesis_unit` from
  `references/feature_search_space.md` or documented train-only inspection.
- Keep CV run counts budgeted. Confirm finalists with `random_state=2026`.

## Runtime

Canonical eval target: under 5 minutes. Park or ask before running candidates
expected to exceed 10 minutes.

## Environment

- Windows / PowerShell. Quote paths because the project path contains spaces.
- Use PowerShell syntax for examples and environment variables.
- Dependencies are in `requirements.txt`. LightGBM is not installed.

## Notebooks

Notebooks are not on the decision path except where explicitly created after a
human accepts a plugin promotion report. `mfm_cli.py promote` validates a
reflected candidate and reports it to the human; it does not write prediction
artifacts, replace the global champion, or register DagsHub/MLflow runs. A
human-accepted global winner should have a dedicated
`experiments/<family>/<family>.ipynb` notebook that mirrors the accepted recipe
and generates/logs CV metrics, model artifacts, prediction artifacts, and
`family_status=global_champion` to DagsHub/MLflow. Treat
`practicals_notebooks/` as course material, not submission pipeline code.
