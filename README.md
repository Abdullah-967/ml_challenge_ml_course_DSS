# ML Challenge Workflow

This repository predicts French property transaction values (`property_value`,
EUR) for the Tilburg ML challenge. The decision metric is 5-fold CV MAE with
`KFold(n_splits=5, shuffle=True, random_state=42)`.

The final submission artifact is `predicted.zip` containing exactly one archive
entry named `predicted.json`.

## Source of Truth

- `AGENTS.md` and `CLAUDE.md` define the operating rules for coding agents.
- `plugins/model-family-mae/README.md` documents the local MFM plugin and CLI.
- This README summarizes the human-facing workflow and avoids duplicating every
  command or stage rule.

## Repository Layers

- Global champion layer: top-level `experiment.py`, `results.tsv`, `run.log`,
  and final `predicted.{json,zip}` artifacts.
- Model-family exploration layer: `experiments/<family>/` workspaces created and
  maintained by the `model-family-mae` plugin.
- Notebook tracking layer: post-acceptance notebooks under
  `experiments/<family>/<family>.ipynb` for DagsHub/MLflow audit and monitoring.

## Experiment Loop

Use the `model-family-mae` plugin from the repository root. The canonical flow
is:

```text
inventory -> init -> plan -> run -> reflect -> promote
```

Reflection is mandatory before a run is used as evidence. It records the run in
the family/global result logs and updates the family state. A run without
reflection is not a decision point.

In the plugin, `promote` means candidate validation and reporting. It validates
an explicit reflected run and reports the candidate, experiment path, CV
evidence, and next human-review step. It does not write prediction artifacts,
replace the top-level global champion, or register anything in DagsHub/MLflow.

## Human Review and Winner Registration

After a reflected experiment finishes, a human reviews the evidence before the
repository records a global winner.

Review inputs:

- `experiments/<family>/runs/<run_id>/result.json`
- `experiments/<family>/results.tsv`
- `experiments/<family>/iteration_log.md`
- `experiments/results.tsv`
- the current top-level champion in `experiment.py` and `results.tsv`

Promotion rules stay aligned with `AGENTS.md` and `CLAUDE.md`: promote only when
the candidate beats the current global best by a pooled-std-aware, noise-aware
margin, has second-seed confirmation, and has the required ablation summary for
any multi-knob run. Within-noise ties are parked as runner-up evidence.

When the plugin reports a promotable candidate, the human decision is:

1. Accept it as the new global winner and promote the repo-level artifacts.
2. Ignore or park it as runner-up evidence.

When the human accepts a promotion, turn the accepted candidate into a dedicated
notebook. That notebook generates the accepted winner's prediction artifacts,
registers the run in DagsHub/MLflow, and leaves the promoted code/artifacts under
Git.

## DagsHub and MLflow

The DagsHub/MLflow notebook records the human-accepted winner after the review
decision. It is an audit and monitoring artifact, not the mechanism that chooses
the champion and not something the plugin writes automatically.

The notebook should mirror the accepted recipe and log:

- model parameters and feature groups;
- fold MAEs, `cv_mae`, and `cv_mae_std`;
- `family_status=global_champion`;
- final model artifacts;
- `predicted.json` and `predicted.zip`.

Git is the source of truth for code and promoted repository artifacts.
DagsHub/MLflow stores run metadata, metrics, models, and prediction artifacts.
Pushing code to Git does not register an MLflow run; the dedicated notebook must
execute successfully.

## Load-Bearing Rules

- `dataset/train.json` is the labelled training set.
- `dataset/test.json` is for final predictions only. Do not inspect it for
  feature selection, category coverage, clipping bounds, tuning, or promotion
  decisions.
- `dataset/features.json` is the feature-description source before naming
  feature groups.
- All preprocessing must be fold-safe inside each CV fold.
- Notebooks are not on the decision path except for post-acceptance tracking of
  a human-accepted winner.
