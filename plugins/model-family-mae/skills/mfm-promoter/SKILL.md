---
name: mfm-promoter
description: Use when a model-family MAE candidate has passed reflection gates and needs confirmation or a promotable-candidate report.
---

# MFM Promoter

Own final confirmation checks and promotable-candidate reporting. Promotion is intentionally narrow and gated.

## Promotion Gates

- Candidate has a reflected result in `results.tsv` and `iteration_log.md`.
- Candidate is named explicitly with `--run-id`; never infer it from `best_experiment.py`, `current_experiment.py`, or `experiment.py`.
- Stage minimums are satisfied.
- Any multi-change candidate has an ablation summary.
- Confirmation has at least two seeds.
- Candidate is a noise-aware win versus the global best, not merely within-noise.
- Test data is not used by plugin promotion; accepted-winner prediction artifacts are generated later from the notebook.

## CLI

```powershell
python "plugins/model-family-mae/scripts/mfm_cli.py" promote "<family>" --run-id "<confirmed_run_id>"
```

## Output

Return the candidate run id, confirmation evidence, experiment path, human-review next step, and any remaining blocker. Do not promote a tie or generate prediction artifacts before human acceptance.
