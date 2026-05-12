---
name: model-family-mae
description: Compatibility entrypoint for the model-family MAE plugin. Use when older prompts call the original model-family-mae skill; immediately route orchestration to mfm-orchestrator and load focused skills for planning, worker execution, reflection, or promotion.
---

# model-family-mae

This is a compatibility wrapper for the original monolithic skill. The plugin is now split into focused skills:

- `mfm-orchestrator`: session control, state inspection, delegation, and user-facing status.
- `mfm-planner`: active-family selection, stage gates, and work-item creation.
- `mfm-worker`: one isolated CV run under `experiments/<family>/runs/<run_id>/`.
- `mfm-reflector`: append results, write `iteration_log.md`, update `state.json`, and apply noise-aware decisions.
- `mfm-promoter`: confirmation and promotable-candidate reports.

When this skill is invoked, switch to `mfm-orchestrator` first. Load the other focused skills only for the specific task at hand.

## Stable Assets

The reference library and compatibility scripts remain available at plugin root:

- `templates/experiment_template.py`
- `scripts/init_family.py`
- `scripts/eval_family.py`
- `references/search_policy.md`
- `references/reflection_protocol.md`
- `references/ablation_protocol.md`
- `references/autoresearch_loop.md`
- `references/model_families.md`
- `references/feature_lanes.md`
- `references/feature_search_space.md`
- `references/experiment_layout.md`
- `references/leakage_and_validation.md`
- `references/practicals_notebooks.md`

The top-level plugin CLI is now the preferred script surface:

```powershell
python "plugins/model-family-mae/scripts/mfm_cli.py" inventory
python "plugins/model-family-mae/scripts/mfm_cli.py" plan --family "<family>" --write
python "plugins/model-family-mae/scripts/mfm_cli.py" run "experiments/<family>/work_items/<item>.json"
python "plugins/model-family-mae/scripts/mfm_cli.py" reflect "experiments/<family>/runs/<run_id>/result.json"
python "plugins/model-family-mae/scripts/mfm_cli.py" promote "<family>" --run-id "<confirmed_run_id>"
```
