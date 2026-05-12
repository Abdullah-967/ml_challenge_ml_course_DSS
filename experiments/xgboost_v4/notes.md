# xgboost_v4 Notes

## Status

**Promoted.** Stages: smoke=3, deepen=40, ablate=1, confirm=1.

## Family premise

Beat xgboost_v2's promoted recipe (49154 seed=42, 49200 2-seed mean) using
additional signal sources: geographic hierarchy (dept/region cats), feature
engineering (built_per_land, built_rel_type via fold-safe group statistics),
per-property-type sub-model architecture, and capacity scaling (n_estimators).

## Best Result (promoted)

- recipe: W''''' (deepen iter37 winner: per-type sub-model architecture + n_est=4000)
- seed=42 cv_mae: **47107.53 ± 5244.67** (deepen iter37 `20260507-235645`)
- seed=2026 cv_mae: **47998.49 ± 3831.88** (confirm `20260508-003012`)
- 2-seed mean: **47553.01** (seed agreement: |Δ|=891, within pooled noise threshold ~1135)
- runtime: ~7 min per CV
- feature_lane: `v2_plus_geo_hierarchy`
- recipe (best_experiment.py reflects this exactly):
  - features: v2's full 33-feature set + dept_code (cat) + region_code (cat) + built_per_land (numeric) + built_rel_type (numeric, fold-safe group stat)
  - target: log1p with expm1 inverse
  - architecture: 0.7 * global_xgb + 0.3 * per-type sub-model for top 5 property types (UNE MAISON, UN APPARTEMENT, TERRAIN DE TYPE TERRE ET PRE, TERRAIN DE TYPE TAB, ACTIVITE)
  - hyperparameters: `XGBRegressor(reg:absoluteerror, n_est=4000, lr=0.05, max_depth=6, mcw=5, subsample=0.8, colsample_bytree=0.6, reg_lambda=1.0, hist, enable_categorical=True)`

## Decision

**Promoted.** Vs xgboost_v2 promoted (49200, 2-seed mean): **−1647 — REAL noise-aware win**
(>1188 threshold). 2-seed agreement |Δ|=891 confirms reproducibility.

Eleven kept knobs accumulated:
1. Lane A: dept_code + region_code as native cats (smoke −42 vs v2)
2. iter3: built_per_land = built_area/land_area (−116)
3. iter5: built_rel_type = built_area / mean(built_area | property_type) fold-safe (−245)
4. iter22: 2 per-type sub-models with 0.5 blend (−153)
5. iter23: extended to 5 sub-types (−57)
6. iter25: blend 0.3 sub / 0.7 global (−5)
7. iter33: n_est=1000 (−482)
8. iter34: n_est=1500 (−284)
9. iter35: n_est=2000 (−235)
10. iter36: n_est=3000 (−126)
11. iter37: n_est=4000 (−301)

Net: 49154 (v2 W' anchor) → 47108 (W''''' seed=42) = **−2046 single-seed lift**.

vs HGB iter21 (50934.78): −3382 — strong gap.
vs tree_bagging_rf confirm (50753.32): −3200 — strong gap.
vs xgboost_v2 promoted (49200 2-seed): **−1647 — new global best**.

xgboost_v4 is the new best-performing family across all explored families.

## Artifacts

- `experiments/xgboost_v4/predicted.json` (6843 predictions, sample[0]=47519)
- `experiments/xgboost_v4/predicted.zip`
- `experiments/xgboost_v4/best_experiment.py`

## Stage Summary

### Stage 1 smoke (3 lanes)

| lane | cv_mae | verdict |
|---|---:|---|
| **v2_plus_geo_hierarchy** | **49111.53 ± 4975** | best (geo hierarchy lane wins) |
| v2_plus_temporal_cats | 49343.36 ± 4922 | tied (temporal redundant w/ date_ordinal) |
| v2_plus_fold_te | 49505.39 ± 4922 | worst (commune-level TE too noisy) |

### Stage 2 deepen (40 single-knob iters; 11 kept, 29 reverted)

Highlights of kept knobs (cumulative -2046 vs v2 W'):
- iter3 built_per_land (-116): explicit ratio trees can't easily compute
- iter5 built_rel_type (-245): fold-safe group-stat ratio (size relative to type norm)
- iter22-25 per-type sub-model architecture (-215 cumulative): structural specialization
- iter33-37 n_est ramp 500→4000 (-1428 cumulative): the dominant late-stage win

Notable reverts: log1p (redundant with v2), monotone constraints (+2249, hurts), commune-level TE (too noisy), 2D type-x-dept TE, 5-bag bootstrap (overfit small samples), Ridge residual stacking (catastrophic +40k), early stopping (eval-set reduces effective training data).

### Stage 3b ablate (1 LOO run)

| knob | revert | result | Δ vs W''''' | verdict |
|---|---|---:|---:|---|
| a1 | drop per-type sub-models | 47392.22 | +284 | tie (NOT load-bearing alone, but consistent contribution kept) |

Sub-models contribute tie-positive lift (+284, within ~1180 noise) but were retained because they accumulated consistently across iter22/23/25.
Other knobs implicitly ablated during exploration: iter10 (drop dept/region cats: +431, kept), iter20 (drop cadastral_first: +1846, kept), iter31 (drop room_layout: +409, kept).

### Stage 4 confirm (1 run, seed=2026)

- W''''' confirm seed=2026: 47998.49 ± 3831.88 (vs seed=42 47107.53, |Δ|=891, seeds agree)

## What surprised xgboost_v4

- **n_estimators ramp gave the largest lift** by far (-1428 from iter33-37). With v4's expanded feature set (built_rel_type, built_per_land, dept/region cats), the model was previously underfit at v2's n_est=500. More trees extracted real signal.
- **Per-type sub-models worked despite smaller per-type training data**. The 0.3/0.7 blend ratio was optimal — pure sub-model (BLEND=0.7) hurt; pure global hurt slightly. The arithmetic mean of two reasonable estimators was the right move.
- **Commune-level TE (Lane C) failed** even with smoothing=30 — 36k commune levels have too noisy means. **Property-type-level relative-stat (built_rel_type)** worked because property_type has only ~10 levels.
- **Most v2 hyperparam reverts ported** (max_depth=8 still hurts, lr=0.03 still hurts) but the specific exception was n_estimators — v2 plateaued at 500 with 4-feature lane, but v4's richer feature mix benefits from 4000 trees.
- **Ridge residual stacking failed catastrophically** (88k MAE) — Ridge interpreted residuals as signal and amplified noise. Not all stacks help.
- **Heterogeneous 5-model ensemble underperformed** the single recipe — diversity from depth/lr changes hurt more than averaging helped because most recipes were sub-optimal individually.
