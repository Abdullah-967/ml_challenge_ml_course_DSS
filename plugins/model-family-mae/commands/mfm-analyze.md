---
description: Run a train-only advisory feature diagnostic and suggest next hypothesis units.
argument-hint: "[family] [analysis flags]"
---

Use the plugin's diagnostic surface when you want a train-only feature
assessment without changing the stage workflow:

```powershell
python "plugins/model-family-mae/scripts/mfm_cli.py" analyze --family "<family>"
python "plugins/model-family-mae/scripts/mfm_cli.py" analyze --family "ridge" --method "poly-prune-lite"
```

This command is advisory only. It reads `dataset/train.json`, reports numeric
redundancy patterns, and can optionally run a bounded polynomial-pruning
diagnostic that scores subsets with train-only CV MAE rather than holdout MSE.
Do not treat it as a promotion gate or a substitute for canonical CV.
