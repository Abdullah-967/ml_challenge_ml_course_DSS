---
description: Create the next one-knob work item for a model family.
argument-hint: "<family> [planning flags]"
---

Use `mfm-planner`. Treat the first argument as the family name and pass any
planning flags explicitly:

```powershell
python "plugins/model-family-mae/scripts/mfm_cli.py" plan --family "<family>" --write
```

For feature/preprocessing deepen or autoresearch work, include `--change-kind`,
`--hypothesis-unit`, and `--feature-group` so the worker tests one attributable
hypothesis unit rather than a vague lane. Return the created `work_item.json`
path and explain the stage gate behind it. Do not execute the work item.
