---
name: mfm-worker
description: Use when executing exactly one isolated model-family MAE work item and returning a structured result without making workflow decisions.
---

# MFM Worker

Own one run only. The worker plane must be safe to parallelize.

## Hard Rules

- Execute exactly one `work_item.json`.
- Do not choose stages, promote recipes, or write `iteration_log.md`.
- Do not edit `experiments/<family>/current_experiment.py` or `best_experiment.py`.
- Work only inside `experiments/<family>/runs/<run_id>/` plus the input work item.
- If a required one-knob edit is ambiguous, stop and ask the orchestrator to clarify the work item.

## Procedure

1. Read the work item.
2. If the work item includes `hypothesis_unit`, confirm the isolated edit can
   implement that unit as one attributable feature/preprocessing idea. If it is
   ambiguous or bundles unrelated ideas, stop and ask the planner to clarify.
3. If the work item requires an edit, create `runs/<run_id>/experiment.py` from `experiment_source` and edit that isolated run copy only.
4. If the work item requires no edit, let the CLI copy `experiment_source`.
5. Run:

```powershell
python "plugins/model-family-mae/scripts/mfm_cli.py" run "experiments/<family>/work_items/<item>.json"
```

The CLI preserves an existing `runs/<run_id>/experiment.py`. Use `--overwrite-experiment` only when intentionally discarding a prepared run copy.

6. Return the generated `result.json` path and the measured metrics.

## Final Report

```text
worker_result:
  result_json: experiments/<family>/runs/<run_id>/result.json
  model_family: <family>
  feature_lane: <lane>
  stage: <stage>
  run_id: <run_id>
  cv_mae: <value>
  cv_mae_std: <value>
  runtime_seconds: <value>
  status: completed | failed | timeout
```
