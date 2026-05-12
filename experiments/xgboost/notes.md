# xgboost Notes

## Status

**Promoted.** Stages: smoke=3, deepen=10, tune=10, ablate=4, confirm=1.

## Best Result (promoted)

- recipe: simplified Stage 3 winner
- seed=42 cv_mae: **49685.50** ± 4670.67 (tune iter3 = same recipe)
- seed=2026 cv_mae: **49827.48** ± 4929.99 (confirm run `20260506-233001`)
- 2-seed mean: **49756.49** (seed agreement: |Δ|=142, well within pooled noise)
- runtime: ~40-45s per CV
- feature_lane: `geo_signal`
- recipe (current_experiment.py reflects this exactly):
  - features: all numeric/bool (excl `parcel_ids`, `transferred_parcel_ids`) + ratios{built_per_premise, land_per_lot, commercial_share, apt_share, houses_per_premise} + date_ordinal
  - native cats: commune_first, cadastral_first, property_type
  - model: `XGBRegressor(reg:absoluteerror, n_est=500, lr=0.05, **max_depth=6**, min_child_weight=5, subsample=0.8, colsample_bytree=0.8, reg_lambda=1.0, tree_method=hist, enable_categorical=True)`

## Decision

Promoted simplified recipe (B + max_depth=6 only) over the multi-change tune iter9 winner. Ablation showed only `max_depth=6` was load-bearing; subsample/colsample/reg_lambda tweaks were within-noise tweaks that don't survive ablation. Per protocol, simplest recipe within W's noise band is preferred.

vs HGB iter21 (50934.78): -1249 at seed=42 (real win, threshold ~1183), -1107 at seed=2026 (just within noise threshold ~1216), -1178 at 2-seed mean (real win above threshold ~1200).

## Artifacts

- `experiments/xgboost/predicted.json` (6843 predictions)
- `experiments/xgboost/predicted.zip`

## Stage Summary Tables

### Stage 1 smoke (3 lanes)
| lane | cv_mae | verdict |
|---|---:|---|
| all_numeric | 53600.06 | first xgboost run |
| numeric_plus_basic_cats | 52771.66 | tied lane1 |
| **geo_signal** | **51530.01** | best lane (real win vs lane1) |

### Stage 2 deepen (10 single-knob iters; 3 kept)
- Kept: derived_ratios (iter2, marginal), date_ordinal (iter5, marginal), property_type cat (iter10, real lift -429)
- Reverted: log1p target, presence flags, log skewed numerics, room aggregates, avg area per unit, commune target enc, drop sparse per-room cols
- Net: 51530.01 → 50957.36

### Stage 3 tune (10 single-knob iters; 4 kept)
- Kept: max_depth=5 (iter2), max_depth=6 (iter3, biggest lift), subsample=0.9 (iter7), colsample=0.7 (iter8), reg_lambda=2.0 (iter9)
- Reverted: lr=0.025 + n_est=1000, min_child_weight=3, min_child_weight=10, subsample=0.7, reg_lambda=4.0
- Net: 50957.36 → 49546.40

### Stage 3b ablate (4 LOO runs)
- max_depth=6: load-bearing (drop +1393)
- subsample=0.9: redundant (drop +281, tie)
- colsample=0.7: redundant (drop +130, tie)
- reg_lambda=2.0: redundant (drop +86, tie)

### Stage 4 confirm (1 run, seed=2026)
- Promoted recipe: 49827.48 (vs seed=42 same recipe 49685.50, |Δ|=142, seeds agree)

## What surprised xgboost
- log1p target hurt (HGB liked it)
- presence flags / aggregates / avg area / target encoding all redundant — XGBoost finds these splits internally
- depth was the dominant tuning axis (4 → 6 = -1272); other tuning knobs were within-noise
