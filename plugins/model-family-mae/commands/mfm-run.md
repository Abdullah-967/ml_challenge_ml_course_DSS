---
description: Run exactly one model-family MAE work item in an isolated run directory.
argument-hint: "<path to work_item.json>"
---

Use `mfm-worker` and run:

```powershell
python "plugins/model-family-mae/scripts/mfm_cli.py" run "$ARGUMENTS"
```

Return only the generated `result.json` path and measured metrics. Do not reflect or promote in this command.
