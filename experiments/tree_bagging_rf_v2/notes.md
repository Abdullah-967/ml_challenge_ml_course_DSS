# tree_bagging_rf_v2 Notes

## Status

**Park (runner-up tie).** Stages: smoke=3, deepen=13, confirm=1. Promotion blocked by noise-aware gate.

## Best Result (family-best, NOT promoted)

- recipe: lane A = v1 promoted recipe + fold-safe `built_rel_type`
- seed=42 cv_mae: **50565.97 +/- 4813.84** (smoke lane A `20260508-222002`)
- seed=2026 cv_mae: **50900.23 +/- 4520.90** (confirm `20260509-155212`)
- 2-seed mean: **50733.10** (seed agreement: |Delta|=334, within pooled noise ~1167)
- runtime: ~222s per CV (seed=42), ~237s (seed=2026)
- feature_lane: `v1_anchor_plus_built_rel_type`
- recipe (best_experiment.py reflects this exactly):
  - features: v1 promoted recipe (numeric/bool excl ID cols + ratios + presence flags
    + commune/cadastral/property_type/transaction_type TE smooth=10 + commune_freq)
    + new fold-safe `built_rel_type` = `built_area / mean(built_area | property_type)`
  - target: log1p with expm1 inverse
  - model: `RandomForestRegressor(criterion=absolute_error, n_estimators=200,
    max_depth=18, min_samples_leaf=2, max_features=0.4, bootstrap=False,
    n_jobs=-1, random_state=42)`

## Decision

**Park as runner-up tie.** Promotion gate FAILED:

- 2-seed mean 50733.10 vs HGB iter21 global champion 50934.78: Delta = -201.68
- Pooled std ~ sqrt((4520.90^2 + 4795.53^2)/2) ~ 4660.30, threshold (0.25x) ~ 1165
- |Delta| = 202 << 1165 -> TIE WITHIN NOISE. Not a noise-aware win.

vs v1 promoted recipe (50753 2-seed mean): Delta = -20 (definitive tie). v2 essentially
reproduces v1 with one extra fold-safe ratio.

vs xgboost_v4 confirm (47998 seed=2026, ~47553 2-seed mean): Delta = +3180 (real-gap behind).

## Stage Summary

### Smoke (3 lanes, anchored on v1 promoted recipe)

| lane | knob added | cv_mae (seed=42) | verdict |
|---|---|---:|---|
| A | `built_rel_type` (fold-safe property_type-relative built area) | **50565.97** | best lane (family anchor) |
| B | `id_token_counts` (parcel/transferred token counts) | 50824.04 | tie+regress |
| C | `room_area_density_ratios` (10 area/num ratios) | 50575.66 | tie |

### Deepen (13 single-knob iters; 0 kept, 13 reverted)

| iter | knob | cv_mae | Delta vs lane A | verdict |
|---|---|---:|---:|---|
| D1 | +built_per_land cumulative | 50941.89 | +376 | discard |
| D2 | +room_density cumulative | 50705.80 | +140 | discard |
| D3 | ExtraTrees swap | 52459.34 | +1893 | REAL regression |
| D4 | n_est=400 | 50660.72 | +95 | tie |
| D5 | max_depth=22 | 50908.39 | +342 | tie+regress |
| D6 | min_samples_leaf=1 | 50740.33 | +174 | tie+regress |
| D7 | per-type submodels (top 3, blend 0.3) | 50602.36 | +36 | tie |
| D8 | log_skewed_numerics (9 cols) | 50691.82 | +126 | tie+regress |
| D9 | smooth=15 | 50767.98 | +202 | tie+regress |
| D10 | max_features=0.3 | 50886.08 | +320 | tie+regress |
| D11 | +built_rel_commune | 50676.01 | +110 | tie |
| D12 | n_est=600 | 50632.07 | +66 | tie (over-budget) |
| D13 | two-seed averaging inside fit_predict | 50581.73 | +16 | tie |

### Confirm (1 run)

- lane A confirm seed=2026: 50900.23 +/- 4520.90 (vs seed=42 50565.97; |Delta|=334, seeds agree)

## What surprised tree_bagging_rf_v2

- `built_rel_type` (the lane A knob) was the ONLY new feature unit that moved family below v1's
  anchor; even then only by -98 (within noise). xgboost_v4 saw -245 from the same exact unit;
  RF can't extract as much because its split points are not refined per-step the way boosting is.
- `built_per_land` regressed +376 in v2 even though xgboost_v4 logged it as -116. Land-area
  zeros are common (commercial/agricultural records); RF's median imputer collapses 1/0 to a
  noisy mode, hurting splits.
- ExtraTrees swap was a REAL regression (+1893). With max_features=0.4 + bootstrap=False already
  de-correlating trees, random splits added bias the RF didn't have headroom for.
- Per-property-type sub-models (proven xgboost_v4 lift -215) gave RF essentially +36 (tie).
  Boosting wins from per-type because each sub-model refines residuals on its own subset; RF
  just averages independently across trees regardless of sub-model partitioning.
- Capacity scaling fully saturated: n_est=200 (50566), n_est=400 (50661), n_est=600 (50632) --
  no monotonic trend. RF cannot extract more from this dataset by adding trees.
- Two-seed averaging tied at +16. With 200 trees, the per-seed fold MAE is already near the
  irreducible-noise floor; a second seed buys negligible additional variance reduction.

## Promotion path (not for v2)

xgboost_v4 confirm seed=2026 cv_mae **47998.49 +/- 3831.88** is -2937 vs HGB iter21
(threshold ~1188 -> well past noise band). It is the actual global-promotable winner of
the existing experiment grid. tree_bagging_rf_v2 does not reach that band; further RF
iteration is unlikely to succeed.

## Artifacts

- `experiments/tree_bagging_rf_v2/best_experiment.py` (lane A seed=42 recipe)
- `experiments/tree_bagging_rf_v2/current_experiment.py` (mirror)
- `experiments/tree_bagging_rf_v2/iteration_log.md` (full reflection trail)
- `experiments/tree_bagging_rf_v2/results.tsv` (17 rows: 3 smoke + 13 deepen + 1 confirm)
