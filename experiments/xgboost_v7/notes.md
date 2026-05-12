# xgboost_v7 Notes

## Status

**Promoted.** Stages: smoke=3, deepen=2.

## Best Result

- recipe: v6 promoted anchor + top-15 per-type sub-models + n_estimators=8000
- seed=42 cv_mae: **46,308.02 +/- 5,754.24** (`20260509-192702-deepen-v6_capacity_path`)
- seed=2026 cv_mae: **47,233.08 +/- 3,051.72** (`20260509-195253-deepen-v6_capacity_path`)
- 2-seed mean: **46,770.55**
- previous best 2-seed mean: xgboost_v6 at **46,922.95**
- delta vs xgboost_v6 2-seed mean: **-152.39**

## Decision

Promoted `20260509-195253-deepen-v6_capacity_path` after seed-2026
confirmation. The recipe is a directional global winner over xgboost_v6 on
both the seed-42 raw leaderboard and the two-seed mean comparison. The margin
is still within fold noise, so treat it as a confirmed incremental improvement,
not a large statistical separation.

## Wide Smoke Summary

Three wide lanes were run before deepening:

- Lane A, top20/min100 sub-model coverage: 47,216.68, reverted.
- Lane B, lower submodel blend weight 0.3 -> 0.2: 46,726.02, reverted.
- Lane C, n_estimators 6000 -> 7000: 46,498.56, kept.

Only after lane C won smoke did the search deepen along capacity:

- n_estimators=8000: 46,308.02, kept and confirmed.

## Artifacts

- `experiments/xgboost_v7/predicted.json`
- `experiments/xgboost_v7/predicted.zip`
- `experiments/xgboost_v7/xgboost_v7.ipynb`
- top-level `predicted.json`
- top-level `predicted.zip`
- top-level `solution.ipynb`
