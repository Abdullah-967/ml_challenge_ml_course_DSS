# xgboost_v6 Notes

## Status

**Promoted.** Stages: smoke=3, deepen=5.

## Best Result

- recipe: v4 W''''' anchor + top-15 per-type sub-models + n_estimators=6000
- seed=42 cv_mae: **46,653.36 +/- 5,466.57** (`20260509-173002-deepen-v4_anchor`)
- seed=2026 cv_mae: **47,192.53 +/- 3,177.34** (`20260509-174840-deepen-v4_anchor`)
- 2-seed mean: **46,922.95**
- previous best 2-seed mean: xgboost_v5 at **47,350.05**
- delta vs xgboost_v5 2-seed mean: **-427.10**

## Decision

Promoted `20260509-174840-deepen-v4_anchor` after seed-2026 confirmation.
The confirmed recipe beats all previous raw seed-42 iterations and improves the
best two-seed xgboost mean, although the margin remains within the fold-noise
band. Final artifacts are written under this family and copied to the repository
root.

## Artifacts

- `experiments/xgboost_v6/predicted.json`
- `experiments/xgboost_v6/predicted.zip`
- top-level `predicted.json`
- top-level `predicted.zip`

## Search Summary

Smoke feature lanes did not help: bounded parcel numeric components timed out
on the v5-heavy anchor and regressed on the v4 anchor, while `commune_section`
also regressed. The winning path was architectural/capacity:

- top-15 per-type sub-models at n_est=4000: 46,946.76
- top-15 per-type sub-models at n_est=5000: 46,879.26
- top-15 per-type sub-models at n_est=6000: 46,653.36
