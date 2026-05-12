# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What this repo is

A Tilburg ML challenge: predict French property transaction values (`property_value`, in EUR) from cadastral / structural / geographic features. Decision metric is **5-fold CV MAE** (`KFold(n_splits=5, shuffle=True, random_state=42)`). The deliverable is a `predicted.json` (list of `{"property_value": float}`) and a matching `predicted.zip` whose archive entry **must** be named exactly `predicted.json`.

## Dataset rules (load-bearing)

- `dataset/train.json` — labelled records.
- `dataset/test.json` — **final predictions only.** Do not use it for feature selection, category coverage inspection, clipping bounds, hyperparameter tuning, or park/promote decisions. Trained pipelines may transform test records using preprocessing learned from full training data.
- `dataset/features.json` — column descriptions; consult before naming a feature group.
- All preprocessing must be **fold-safe**: imputers, encoders, target/group statistics, clipping bounds, and blend weights are fit on the fold's training split. See `plugins/model-family-mae/references/leakage_and_validation.md`.

## Repository architecture

Two layers operate side-by-side:

1. **Global champion layer (top level)**
   - `experiment.py` — current global champion's `fit_predict(train_records, test_records)`. Currently HGB on log1p target with structural ratios (iter22, cv_mae≈50,907 — see `results.tsv`).
   - `baseline/baseline.py` — starter Ridge baseline that writes `baseline/predicted.{json,zip}`.
   - `results.tsv` — append-only global scratch leaderboard. Columns: `commit | cv_mae | cv_mae_std | runtime_seconds | status | description`. One row per kept-or-discarded global iteration; `status` ∈ `{keep, discard, crash, park, confirm, promote}`.
   - `run.log` — last run's per-fold MAEs and aggregate stats.

2. **Model-family exploration layer (`experiments/<family>/`)**
   Each active family is an isolated workspace produced by the bundled `model-family-mae` plugin:
   ```
   experiments/<family>/
     state.json              # planner state
     experiment.py           # initializer seed copy
     current_experiment.py   # anchor source for new work items
     best_experiment.py      # best-known checkpoint (NOT a promotion target)
     results.tsv             # family run history
     iteration_log.md        # narrative reflection (append-only)
     notes.md                # human-readable status / decision / next action
     work_items/<run_id>.json
     runs/<run_id>/
       experiment.py         # frozen recipe for this run
       result.json
       stdout.log / stderr.log
   ```
   Every `experiment.py` must expose `fit_predict(train_records, validation_records)` returning a list/array of predictions for the validation records.

## Plugin: model-family-mae

`plugins/model-family-mae/` is the canonical workflow for systematic family search. It is registered locally via `.claude-plugin/marketplace.json` (re-add with `/plugin marketplace add .` from the repo root). Don't hand-roll family directories or alternate evaluators — drive everything through its CLI.

**Driver script (run from repo root, PowerShell):**
```powershell
python "plugins/model-family-mae/scripts/mfm_cli.py" inventory
python "plugins/model-family-mae/scripts/mfm_cli.py" init "<family>"
python "plugins/model-family-mae/scripts/mfm_cli.py" plan --family "<family>" --feature-lane "<lane>" --write
python "plugins/model-family-mae/scripts/mfm_cli.py" run    "experiments/<family>/work_items/<run_id>.json"
python "plugins/model-family-mae/scripts/mfm_cli.py" reflect "experiments/<family>/runs/<run_id>/result.json"
python "plugins/model-family-mae/scripts/mfm_cli.py" promote "<family>" --run-id "<confirmed_run_id>"
```

**Slash commands** (`/mfm-start`, `/mfm-plan`, `/mfm-run`, `/mfm-reflect`, `/mfm-promote`, `/mfm-status`) and **skills** (`mfm-orchestrator`, `mfm-planner`, `mfm-worker`, `mfm-reflector`, `mfm-promoter`) wrap that CLI. The compatibility skill `model-family-mae` exists only to route old prompts into `mfm-orchestrator`.

