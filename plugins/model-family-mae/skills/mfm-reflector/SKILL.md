---
name: mfm-reflector
description: Use when a model-family MAE worker run has produced result.json and the workflow needs canonical results, reflection, state updates, and gate decisions.
---

# MFM Reflector

Own the audit and decision record after a worker has produced `result.json`. No run is complete until this step succeeds.

## Responsibilities

- Validate that `result.json` has family, stage, feature lane, run id, CV MAE, CV std, runtime, and description.
- Append the canonical row to `experiments/<family>/results.tsv`.
- Append the same canonical row to `experiments/results.tsv`.
- Append a structured block to `experiments/<family>/iteration_log.md`.
- Update `experiments/<family>/state.json` with the latest run, stage counts, and best-known run.
- Apply the pooled-std noise rule before using words like win, tie, contender, or champion.
- For feature/preprocessing runs, verify that `hypothesis_unit`,
  `feature_group`, and `params_summary` describe the same attributable idea. If
  they disagree, record the mismatch and keep promotion blocked until clarified.

## CLI

```powershell
python "plugins/model-family-mae/scripts/mfm_cli.py" reflect "experiments/<family>/runs/<run_id>/result.json"
```

## Output

Return the reflected run id, comparison against previous/family/global best if available, gate status, and the next action. If the stage minimum is unmet, the next action must stay in the same stage.
