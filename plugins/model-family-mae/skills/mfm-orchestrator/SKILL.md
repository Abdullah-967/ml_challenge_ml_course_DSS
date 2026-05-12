---
name: mfm-orchestrator
description: Use when the user wants to start, resume, inspect, or coordinate the model-family MAE workflow across planning, worker execution, reflection, and promotion.
---

# MFM Orchestrator

This is the control-plane entrypoint for the model-family MAE plugin. Keep it small: coordinate the workflow, delegate specialized tasks, and report state. Do not perform model edits, CV runs, reflection scoring, or promotion directly when a focused skill can own that task.

## Responsibilities

- Inventory root `results.tsv`, `experiments/results.tsv`, `experiments/*/state.json`, family `results.tsv`, and pending `work_items/*.json`.
- Pick exactly one active family for the session, using `mfm-planner` for stage rules and queue construction.
- Create work items through the top-level CLI instead of handwritten ad hoc commands.
- For feature/preprocessing work, require the planner to name one
  `hypothesis_unit` from `references/feature_search_space.md` or documented
  dataset inspection.
- Delegate isolated execution to `mfm-worker`, one work item per worker.
- Require `mfm-reflector` after every run before making the next decision.
- Delegate final confirmation checks and promotion reports to `mfm-promoter`.

## Command Surface

Use the plugin-root CLI from the repository root:

```powershell
python "plugins/model-family-mae/scripts/mfm_cli.py" inventory
python "plugins/model-family-mae/scripts/mfm_cli.py" plan --family "<family>" --write
python "plugins/model-family-mae/scripts/mfm_cli.py" init "<family>"
```

## Collaboration Rules

- Parent/orchestrator owns state transitions and user-facing decisions.
- Planner owns stage gates and work item shape.
- Worker owns one isolated run directory under `experiments/<family>/runs/<run_id>/`.
- Reflector owns `iteration_log.md`, family/global `results.tsv`, and `state.json` updates after a run.
- Promoter owns confirmation checks and promotable-candidate reports.

## Response Shape

Report the active family, stage, completed iteration counts, pending work items, latest CV MAE/std/runtime if available, blocked gates, and the next one-knob action. Keep long policy details deferred to the focused skills and references.
