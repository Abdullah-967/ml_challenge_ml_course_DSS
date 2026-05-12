# xgboost_v5 Notes

## Status

**Parked.** Stages: smoke=3, deepen=10, confirm=1.

## Family premise

Beat xgboost_v4 W''''' (47107.53 seed=42, 47553.01 2-seed mean) by a margin
the user described as "by far" (~ 2x pooled noise band, target <= ~44,950).
Probe orthogonal new signal sources at v4's full capacity recipe.

## Best Result (parked, not promoted)

- recipe: iter10 = v4 W''''' anchor + top-10 per-type sub-models + n_est=5000
- seed=42 cv_mae: 46,909.14 +/- 5,296.85 (deepen iter10 `20260508-160016`)
- seed=2026 cv_mae: 47,790.96 +/- 3,596.40 (confirm `20260508-173019`)
- 2-seed mean: **47,350.05** (seed gap |Δ|=881.82, agrees within pooled noise)
- runtime: ~17-19 min per CV (5000 trees x 11 model fits)
- feature_lane: `v4_anchor` (no smoke lane was kept)
- two kept knobs over v4 W''''' (cumulative single-seed lift -198, 2-seed mean lift -203):
  - iter9: top-10 per-type sub-models (vs v4 top 5)
  - iter10: n_est 4000 -> 5000 (mechanically simple)

## Decision: PARK (NOT promoted)

vs v4 W''''' 2-seed mean (47553):
- iter10 2-seed mean: 47350 (delta_mae **-203**)
- pooled noise band: ~1100
- significance: **tie_within_noise** -- NOT a noise-aware win.

User requested "global winner by far" target (-2400+ vs 47553 = <=44950): **NOT MET, not even close**. v5's actual lift is ~10x smaller than the requested margin.

Per protocol (search_policy.md): "A within-noise tie versus the global champion is not grounds for promotion to global champion."

**v4 W''''' (xgboost_v4) remains the global champion.** v5 is recorded as a confirmed within-noise tie -- usable as a slightly more expensive runner-up or as a candidate for a future blend with diverse-bias models, but **not** a champion replacement.

## What we learned in v5

- **Smoke (3/3 reverted).** None of the orthogonal feature sources we probed cleared noise on top of v4:
  - `presence_flags` (informative-missingness): +1192, tie regression side
  - `id_token_counts` (parcel_ids/transferred token counts): +1694, regression
  - `commune_frequency` (fold-safe count): +1229, tie regression side
  -> v4's feature set is saturated for xgboost.
- **Deepen (10 iters; 2 kept tied-on-lift, 8 reverted).** Architectural and capacity probes:
  - iter4 cadastral_first TE smooth=20: +1304, regression. 846 levels not the right granularity.
  - iter5 3-seed averaging: +461, tie regression. Confirms v4 seed=42 is OPTIMISTIC; true mean is ~47550.
  - iter6 per-region replace per-type: +285, tie. region_code is dataset-near-constant.
  - iter7 sub-model max_depth=8: +28, tie. Sub-model capacity already saturated at depth=6.
  - iter8 XGB+HGB blend 50/50: +921, tie regression. HGB drags down (HGB-alone is 50934).
  - **iter9 top-10 sub-models: -130, tie LIFT (KEPT).** First v5 lift direction.
  - **iter10 n_est=5000: -198 cumulative, tie LIFT (KEPT).** Family best.
  - iter11 lr=0.04+n_est=6250 (paired): +1471, regression. Slower learning at fixed budget hurt.
  - iter12 BLEND 0.4: +121, tie regression. v4's 0.3 stays optimal.
  - iter13 subsample=0.7: +1024, tie regression. v4's 0.8 stays optimal.
- **Confirm.** iter10 seed=2026 = 47791 vs seed=42 = 46909, |Δ|=882 -- within v4's seed precedent (891). 2-seed mean 47350.

## What surprised xgboost_v5

- **3-seed averaging produced 47568** which essentially matches v4's 2-seed mean (47553). Both seed=42 single-seed scores (47107 v4, 46909 v5) were slight underestimates of the true expected value. This means evaluating raw improvement on a single seed=42 score systematically overstates a recipe's capability.
- **iter6 (per-region sub-models replace per-type) result equaled v4's drop-sub-models ablate exactly** (47392.22 to four decimals). Strong signal that `region_code` has near-zero diversity in the training set and per-region grouping degenerates to per-global. The feature_search_space.md note ("region_code constant in current training set") was directly observable in this experiment.
- **The cumulative lift per kept knob in v5 is ~70-130** (iter9 -130, iter10 -68), one order of magnitude smaller than v4's late-stage knobs (n_est ramp gave -126 to -482 each). v4 already absorbed most of the easily attributable signal; v5's headroom is dominated by fold noise.

## Artifacts

- `experiments/xgboost_v5/runs/20260508-160016-deepen-v4_anchor/` -- iter10 recipe (best seed=42 single-seed)
- `experiments/xgboost_v5/runs/20260508-173019-deepen-v4_anchor/` -- confirm seed=2026
- `experiments/xgboost_v5/iteration_log.md` -- full reflective log
- `experiments/xgboost_v5/results.tsv` -- structured run history

No `predicted.json` produced -- v5 is parked, not promoted, so no final-prediction artifact is generated. The promoted artifacts under `experiments/xgboost_v4/` (champion) remain authoritative.

## Recommended Next Action

1. **Keep `xgboost_v4` as the global champion.** The promoted artifacts in `experiments/xgboost_v4/` and the top-level `solution.ipynb` based on it are the canonical submission.
2. If pursuing further MAE improvement, the cheapest unattempted directions are likely:
   - **Cross-family blend** of v4 anchor with `tree_bagging_rf` (currently 50843 -- much weaker, likely won't help) or a fresh `lightgbm` family (high diversity, potentially worth a smoke).
   - **Stacking** with OOF predictions as a feature for a second-pass model (NOT residual stacking -- that catastrophically failed in v4 iter19).
   - **External signal**: if the user can ingest external data (e.g. INSEE commune-level price index), it would bring information not present in the current schema.
3. NOT recommended: more xgboost-only iterations on top of v4. Five rounds (xgboost, v2, v3, v4, v5) have been thoroughly searched; the curve has plateaued.
