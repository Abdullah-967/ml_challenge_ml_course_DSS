# xgboost_v9 Notes

## Premise

First-principles XGBoost round driven by `mfm_cli.py analyze` and backward
selection. Smokes started at the baseline-3-features regime; deepen explored a
10-feature analyze-derived pool by dropping one feature at a time. Multi-knob
lean-subset confirmation iters bound the recipe floor.

## Status

**PARKED** (2026-05-10). Deepen budget exhausted (smoke=3, deepen=15). User
chose immediate park without seed=2026 confirm. Family is a documented
first-principles audit, not a global-champion contender. Best recipe and
lean_7 finding are preserved in `results.tsv` and `iteration_log.md`.

## Best Result

`20260510-112454-deepen-backward_select_drop_month` -- cv_mae **58580.21 +/-
4671.43** (9 features = pool10 minus `month`).

Interpretable-tie alternative: `20260510-112836-deepen-lean_7_drop_strongest_ties`
-- cv_mae 58720.16 +/- 4468.14 with only 7 features
{built_area, land_area, house_area, num_lots, num_commercial, num_house_2_rooms,
year}. 30% smaller feature set, MAE ties the anchor within noise (delta=+114,
noise_band=~1109). Cleaner candidate for any downstream blending.

## First-Principles Findings (analyze + backward selection)

- Top non-redundant target correlations: built_area (0.55), num_lots (0.38),
  num_commercial (0.34); rest drop below |r|=0.17.
- Smoke triad: pure-area triplet (61254) and top-corr-mixed triplet (62280)
  tie within noise; pure-count triplet collapses to 72561 (+11k). Counts
  alone do not encode the price signal.
- Backward selection on the 10-feature analyze pool: only **built_area** (drop
  +1919) and **land_area** (drop +1950) are individually essential. The other
  8 features each show within-noise single-drop deltas.
- Compound drops: dropping all 8 tie-droppers together (`keystone_pair_only`,
  2 features) regresses by +4828. The 8 features carry collective signal that
  individual ablation hides. The "lean floor" is between 5 and 7 features:
  lean_5 (5 features) regresses (+1352); lean_7 (7 features) ties (+114).

## Decision

**Parked.** v9 best (58580) is ~+11k worse than the global champion
(xgboost_v8 at ~47452). The value of v9 is the first-principles audit
(built_area + land_area are the two essential features) and the interpretable
7-feature lean recipe. No promote, no confirm. Available as a future
blend-diversity candidate if an ensemble family is ever opened.

## Next Action

None for v9. Move to a new family/idea per user direction.
