# xgboost_v8 Notes

## Status

**PROMOTED (family-level).** Stages: smoke=3, deepen=10, tune=10, confirm=2.

Final candidate: **iter7 features (presence_flags) + lr=0.07 + restored capacity (n_est=8000, top_k=15)** at log1p target, blend=0.3.

## Family Best Result (final candidate)

- recipe: xgboost_v7-style anchor + 5 presence_flags (has_apartments, has_houses, has_commercial, has_dependencies, has_lots) + lr=0.07 (tune-best knob)
- seed=42 cv_mae: **47,821.69 +/- 5,237.42** (`20260510-051940-confirm-v8_final_seed42`)
- seed=2026 cv_mae: **47,452.08 +/- 2,901.19** (`20260510-054235-confirm-v8_final_seed2026`)
- 2-seed mean: **47,636.88**

## Comparison vs xgboost_v7 promoted

| | v7 promoted | v8 final |
|---|---:|---:|
| seed=42 | 46,308.02 | 47,821.69 |
| seed=2026 | 47,233.08 | 47,452.08 |
| **2-seed mean** | **46,770.55** | **47,636.88** |
| delta vs v7 (mean) | — | +866.33 |

Pooled-std vs v7 2-seed mean: noise band ~1,000-1,400. |delta|=866 -> **tie_within_noise** vs v7 promoted. v8 does NOT beat v7 by a noise-aware margin.

## Decision

Park v8 as a **runner-up / blend candidate**, not as new global champion. Per CLAUDE.md and search_policy: "A within-noise tie versus the global champion is not grounds for promotion to global champion." Top-level `predicted.json` and global champion stay v7. v8 family-level artifacts generated for blending or future use.

## Smoke Stage Summary (3/3 at smoke shrink n=4000/top_k=10)

| lane | hypothesis_unit | cv_mae | cv_mae_std | runtime_s |
|------|------|---:|---:|---:|
| A | structural_numeric_baseline (+4 cadastral counts) | 48,468.89 | 4,727.28 | 1083.6 |
| B | room_area_density_ratios (+10 cols) | 48,002.73 | 5,199.55 |  756.3 |
| C | drop_sparse_room_layout (-8 cols) | 48,236.73 | 5,068.73 |  641.1 |

All within noise. Picked B as deepen anchor (lowest absolute MAE).

## Deepen Stage Summary (10/10 at restored capacity)

| iter | knob | cv_mae | runtime_s |
|---|---|---:|---:|
| 1 | density ratios + capacity restore | 48,040.81 | 1943 |
| 2 | drop density (= v7 features) | 47,978.89 | 1488 |
| 3 | drop sparse rooms on iter2 | 48,461.88 | 1247 |
| 4 | + cadastral counts on iter3 | 48,492.17 | 1285 |
| 5 | drop dept_code, region_code | 48,302.65 | 1301 |
| 6 | log_skewed_numerics (areas) | 47,978.89 | 1302 |
| **7** | **+ presence_flags (5)** ← deepen-best | **47,963.50** | **1323** |
| 8 | + parcel_density_ratios (4) | 48,718.82 | 1357 |
| 9 | + month_cyclical (sin/cos) | 48,549.83 | 1377 |
| 10 | drop sparse rooms on iter7 | 48,329.38 | 1262 |

All deepen iterations within pooled-std noise of each other. Picked iter7 as tune anchor.

## Tune Stage Summary (10/10 at smoke shrink)

| iter | knob | cv_mae | runtime_s |
|---|---|---:|---:|
| 1 | lr 0.05->0.03 | 48,454.12 | 600 |
| **2** | **lr 0.05->0.07** ← tune-best | **47,875.82** | **589** |
| 3 | max_depth 6->5 | 47,916.64 | 529 |
| 4 | max_depth 6->7 | 48,793.77 | 682 |
| 5 | mcw 5->3 | 48,376.03 | 615 |
| 6 | mcw 5->10 | 48,687.38 | 565 |
| 7 | subsample 0.8->0.7 | 48,426.72 | 576 |
| 8 | colsample 0.6->0.5 | 48,070.43 | 577 |
| 9 | reg_lambda 1->5 | 48,262.93 | 625 |
| 10 | blend 0.3->0.2 | 48,040.87 | 637 |

lr=0.07 best by 41 cv_mae over max_depth=5 (within noise). Adopted lr=0.07 for final candidate.

## Smoke Shrink Note

Smoke and tune used n_estimators=4000 / top_k=10 (user-approved). Deepen and confirm used n_estimators=8000 / top_k=15 (full v7-equivalent capacity). Tune-winner recipe re-tested at restored capacity for the final two confirm runs.

## Key Methodological Findings

1. **XGBoost thread non-determinism**: code-identical runs with same seed produce ~5,000 cv_mae variation on folds 0-1 (folds 2-4 stable within ~100). This dominates single-knob signal in this family — most ablations land within ~1,500 noise band.
2. **Density ratios neutral, not negative**: iter1 stand-alone reading suggested +1700 regression; iter2 (drop density) confirmed the effect was almost entirely thread-determinism, not feature signal.
3. **Log transforms are no-ops** under tree_method=hist with quantile bins (iter6 was bit-identical to iter2).
4. **Feature space saturated** at v7 anchor: every numeric feature add/drop tested at restored capacity ties within noise.

## Artifacts

- `experiments/xgboost_v8/best_experiment.py` -- final candidate recipe (= seed=42 confirm experiment.py)
- `experiments/xgboost_v8/predicted.json` -- v8 family predictions (6,843 rows)
- `experiments/xgboost_v8/predicted.zip` -- zipped form for submission compat
- `experiments/xgboost_v8/iteration_log.md` -- 25 reflected runs (3+10+10+2)
- `experiments/xgboost_v8/results.tsv` -- structured run history
- `experiments/xgboost_v8/variants/*.py` -- 18 frozen recipes (3 smoke + 10 deepen + 10 tune base+overrides + 2 final)

Top-level `predicted.json` and root `experiments/results.tsv` not modified — v7 remains the global champion.