**Hook:** `plugins/model-family-mae/hooks/log_eval.ps1` is a PostToolUse audit hook that appends every `eval_family.py` / `mfm_cli.py run` invocation to `experiments/_mfm_hook.log`. It is non-blocking and audit-only — reflection still requires `mfm_cli.py reflect`.

## Search discipline (do not skip)

These rules sit in `plugins/model-family-mae/references/` and are enforced by the workflow. Read them before iterating.

- **One knob per iteration.** A feature unit, a single hyperparameter, a preprocessing change, or a target transform — never two unrelated ideas. Mechanically-paired knobs (e.g. `learning_rate` halved with `n_estimators` doubled) count as one; document the pairing in `change_from_previous`. Multi-knob runs require `multi_change: true` and trigger `ablation_protocol.md` before any promotion.
- **Reflection precedes the next decision.** After every canonical CV run, append a structured entry to `experiments/<family>/iteration_log.md` per `reflection_protocol.md` *before* the next run is planned. A run without a reflection entry is not a data point.
- **Significance is pooled-std-aware.** `pooled_std = sqrt((std_A² + std_B²)/2)`, `noise_band = 0.25 × pooled_std`. `improvement` requires `delta_mae <= -noise_band`; `regression` requires `>= +noise_band`; everything else is `tie_within_noise`. A within-noise tie is a tie — never a "contender" or "champion".
- **Stage budgets** (`search_policy.md`): smoke = exactly 3 lanes; deepen = 10–15 single-knob iterations; tune (or autoresearch) = 10–15; confirm = at least 2 seeds (canonical 42 + alternate, typically 2026).
- **Promotion gate.** Promote to global champion only if the candidate beats the global best by a **noise-aware** margin AND has been confirmed on a second shuffled-fold seed AND (if multi-knob) has a written `ablation_summary`. Otherwise park as runner-up; do not overwrite the global champion narrative.
- **Feature work** must name one `hypothesis_unit` from `references/feature_search_space.md` or documented dataset inspection (e.g. `area_density_ratios`, `room_layout_distribution`, `commune_frequency`). Vague labels like "deepen geo_signal" are not allowed.
- **Test-set rule** (above). The 5 CV folds are also overfittable — keep run counts budgeted and confirm finalists on `random_state=2026`.

## Runtime budget

Normal canonical eval target: **under 5 minutes**. Hard stop / park: **over 10 minutes** unless the user approves. If a candidate would blow the cap, shrink it (fewer trees, smaller depth) before running rather than skipping the canonical CV.

## Environment

- Python with `pandas`, `numpy`, `scikit-learn`, `matplotlib`, `xgboost` (see `requirements.txt`). HGB is the current champion class; XGBoost is installed for family search; LightGBM is **not** installed.
- Windows / PowerShell. Use PowerShell syntax (`$env:VAR`, backtick line continuation, `;` to chain). The bundled hook and CLI examples assume PowerShell quoting.
- Working tree path contains spaces (`OneDrive - Tilburg University`) — always quote paths.

## Notebooks

- `baseline/baseline.ipynb` — the official starter notebook (Ridge on three features).
- `notebooks/eda_pandas.ipynb`, `notebooks/eda_pyspark.ipynb`, `notebooks/eda.ipynb` — exploration only, not on the decision path.
- `experiments/<family>/<family>.ipynb` - only created after a human accepts a plugin promotion report. `mfm_cli.py promote` validates a reflected candidate and reports the candidate, experiment path, and CV evidence; it does not write prediction artifacts, replace the global champion, or register DagsHub/MLflow runs. For a human-accepted global winner, this notebook mirrors the accepted recipe and generates/logs CV metrics, model artifacts, prediction artifacts, and `family_status=global_champion` to DagsHub/MLflow for audit and monitoring.
- `practicals_notebooks/` — course materials, not part of the submission pipeline.
