---
description: Report a promotable model-family candidate for human review.
argument-hint: "<family> --run-id <confirmed_run_id>"
---

Use `mfm-promoter`. Verify promotion gates first, then run:

```powershell
python "plugins/model-family-mae/scripts/mfm_cli.py" promote "$ARGUMENTS"
```

Return the candidate run, experiment path, CV evidence, and any remaining caveats.
Do not generate prediction artifacts before human acceptance. Do not promote a
within-noise tie. Do not rely on `best_experiment.py` as an implicit candidate;
the run id must identify the reflected confirmation run.
