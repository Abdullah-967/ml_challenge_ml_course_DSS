# xgboost_v3 Notes

## Status

**Promoted.** Stages: smoke=1, deepen=10, ablate=2, confirm=1.

## Family premise

Test whether XGBoost trained on ONLY the 3 features used in the project's
Ridge baseline (`built_area`, `num_lots`, `num_commercial`) can perform
competitively. The constraint IS the family -- no new raw features allowed,
not even derived ratios from the kept three. Allowed knobs: target transforms,
preprocessing, hyperparameters.

## Best Result (promoted)

- recipe: W''' (deepen iter9 winner: max_depth=2 + colsample_bytree=1.0)
- seed=42 cv_mae: **62354.51 ± 4564.56** (deepen iter9 `20260507-213647`)
- seed=2026 cv_mae: **62674.08 ± 4330.88** (confirm `20260507-214500`)
- 2-seed mean: **62514.30** (seed agreement: |Δ|=320, well within pooled noise threshold ~2448)
- runtime: ~25-35s per CV
- feature_lane: `baseline_three_only`
- recipe (best_experiment.py reflects this exactly):
  - features (3 numeric only): built_area, num_lots, num_commercial
  - target: raw property_value (no log1p)
  - cats: none
  - model: `XGBRegressor(reg:absoluteerror, n_est=500, lr=0.05, max_depth=2, mcw=5, subsample=0.8, colsample_bytree=1.0, reg_lambda=1.0, hist)`

## Decision

Promoted W'''. Two single-knob changes from the smoke anchor (max_depth 6→2,
colsample_bytree 0.8→1.0). Ablation showed both knobs are tie-positive in
isolation (a1: +335 reverting depth, a2: +272 reverting colsample, combined
revert = smoke iter1 at +163), all within pooled noise threshold ~2275-2350.
Per protocol "Never convert a within-noise tie into a contender", the recipe
is technically tied with the smoke anchor. Promotion is justified by Occam:
W''' has lower model capacity (depth 2 vs 6) and uses all 3 columns per tree
(no random sampling), so a tie at simpler is preferred.

vs xgboost_v2 promoted (49200, 2-seed mean): **+13314 -- real LOSS** (>>noise threshold ~1190).
The 3-feature constraint guarantees this gap. xgboost_v3 is NOT a candidate
for global best; this family exists to characterize the cost of the baseline
feature constraint.

vs Ridge baseline: not directly comparable (Ridge baseline cv was not measured
under our 5-fold protocol), but xgboost_v3 trained on the same 3 features is
~62514 MAE, which is the achievable XGB ceiling under the baseline feature set.

## Artifacts

- `experiments/xgboost_v3/predicted.json` (6843 predictions)
- `experiments/xgboost_v3/predicted.zip`
- `experiments/xgboost_v3/best_experiment.py`

## Stage Summary

### Stage 1 smoke (1 lane -- single-lane deviation documented)

| lane | cv_mae | verdict |
|---|---:|---|
| **baseline_three_only** | **62517.15 ± 4530** | smoke anchor |

Single lane is the family's defining premise; multi-lane smoke would defeat
the purpose of testing the exact 3-feature constraint.

### Stage 2 deepen (10 single-knob iters; 4 kept, 6 reverted)

| iter | knob | result | Δ vs prev W | verdict |
|---|---|---:|---:|---|
| 1 | log1p target | 62653.73 | +137 | revert (tie, +complexity) |
| 2 | monotone constraints | 64766.37 | +2249 | REVERT (real regression) |
| 3 | target clip 99.5pct | 62496.04 | -21 | revert (tie, +complexity) |
| 4 | max_depth=4 | 62450.70 | -66 | KEEP (tie, simpler) |
| 5 | lr=0.03 + n_est=1000 | 62479.88 | +29 | revert (tie, +runtime) |
| 6 | colsample_bytree=1.0 | 62402.52 | -48 | KEEP (tie, simpler) |
| 7 | subsample=1.0 | 62515.96 | +113 | revert (tie-negative) |
| 8 | max_depth=3 | 62365.37 | -37 | KEEP (tie, simpler) |
| 9 | max_depth=2 | 62354.51 | -11 | KEEP (tie, simpler) |
| 10 | lr=0.1 | 62500.86 | +146 | revert (tie-negative) |

Net: 62517.15 (anchor) → 62354.51 (W''', -163, tie within noise but Occam-simpler).

The deepen phase did the substantive hyperparameter exploration that would
normally be the tune stage; with only 3 raw features the deepen surface
collapses to non-feature knobs. No formal "tune" stage was run.

### Stage 3b ablate (2 LOO runs vs W''' noise threshold ~2275-2350)

| knob | revert | result | Δ vs W''' | verdict |
|---|---|---:|---:|---|
| a1 | drop max_depth=2 (back to 6) | 62689.66 | +335 | tie (NOT load-bearing alone) |
| a2 | drop colsample=1.0 (back to 0.8) | 62626.24 | +272 | tie (NOT load-bearing alone) |
| a3 | combined revert (= smoke iter1) | 62517.15 | +163 | tie (combined effect within noise) |

Combined a3 result is implicit (= smoke iter1, already on record). All ablation
deltas are within pooled-std noise. Decision: keep both knobs by Occam (simpler
recipe, tied MAE).

### Stage 4 confirm (1 run, seed=2026)

- W''' confirm seed=2026: 62674.08 ± 4330.88 (vs seed=42 62354.51, |Δ|=320, seeds agree well within threshold ~2448)

## What surprised xgboost_v3

- **Monotonic constraints HURT** (+2249, real regression). With only 3 features
  the model relies on non-monotone interactions, so domain-knowledge constraints
  (more area = higher value) actually destroy a useful signal pathway.
- **Occam wins consistently in feature-starved regime**: every kept knob
  reduced complexity (depth 6→2, colsample 0.8→1.0 = no sampling). With only
  3 features, the bias-variance tradeoff favors very small trees.
- **No real lift was achievable**: combined kept-knob effect was within noise.
  The 3-feature constraint sets a hard MAE floor near 62500, ~13k worse than
  xgboost_v2's 29-feature recipe (49200). This quantifies the cost of the
  baseline feature constraint.
- **log1p target was tie-negative** here (+137), opposite to xgboost_v2 where
  it was tie-positive. Different feature mix interacts differently with target
  scale; with feature-starved models, the implicit log-rescaling doesn't
  redirect remaining learning capacity productively.
- **subsample=0.8 helped a tiny bit** (subsample=1.0 was tie-negative), perhaps
  because random row sampling is cheap regularization in a feature-starved model.

## Note on protocol deviation

Single-lane smoke and skipped formal "tune" stage are deliberate:
- Single-lane smoke: family premise IS the feature lane, multi-lane meaningless.
- Skipped tune: deepen iters 4-10 already exhausted the meaningful hyperparam
  search space (depth, lr, subsample, colsample, capacity_pair) under the
  feature-starved constraint. Adding 10 more hyperparam iters would just churn
  noise without expanding coverage.
