# gradient_boosting_sklearn Notes

## Status

Stage 1 smoke complete (3/3). Stage 2 deepen complete (15/15 single-knob iterations -- full upper budget). **Recommended decision: park** as a cheap and architecturally-diverse blend candidate. No noise-aware path to global champion `xgboost_v6` (delta +6328, far outside noise band ~1126).

## Best Result

`20260509-210426-deepen-geo_signal` (deepen iter13) -- cv_mae = **53250.72 +/- 4268.62** in 101.4 s. Recipe: smoke geo_signal anchor + max_depth=4 + n_estimators=200 (lr=0.1 unchanged, single-knob bumps stacked attributively across iter3 and iter13).

```python
GradientBoostingRegressor(
    loss="absolute_error",
    n_estimators=200,
    learning_rate=0.1,
    max_depth=4,
    subsample=0.8,
    random_state=42,
)
# + commune_codes fold-safe smoothed mean-target encoding (k=20)
# + median imputation
```

vs global best xgboost_v6 (46922.95 two-seed mean): delta = +6328 (clear regression beyond 1126 noise band; ~13% above global). vs prior HGB iter21 (50907): delta = +2344 (still regression; hist-based GBR remains stronger on this dataset).

## Two clear deepen wins, 13 ties

- iter3 (max_depth 3 -> 4): clear improvement (-1313 mean) over smoke geo_signal.
- iter13 (n_estimators 100 -> 200): -852 mean / -10% std vs iter3. Mean tie within noise but std drop is meaningful; promoted on combined diagnostic.

Other simpler / more-stable variants worth recording for a future blend study:
- iter12 (drop sparse room layout): -8% std, -50% feature count, mean tied -- cleanest minimal-feature variant.
- iter14 (n_est=300 on iter13): -12% std vs iter13, mean tied; useful if a stability-oriented variant is needed.

## Smoke Summary

| run_id | lane | cv_mae | cv_mae_std | runtime_s | vs anchor (A) |
|---|---|---|---|---|---|
| 20260509-195547-smoke-all_numeric | all_numeric | 57603.89 | 5025.89 | 28.6 | (anchor) |
| 20260509-195905-smoke-numeric_plus_basic_cats | numeric_plus_basic_cats | 57111.24 | 5119.16 | 45.7 | tie within noise |
| 20260509-200605-smoke-geo_signal | geo_signal | 55415.36 | 4841.21 | 31.2 | clear improvement (-2188) |

## Deepen Summary (anchor = smoke geo_signal unless noted)

| run_id | knob | cv_mae | cv_mae_std | runtime_s | vs iter3 | verdict |
|---|---|---|---|---|---|---|
| iter1 (...01207) | log1p target | 55117.55 | 4972.12 | 46.8 | n/a (anchor=smoke) | discard (tie vs smoke + adds transform) |
| iter2 (...01610) | capacity_pair n_est=300/lr=0.05 | 54588.05 | 4641.28 | 90.7 | n/a (anchor=smoke) | discard (tie vs smoke + 3x runtime) |
| **iter3 (...02125)** | **max_depth=4** | **54102.89** | **4723.25** | **41.0** | **(family best)** | **keep** |
| iter4 (...03134) | max_depth=5 | 53653.44 | 4911.41 | 51.9 | -449 (tie, std rose) | discard |
| iter5 (...03703) | cadastral TE k=20 | 53941.17 | 4741.89 | 47.9 | -162 (tie) | discard |
| iter6 (...03939) | area_density_ratios | 54166.89 | 4539.11 | 47.2 | +64 (tie, std improved) | discard |
| iter7 (...04222) | commune TE k=5 | 54165.88 | 4705.71 | 43.1 | +63 (tie) | discard |
| iter8 (...04456) | log_skewed_numerics (14 areas) | 54119.38 | 4678.23 | 89.9 | +16 (tie) | discard |
| iter9 (...04818) | min_samples_leaf=20 | 54315.85 | 4777.65 | 86.1 | +213 (tie) | discard |
| iter10 (...05101) | subsample=1.0 | 54452.74 | 4734.67 | 93.7 | +350 (tie) | discard |
| iter11 (...10000) | max_features='sqrt' | 55271.21 | 5119.33 | 39.0 | +1168 (tie, std worse) | discard |
| iter12 (...10203) | drop sparse room layout | 54180.0 | 4365.60 | 39.1 | +77 (tie, std -8%, simpler) | keep (simpler variant) |
| **iter13 (...10426)** | **n_estimators=200** | **53250.72** | **4268.62** | **101.4** | **-852 (tie on mean, std -10%)** | **keep -- new family best** |
| iter14 (...10726) | n_est=300 (chained on iter13) | 53435.84 | 3768.28 | 159.3 | +185 vs iter13 (tie, std -12% / slower) | discard (slower) |
| iter15 (...11120) | depth=5 (chained on iter13) | 53334.82 | 4680.65 | 200.1 | +84 vs iter13 (tie, std worse) | discard (depth saturated) |

**Two clear wins across 15 deepens:** max_depth=4 (iter3) and n_estimators=200 (iter13). Together they take the family from smoke geo_signal 55,415 -> 53,251 (-2,164 mean, -13% std). iter4 and iter15 both confirmed depth saturates at 4. iter14 confirmed n_est plateaus at ~200 for mean (std keeps dropping but at runtime cost).

## Decision

Park. Family final best (iter13) is +6,328 above global champion xgboost_v6 -- well outside the 1,126 noise band. Keep the smoke + deepen evidence on disk. Do NOT promote, do NOT seed-2026 confirm (no path to noise-aware win). If the family is wanted for blending later, iter13 is the canonical recipe; iter12 / iter14 are documented simpler / more-stable alternatives.

## Next Action

User decision: park vs run seed=2026 confirm of iter13 vs further work. Default = park.

## Precondition Bugs Resolved

- **20260509 run `20260509-195144-smoke-all_numeric`**: failed at fit time with `Input X contains infinity or a value too large for dtype('float32')`. Root cause: `parcel_ids` / `transferred_parcel_ids` are comma-joined ID strings that pandas coerced to floats up to ~8.6e+259, which overflows sklearn's internal float32 cast inside `GradientBoostingRegressor.fit`. `commune_codes` / `cadastral_sections` were also slipping in as object-numeric. Fix: extended `DROP_FROM_NUMERIC` in `current_experiment.py` to exclude all four columns plus `region_code`. The failed run is left on disk for audit but is **not** reflected as evidence — it is a setup bug, not a model observation.

## Decision

Re-plan smoke lane A with the fixed anchor.

## Next Action

`mfm_cli.py plan --family gradient_boosting_sklearn --feature-lane all_numeric --change-kind feature --hypothesis-unit structural_numeric_baseline --feature-group structural_numeric --write`
