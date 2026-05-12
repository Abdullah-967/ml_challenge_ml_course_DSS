---
name: mfm-planner
description: Use when selecting the active model family, applying stage gates, or creating one-knob work items for the model-family MAE workflow.
---

# MFM Planner

Own stage policy and work-item creation. Do not run evaluations and do not write reflections.

## Inputs

- Root leaderboard: `results.tsv`
- Experiment-wide reflected history: `experiments/results.tsv`
- Family directories: `experiments/<family>/`
- Family state: `experiments/<family>/state.json`
- Family history: `experiments/<family>/results.tsv`
- User hint: optional family or stage preference

## Planning Contract

- Choose one active family per session.
- Stage 1 smoke requires exactly three fair feature lanes unless a lane is incompatible or too slow, and the reason is documented.
- Stage 2 deepen requires at least ten single-knob feature/preprocessing iterations.
- Stage 3 tune/autoresearch requires at least ten single-knob iterations.
- Stage 3b ablate is mandatory before promotion when the candidate is multi-change.
- Stage 4 confirm requires at least two seeds before promotion.
- Never convert a within-noise tie into a contender.
- For feature/preprocessing work, name exactly one `hypothesis_unit`. Use
  `references/feature_search_space.md` so broad lanes do not hide the actual
  feature idea.

## Work Item Shape

Create JSON work items under `experiments/<family>/work_items/`:

```json
{
  "family": "xgboost",
  "stage": "smoke",
  "feature_lane": "geo_signal",
  "change_kind": "feature",
  "hypothesis_unit": "commune_first_category",
  "feature_group": "geography",
  "description": "Smoke-test geo-derived features with the current family recipe.",
  "params_summary": "single_knob=geo_signal",
  "seed": 42,
  "experiment_source": "experiments/xgboost/current_experiment.py"
}
```

Prefer the CLI for consistent paths:

```powershell
python "plugins/model-family-mae/scripts/mfm_cli.py" plan --family "xgboost" --feature-lane "geo_signal" --change-kind "feature" --hypothesis-unit "commune_first_category" --feature-group "geography" --write
```

## Output

Return the chosen family, current stage, why the stage gate is or is not satisfied, the exact work item path, and why that work item is the next best one-knob task.
