# Experiment Layout

Use this reference when creating or resuming `experiments/<model_family>/`, logging family results, or turning a human-accepted winner into notebook/artifact form.

## Table Of Contents

- [Directory Shape](#directory-shape)
- [End-To-End Commands](#end-to-end-commands)
- [Canonical Evaluation](#canonical-evaluation)
- [Per-Family Results](#per-family-results)
- [Notes File](#notes-file)
- [Accepted-Winner Notebook](#accepted-winner-notebook)
- [Prediction Artifacts](#prediction-artifacts)
- [Naming](#naming)
- [Consistency Checks](#consistency-checks)

## Directory Shape

Each active family owns one directory:

```text
experiments/
  results.tsv                  # reflected runs across all families

experiments/<model_family>/
  state.json
  experiment.py               # initializer seed copy for compatibility
  current_experiment.py       # source copied into new run directories
  best_experiment.py          # best-known checkpoint, not a promotion target
  results.tsv
  notes.md
  iteration_log.md
  work_items/
    <run_id>.json
  runs/
    <run_id>/
      experiment.py
      result.json
      stdout.log
      stderr.log
  <model_family>.ipynb          # only after human acceptance
  predicted.json                # only after accepted-winner notebook run
  predicted.zip                 # only after accepted-winner notebook run
```

Every runnable experiment file must expose the `fit_predict(train_records, validation_records)` interface expected by bundled `scripts/eval_family.py` and accepted-winner notebooks.

Do not scatter temporary family experiments across root files. Root `experiment.py` may remain the global champion context, but model-family exploration belongs under `experiments/<model_family>/`.

## End-To-End Commands

Initialize a family:

```powershell
python "plugins/model-family-mae/scripts/mfm_cli.py" init "<model_family>"
```

Create the next isolated work item:

```powershell
python "plugins/model-family-mae/scripts/mfm_cli.py" plan --family "<model_family>" --feature-lane "<feature_lane>" --write
```

Run and reflect it:

```powershell
python "plugins/model-family-mae/scripts/mfm_cli.py" run "experiments/<model_family>/work_items/<run_id>.json"
python "plugins/model-family-mae/scripts/mfm_cli.py" reflect "experiments/<model_family>/runs/<run_id>/result.json"
```

Confirm a finalist with a second seed:

```powershell
python "plugins/model-family-mae/scripts/mfm_cli.py" plan --family "<model_family>" --feature-lane "<feature_lane>" --params-summary "<candidate summary>" --seed 2026 --write
python "plugins/model-family-mae/scripts/mfm_cli.py" run "experiments/<model_family>/work_items/<confirm_run_id>.json"
python "plugins/model-family-mae/scripts/mfm_cli.py" reflect "experiments/<model_family>/runs/<confirm_run_id>/result.json" --status confirm
```

Report a promotable candidate for human review:

```powershell
python "plugins/model-family-mae/scripts/mfm_cli.py" promote "<model_family>" --run-id "<confirmed_run_id>"
```

## Canonical Evaluation

Use the bundled evaluator as the canonical harness:

```powershell
python "plugins/model-family-mae/scripts/mfm_cli.py" run "experiments/<model_family>/work_items/<run_id>.json"
```

`mfm_cli.py run` calls `scripts/eval_family.py`, writes run logs, and stores
`runs/<run_id>/result.json`. Do not create alternate evaluators for individual
families. If a wrapper script is useful, it should call `scripts/eval_family.py`
without redefining CV logic.

The evaluator decision metric is `cv_mae`. Notebook holdout metrics are supporting context only.

## Per-Family Results

`mfm_cli.py init` creates `experiments/<model_family>/results.tsv` if it does
not exist, with this header:

```text
commit_or_run_id	stage	model_family	feature_lane	cv_mae	cv_mae_std	validation_mae	runtime_seconds	status	params_summary	description
```

Rules:

- append rows; do not overwrite history;
- keep `params_summary` short, such as `n_estimators=200,max_depth=18,min_leaf=2`;
- use `status` values such as `keep`, `discard`, `crash`, `park`, `confirm`, `promote`;
- include enough in `description` to explain the single idea tested.

`mfm_cli.py reflect` also appends the same canonical row to
`experiments/results.tsv`. This experiment-level table is an append-only mirror
of reflected family runs and is keyed by `(model_family, commit_or_run_id)` so
rerunning reflection stays idempotent while preserving same-named runs across
families.

Root `results.tsv` remains the global scratch leaderboard. Add a root row only
after confirmation and promotion gates are satisfied.

## Notes File

Use `notes.md` for human-readable decisions:

```markdown
# <model_family> Notes

## Status

Active, parked, tuning, or promoted.

## Best Result

CV MAE, CV std, feature lane, params, and run id.

## Decision

Why the family was selected, deepened, parked, or promoted.

## Next Action

One scoped next step.
```

Keep notes concise. The results table is the source of run history.

## Accepted-Winner Notebook

When a plugin promotion report is accepted by a human, create or update:

```text
experiments/<model_family>/<model_family>.ipynb
```

Use this standalone model-family notebook pattern:

1. Markdown title: model family, feature scope, why it is worth preserving.
2. Setup: imports, root discovery, constants, DagsHub/MLflow setup.
3. Feature/model helpers: feature lists, frame builders, target builder, `build_model()`, optional `cross_validate_mae()`.
4. Train/evaluate/predict: holdout split, CV metrics, full-data fit, artifact writing.
5. Summary dictionary: experiment name, metrics, features, artifact paths.

Log to DagsHub MLflow when possible:

- params: model type, feature lane, feature names/counts, encoding, key hyperparameters;
- metrics: `validation_mae`, `validation_rmse`, `validation_r2`, `cv_mae`, `cv_mae_std`, prediction count;
- artifacts: sklearn-compatible model/pipeline if possible, `predicted.json`, `predicted.zip`.

## Prediction Artifacts

Only human-accepted winners should write prediction artifacts. The accepted
winner notebook writes:

```text
experiments/<model_family>/predicted.json
experiments/<model_family>/predicted.zip
```

The zip entry must be named exactly `predicted.json`.

Predictions must be a list of objects:

```python
[
    {"property_value": float(value)}
    for value in model.predict(make_feature_frame(test_records))
]
```

## Naming

- directory: snake_case model family, e.g. `xgboost`, `linear_robust`, `tree_bagging`;
- notebook: same as directory, e.g. `xgboost.ipynb`;
- MLflow experiment: kebab-case, e.g. `xgboost`;
- run name: include family and stage, e.g. `xgboost-smoke-all-numeric`.

## Consistency Checks

Before reporting an accepted winner notebook:

- `EXPERIMENT_NAME`, directory name, notebook name, and artifact paths match;
- `feature_lane` in `results.tsv` matches the actual feature builder;
- logged params match `build_model()`;
- `cv_mae` came from canonical 5-fold CV;
- test records were used only for final predictions.
