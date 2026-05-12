---
description: Start or resume the model-family MAE workflow through the orchestrator and produce the next planned work item.
argument-hint: "[family]"
---

You are starting the **model-family-mae** workflow.

1. Use the `mfm-orchestrator` skill as the control plane.
2. Inventory current state:
   ```powershell
   python "plugins/model-family-mae/scripts/mfm_cli.py" inventory
   ```
3. If the user supplied a family, initialize or resume it:
   ```powershell
   python "plugins/model-family-mae/scripts/mfm_cli.py" init "<family>"
   python "plugins/model-family-mae/scripts/mfm_cli.py" plan --family "<family>" --write
   ```
4. If no family was supplied, report inventory and ask the planner to choose one active family.

Do not run an evaluator from this command. The next executable unit must be a `work_item.json` delegated to `mfm-worker`.
