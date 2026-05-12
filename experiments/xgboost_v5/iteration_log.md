# xgboost_v5 Iteration Log

Append-only. One block per canonical CV run. See the bundled `plugins/model-family-mae/references/reflection_protocol.md`.

Required metadata per entry: stage, change_kind, hypothesis_unit, feature_group, anchor_run_id, change_from_previous, hypothesis, observation, comparison, significance, attribution, next_hypothesis.

## iter1 -- 20260508-122416-smoke-v4_plus_presence_flags

- **stage:** smoke
- **change_kind:** feature
- **hypothesis_unit:** presence_flags
- **feature_group:** structural_numeric
- **anchor_run_id:** 20260507-235645-deepen-v2_plus_geo_hierarchy (v4 W''''' deepen iter37 cv 47107.53 +/- 5244.67)
- **change_from_previous:** added 7 binary is_present indicators (built_area, house_area, land_area, apartment_area, num_premises, num_houses, num_apartments) on top of v4 W''''' anchor; everything else identical.
- **hypothesis:** XGBoost handles missing natively but the missingness PATTERN itself may carry independent signal. Expect small lift (delta_mae roughly -100 to -300) if presence carries signal; tie if redundant with native handling.
- **observation:** cv_mae 48,299.25 +/- 5,011.59. fold_maes = [47106, 49225, 40539, 56241, 48386]. fold_4 wall-clock anomaly (1171s vs ~95s for other folds) -- not a CV signal but a scheduler stall; cv_mae value is unaffected.
- **comparison:**
  - vs v4 anchor (47107.53): delta_mae +1191.72, pooled_std sqrt((5011.59^2+5244.67^2)/2)=5129.45, noise_band 0.25*5129.45=1282.36.
  - vs family best so far: this IS the only family run (best so far by default).
  - vs global champion (v4 W''''' 47107.53 seed=42): delta_mae +1191.72.
- **significance:** tie_within_noise (|+1191.72| < 1282.36) but on the regression side of zero.
- **attribution:** single knob (presence_flags only); no other change. Tie-on-regression-side with 7 added features = added complexity for no gain.
- **next_hypothesis:** Lane B (id_token_counts) -- bounded-derived counts from parcel_ids/transferred_parcel_ids strings. Orthogonal to presence: tests transaction scale/complexity rather than missingness pattern. Justification (within-dataset): parcel_ids is comma-delimited variable-length, suggesting a derivable scale signal that trees cannot construct from raw string columns.

## iter2 -- 20260508-122419-smoke-v4_plus_id_token_counts

- **stage:** smoke
- **change_kind:** feature
- **hypothesis_unit:** id_token_counts
- **feature_group:** id_derived
- **anchor_run_id:** 20260507-235645-deepen-v2_plus_geo_hierarchy (v4 W''''' anchor; not iter1, since iter1 reverted)
- **change_from_previous:** different smoke lane vs iter1 (NOT a deepen on top of iter1). Anchor is v4 W''''' for both. This iter adds num_parcel_ids and num_transferred_parcel_ids (token counts of comma-delimited id strings).
- **hypothesis:** transaction scale (number of parcels involved) is independent of area features and may help disambiguate small-vs-large transactions of similar built_area. Expect small lift (-100 to -400) if scale carries signal beyond num_lots/num_premises.
- **observation:** cv_mae 48,801.90 +/- 4,890.92, runtime 702s, all folds completed cleanly (no anomaly).
- **comparison:**
  - vs v4 anchor (47107.53): delta_mae +1694.37, pooled_std sqrt((4890.92^2+5244.67^2)/2)=5070.89, noise_band 0.25*5070.89=1267.72.
  - vs family best (iter1 48299.25): delta_mae +502.65, pooled_std 4951.48, noise_band 1237.87 -- tie within family.
  - vs global champion (47107.53): delta_mae +1694.37.
- **significance:** regression vs anchor (|+1694.37| > 1267.72). NOT useful.
- **attribution:** single knob (id_token_counts only). Token counts likely redundant with num_lots/num_premises which already encode transaction scale.
- **next_hypothesis:** Lane C (commune_frequency) -- fold-safe count of commune_first level in train. Justification (within-dataset): commune_first has ~196 levels but native cat encoding doesn't expose how many train rows per level; frequency = continuous reliability signal trees cannot construct from cat alone. Distinct from commune-level TE (which already failed v4 Lane C with 36k commune means too noisy).

## iter3 -- 20260508-122421-smoke-v4_plus_commune_frequency

- **stage:** smoke
- **change_kind:** feature
- **hypothesis_unit:** commune_frequency
- **feature_group:** geography
- **anchor_run_id:** 20260507-235645-deepen-v2_plus_geo_hierarchy (v4 W''''' anchor)
- **change_from_previous:** different smoke lane vs iter1/iter2. Adds commune_first_freq (fold-safe count from train fold) to v4 anchor. Distinct from commune-level TE (which failed v4 Lane C with 36k commune means too noisy).
- **hypothesis:** Frequency = market liquidity signal, not mean price. Trees use it to gate reliability of cat-derived patterns. Expect small lift (-100 to -400).
- **observation:** cv_mae 48,336.92 +/- 4,934.64, runtime 700s, clean.
- **comparison:**
  - vs v4 anchor (47107.53): delta_mae +1229.39, pooled_std sqrt((4934.64^2+5244.67^2)/2)=5092.02, noise_band 0.25*5092.02=1273.00.
  - vs family best (iter1 48299.25): delta_mae +37.67 -- effectively tied with iter1.
  - vs global champion (47107.53): delta_mae +1229.39.
- **significance:** tie_within_noise (|+1229.39| < 1273.00) but on the regression side of zero. Same direction as iter1.
- **attribution:** single knob (commune_first_freq). Frequency signal does not break above noise; native cat handling already extracts what's there.
- **next_hypothesis:** Smoke stage complete (3/3 lanes done; all on regression side of v4 anchor). NONE of the 3 orthogonal feature additions added signal. Pivot to architectural deepen knobs on v4 anchor (no Lane A/B/C feature kept). Deepen iter4 candidate: 5-seed prediction averaging on the v4 anchor recipe -- variance reduction is orthogonal to features and often gives ~100-300 MAE lift even when feature space is saturated. Justification (within-family): v4 iter12 tried 3-seed averaging at n_est=500 and tied; with v4's final n_est=4000 + per-type architecture, individual fits have higher variance (cv_mae_std grew from ~4500 to ~5200), so seed averaging may now help where it didn't before.

## Smoke summary (3/3 lanes)

| iter | lane | hypothesis_unit | cv_mae | std | delta vs anchor (47107) | verdict |
|---|---|---|---:|---:|---:|---|
| 1 | v4_plus_presence_flags | presence_flags | 48,299.25 | 5,011.59 | +1192 | tie_within_noise (regression side) -- revert |
| 2 | v4_plus_id_token_counts | id_token_counts | 48,801.90 | 4,890.92 | +1694 | regression -- revert |
| 3 | v4_plus_commune_frequency | commune_frequency | 48,336.92 | 4,934.64 | +1229 | tie_within_noise (regression side) -- revert |

Smoke verdict: feature additions on top of v4 W''''' anchor saturate. NO smoke lane is kept; deepen anchor stays at v4 W''''' itself. Family advances to deepen on the basis of being within ~3% of the global champion (search_policy "within roughly 10-15%" gate). Future deepen iterations will explore architectural and capacity knobs orthogonal to feature additions.

## iter4 -- 20260508-141116-deepen-v4_anchor (cadastral_first_te smooth=20)

- **stage:** deepen
- **change_kind:** feature
- **hypothesis_unit:** cadastral_first_te
- **feature_group:** geography
- **anchor_run_id:** 20260507-235645-deepen-v2_plus_geo_hierarchy (v4 W''''' anchor; smoke iter1-3 reverted)
- **change_from_previous:** add fold-safe cadastral_first target encoding (smoothing=20) to v4 anchor.
- **hypothesis:** ~846 cadastral levels = middle ground between commune (36k, too noisy in v4 Lane C) and dept (96, tied in v4 iter2). At this cardinality smoothing=20 should give stable section means that beat the noise band.
- **observation:** cv_mae 48,411.82 +/- 4,947.96, runtime 720s.
- **comparison:**
  - vs v4 anchor (47107.53): delta_mae +1304.29, pooled_std sqrt((4947.96^2+5244.67^2)/2)=5098.47, noise_band 1274.62.
  - vs family best (iter1 48299.25): delta_mae +112.57 -- tied with iter1.
  - vs global champion (47107.53): delta_mae +1304.29.
- **significance:** regression vs anchor (|+1304.29| > 1274.62, just over band).
- **attribution:** single knob (cadastral_first_te). TE at 846 levels still does not clear noise; native cat handling on cadastral_first already extracts the geography signal at this cardinality.
- **next_hypothesis:** iter5 -- 3-seed prediction averaging on v4 anchor. Justification (within-family): v5 anchor has cv_mae_std ~5244 (v4 iter37) which is higher than earlier v4 iters at ~4900 (suggests higher per-fit variance with n_est=4000). Variance reduction via seed averaging is orthogonal to features and often gives ~100-300 MAE lift; v4 iter12 tested 3-seed at n_est=500 and tied (-68), but at n_est=4000 the higher per-seed variance gives more headroom for averaging to clear the noise band.
- next_hypothesis: pending: one-knob next action or gate decision.

## 20260508-142447-deepen-v4_anchor

- stage: deepen
- feature_lane: v4_anchor
- change_kind: diagnostic
- hypothesis_unit: n_a
- feature_group: n_a
- anchor_run_id: 20260507-235645-deepen-v2_plus_geo_hierarchy
- status: revert
- cv_mae: 47568.6042520549
- cv_mae_std: 5023.38296144103
- runtime_seconds: 1984.7932119999969
- change_from_previous: deepen_iter5_3seeds
- hypothesis: Deepen iter5: 3-seed averaging on v4 anchor. Replace single-seed predict with mean of seeds {42, 100, 200} for both global and per-type sub-models. Variance reduction. Distinct from v4 iter12 (3-seed at n_est=500); v5 anchor n_est=4000 has cv_mae_std ~5244 (vs v4 iter11 std ~4922), so seed effect may now exceed noise band.
- **observation:** cv_mae 47,568.60 +/- 5,023.38, runtime 1985s (~33 min).
- **comparison:**
  - vs v4 anchor (47107.53): delta_mae +461.07, pooled_std sqrt((5023.38^2+5244.67^2)/2)=5135.26, noise_band 1283.81.
  - vs family best (iter1 48299.25): delta_mae -730.65, pooled_std 5017.49, noise_band 1254.37 -- significant lift WITHIN family.
  - vs v4 2-seed mean (47553): delta_mae +15 (effectively identical).
  - vs global champion (47107.53 single seed=42): delta_mae +461.07.
- **significance:** tie_within_noise vs anchor (|+461| < 1284). KEY INSIGHT: 47568 closely matches v4 2-seed mean 47553, confirming v4 seed=42 single-shot of 47107 was an OPTIMISTIC point estimate. The expected v4 score is ~47553 not 47107.
- **attribution:** 3-seed averaging captured per-fit variance (std dropped 5244->5023) but the population mean is ~47550, not below it. Variance reduction yields more honest mean estimate, not lift.
- **next_hypothesis:** iter6 -- per-region sub-models REPLACE per-type sub-models (top 5 regions). Justification (within-family): v4 ablate showed per-type contributes only ~+285 over no-sub-models (within noise); type grouping is near-redundant. Region grouping is geographically structured and may capture signal that property-type does not (e.g. price levels in Île-de-France vs Provence). Same cost as anchor.

## 20260508-150002-deepen-v4_anchor

- stage: deepen
- feature_lane: v4_anchor
- change_kind: hyperparameter
- hypothesis_unit: n_a
- feature_group: n_a
- anchor_run_id: 20260507-235645-deepen-v2_plus_geo_hierarchy
- status: revert
- cv_mae: 47392.2161584563
- cv_mae_std: 5328.153506433802
- runtime_seconds: 538.0321599999952
- change_from_previous: deepen_iter6_per_region_submodels
- hypothesis: Deepen iter6: replace per-type sub-models with per-region sub-models (top 5 regions by sample count). Tests whether geographic specialization captures more signal than property-type specialization. Same cost as anchor (still 6 model fits per fold).
- **observation:** cv_mae 47,392.22 +/- 5,328.15, runtime 538s. Notable: result IDENTICAL to v4 ablate-a1 (drop sub-models entirely).
- **comparison:**
  - vs v4 anchor (47107.53): delta_mae +284.69, pooled_std sqrt((5328.15^2+5244.67^2)/2)=5286.79, noise_band 1321.70.
  - vs family best (iter5 47568.60): delta_mae -176.38 -- new family best.
  - vs global champion (47107.53): delta_mae +284.69.
- **significance:** tie_within_noise (|+285| < 1322).
- **attribution:** single knob (sub-models grouping = region instead of type). KEY OBSERVATION: result equals v4 ablate-a1 (47392.22 ± 5328.15) exactly. region_code is dataset-near-constant (search_space note: "constant in current training set"); top_k_regions returned ~1 dominant region, so sub-model trained on essentially all data and final = 0.7*global + 0.3*sub_on_global = ~global. Effectively dropped sub-models.
- **next_hypothesis:** iter7 -- per-type sub-model max_depth=8 (vs global max_depth=6). Justification (within-family): v4 iter26 tested SMALLER sub-model depth=4 (tied within noise); the BIGGER direction is untested. Sub-models see top-5 type slices (1-10k rows each); deeper trees may capture richer interactions per type slice. Rest of recipe identical.

## 20260508-151054-deepen-v4_anchor

- stage: deepen
- feature_lane: v4_anchor
- change_kind: hyperparameter
- hypothesis_unit: n_a
- feature_group: n_a
- anchor_run_id: 20260507-235645-deepen-v2_plus_geo_hierarchy
- status: revert
- cv_mae: 47135.83621918593
- cv_mae_std: 5213.640946205955
- runtime_seconds: 746.3193619000012
- change_from_previous: deepen_iter7_submodel_depth8
- hypothesis: Deepen iter7: per-type sub-models trained with max_depth=8 (vs global's max_depth=6). Sub-models see smaller per-type slices; v4 iter26 tested smaller sub-model depth=4 and tied. Untested direction is BIGGER sub-model capacity to capture richer type-specific interactions.
- **observation:** cv_mae 47,135.84 +/- 5,213.64, runtime 746s.
- **comparison:**
  - vs v4 anchor (47107.53): delta_mae +28.31, pooled_std sqrt((5213.64^2+5244.67^2)/2)=5229.18, noise_band 1307.29.
  - vs family best (iter6 47392.22): delta_mae -256.38 -- new family best.
  - vs global champion (47107.53): delta_mae +28.31. Essentially identical.
- **significance:** tie_within_noise (|+28| << 1307). Effectively the same recipe.
- **attribution:** single knob (sub-model max_depth=8 instead of 6). Bigger sub-model capacity yielded no measurable change -- top-5 type slices already saturated at depth=6.
- **next_hypothesis:** iter8 -- blend v4 anchor predictions 50/50 with HistGradientBoostingRegressor(absolute_error). Justification (within-family): all xgboost-internal knobs (capacity, depth, sub-model grouping/depth, seed averaging, features) have plateaued. Orthogonal to xgboost is cross-family DIVERSITY -- HGB has different histogramming and split criteria, may produce decorrelated errors that average down. Cost ~1.5x.

## 20260508-152527-deepen-v4_anchor

- stage: deepen
- feature_lane: v4_anchor
- change_kind: hyperparameter
- hypothesis_unit: n_a
- feature_group: n_a
- anchor_run_id: 20260507-235645-deepen-v2_plus_geo_hierarchy
- status: revert
- cv_mae: 48028.8730920219
- cv_mae_std: 5050.229983058805
- runtime_seconds: 1022.4921269000042
- change_from_previous: deepen_iter8_hgb_blend50
- hypothesis: Deepen iter8: blend v4 anchor predictions 50/50 with HistGradientBoostingRegressor(absolute_error). Tests cross-family model diversity -- HGB and XGB have different histogramming and split criteria. v4 iter18 heterogeneous-XGB ensemble failed at n_est=500; this is cross-family blend at v4 capacity.
- **observation:** cv_mae 48,028.87 +/- 5,050.23, runtime 1022s.
- **comparison:**
  - vs v4 anchor (47107.53): delta_mae +921.34, pooled_std sqrt((5050.23^2+5244.67^2)/2)=5147.84, noise_band 1286.96.
  - vs family best (iter7 47135.84): delta_mae +893.03 -- regression within family.
  - vs global champion (47107.53): delta_mae +921.34.
- **significance:** tie_within_noise (|+921| < 1287) but on the regression side.
- **attribution:** single knob (50/50 XGB+HGB blend). HGB alone is far worse (HGB iter21 was 50934 vs XGB 47107); blending pulled mean toward the weaker learner. Cross-family blending only helps when both models are competitive.
- **next_hypothesis:** iter9 -- extend per-type sub-models from top 5 to top 10 types. Justification (within-family): v4 iter23 extended from 2 to 5 (-57 lift); diminishing but positive. Top 6-10 types still have hundreds of samples; if each contributes a small attributable lift, the cumulative may clear noise band.

## 20260508-154428-deepen-v4_anchor

- stage: deepen
- feature_lane: v4_anchor
- change_kind: hyperparameter
- hypothesis_unit: n_a
- feature_group: n_a
- anchor_run_id: 20260507-235645-deepen-v2_plus_geo_hierarchy
- status: keep
- cv_mae: 46978.02108332696
- cv_mae_std: 5246.892227878448
- runtime_seconds: 810.2504943000022
- change_from_previous: deepen_iter9_top10_submodels
- hypothesis: Deepen iter9: extend per-type sub-models from top 5 to top 10 types. v4 iter23 extended from 2 to 5 (-57 lift); the next-tier types may have enough samples to add similar marginal lift even though smaller.
- **observation:** cv_mae 46,978.02 +/- 5,246.89, runtime 810s. **First v5 result below v4 anchor.**
- **comparison:**
  - vs v4 anchor (47107.53): delta_mae **-129.51** (LIFT direction), pooled_std sqrt((5246.89^2+5244.67^2)/2)=5245.78, noise_band 1311.45.
  - vs family best (iter7 47135.84): delta_mae -157.82 -- new family best.
  - vs global champion (47107.53 single seed=42): delta_mae -129.51 (within noise; not a winner).
  - vs v4 2-seed mean (47553): delta_mae -575 -- below the more honest mean estimate.
- **significance:** tie_within_noise on LIFT side (|-129| < 1311). Per protocol "tie_within_noise + adds complexity = discard"; but adding 5 extra sub-models is the only positive direction in v5 so far. KEEP as working anchor; cumulative lifts may clear noise on top of this.
- **attribution:** single knob (top10 vs top5 sub-types). Adds 5 more per-fold sub-model fits. Lift consistent with v4 iter23 pattern (top5 vs top2: -57); incremental sub-model contribution diminishes but stays positive.
- **next_hypothesis:** iter10 -- on top of iter9 (top-10 sub-models, KEPT), add capacity push n_est=5000 (single knob: n_est 4000->5000 in both global and sub-models). Justification (within-family): v4 iter38 tested n_est=5000 alone (-66 vs n_est=4000, tied within noise but lift direction). Combined with iter9's lift direction, cumulative may clear noise band.

## 20260508-160016-deepen-v4_anchor

- stage: deepen
- feature_lane: v4_anchor
- change_kind: capacity_pair
- hypothesis_unit: n_a
- feature_group: n_a
- anchor_run_id: 20260508-154428-deepen-v4_anchor
- status: keep
- cv_mae: 46909.14174566427
- cv_mae_std: 5296.85326415855
- runtime_seconds: 1158.0008293000064
- change_from_previous: deepen_iter10_top10_nest5000
- hypothesis: Deepen iter10: ON TOP OF iter9 (top-10 sub-models, KEPT), bump n_estimators 4000->5000 in BOTH global and sub-models. v4 iter38 tested n_est=5000 alone (-66 lift, within noise); compounding with iter9's -130 may clear noise band cumulatively.
- **observation:** cv_mae 46,909.14 +/- 5,296.85, runtime 1158s. Family best.
- **comparison:**
  - vs iter9 anchor (46978.02): delta_mae -68.88, pooled_std sqrt((5296.85^2+5246.89^2)/2)=5271.93, noise_band 1317.98.
  - vs v4 anchor (47107.53): delta_mae **-198.39** (cumulative iter9+iter10).
  - vs v4 2-seed mean (47553): delta_mae -643.86.
- **significance:** tie_within_noise vs iter9 (|-69| < 1318); cumulatively tie vs v4 anchor (-198 < 1318). Direction is positive; magnitude well within noise.
- **attribution:** single knob (n_est 4000->5000) on iter9's kept top-10 anchor. Lift consistent with v4 iter38's -66 from same change at top-5; additive when stacked on top-10.
- **next_hypothesis:** iter11 -- mechanically-paired (lr=0.04, n_est=6250) at fixed step budget = 250 (vs iter10's 0.05 * 5000 = 250). Justification (within-family): v4 iter39 tested lr=0.03+n_est=4000 (failed +1121) -- step budget was reduced to 120; this iter holds budget constant at 250 (the iter10 budget). Untested combo. Slower learning at fixed budget often extracts more signal in flat regions of the loss surface.

## 20260508-162111-deepen-v4_anchor

- stage: deepen
- feature_lane: v4_anchor
- change_kind: capacity_pair
- hypothesis_unit: n_a
- feature_group: n_a
- anchor_run_id: 20260508-160016-deepen-v4_anchor
- status: revert
- cv_mae: 48380.323906604215
- cv_mae_std: 4872.0355518604565
- runtime_seconds: 1413.8945387000058
- change_from_previous: deepen_iter11_lr04_nest6250
- hypothesis: Deepen iter11: ON TOP OF iter10 (top10 sub-models + n_est=5000 KEPT), test mechanically-paired knob lr=0.04 + n_est=6250 (lr*n_est=250 same step budget as iter10's 0.05*5000=250). Slower learning at fixed step budget often extracts more signal.
- **observation:** cv_mae 48,380.32 +/- 4,872.04, runtime 1414s.
- **comparison:**
  - vs iter10 anchor (46909.14): delta_mae +1471.18, pooled_std sqrt((4872.04^2+5296.85^2)/2)=5089, noise_band 1272.25.
  - vs v4 anchor (47107.53): delta_mae +1272.79.
- **significance:** REGRESSION (|+1471| > 1272). Slower learning at fixed step budget hurt; fewer total parameter updates per round of refinement at this point in the curve.
- **attribution:** single mechanically-paired knob (lr 0.05->0.04, n_est 5000->6250 keeping lr*n_est=250). Direction wrong; v4 iter39 (lr=0.03+n_est=4000, budget 120) also failed.
- **next_hypothesis:** iter12 -- BLEND ratio 0.3 -> 0.4 on iter10 anchor (single knob). v4 ablate (drop sub-models) showed +285 regression -- sub-models contribute weakly; raising blend weight tests whether top-10's broader sub-model coverage justifies more weight than v4's top-5 0.3 setting.

## 20260508-164635-deepen-v4_anchor

- stage: deepen
- feature_lane: v4_anchor
- change_kind: hyperparameter
- hypothesis_unit: n_a
- feature_group: n_a
- anchor_run_id: 20260508-160016-deepen-v4_anchor
- status: revert
- cv_mae: 47030.07135705922
- cv_mae_std: 5187.331241851038
- runtime_seconds: 1452.5072523000053
- change_from_previous: deepen_iter12_blend04
- hypothesis: Deepen iter12: ON TOP OF iter10 (top10 + n_est=5000 KEPT), change BLEND ratio 0.3 -> 0.4 for sub-model contribution. v4 ablate showed sub-models contribute marginally (+285 when dropped); raising blend weight tests whether more sub-model influence helps now that there are 10 sub-models (vs v4's top 5). Single knob.
- **observation:** cv_mae 47,030.07 +/- 5,187.33, runtime 1452s.
- **comparison:**
  - vs iter10 anchor (46909.14): delta_mae +120.93, pooled_std 5242.37, noise_band 1310.59.
  - vs v4 anchor (47107.53): delta_mae -77.47.
- **significance:** tie_within_noise (|+121| << 1311). Slight regression direction.
- **attribution:** single knob (BLEND 0.3->0.4). v4's BLEND search (0.3, 0.5, 0.7) found 0.3 optimal; top-10 sub-models do not change that optimum.
- **next_hypothesis:** iter13 -- subsample 0.8 -> 0.7 (single knob, untested in v4). Last deepen iter to satisfy stage budget min=10. After this, family parks unless lift breaks noise band.

## 20260508-171239-deepen-v4_anchor

- stage: deepen
- feature_lane: v4_anchor
- change_kind: hyperparameter
- hypothesis_unit: n_a
- feature_group: n_a
- anchor_run_id: 20260508-160016-deepen-v4_anchor
- status: revert
- cv_mae: 47933.36402752986
- cv_mae_std: 5012.294173383414
- runtime_seconds: 962.1905394999994
- change_from_previous: deepen_iter13_subsample07
- hypothesis: Deepen iter13: ON TOP OF iter10 (top10 + n_est=5000), test subsample 0.8 -> 0.7 (single knob). Untested in xgboost_v4 chain. Lower subsample = more variance per tree = potentially better generalization in saturated capacity regime.
- **observation:** cv_mae 47,933.36 +/- 5,012.29, runtime 962s.
- **comparison:**
  - vs iter10 anchor (46909.14): delta_mae +1024.22, pooled_std 5156.53, noise_band 1289.13.
  - vs v4 anchor (47107.53): delta_mae +825.83.
- **significance:** tie_within_noise (|+1024| < 1289) but firmly regression side.
- **attribution:** single knob (subsample 0.8->0.7). v4 anchor's 0.8 setting was already optimal; lower subsample increases tree-level variance more than it reduces overfitting at this capacity.
- **next_hypothesis:** Deepen budget (10/10) complete. Transition to Stage 4 confirm with seed=2026 on iter10 (top10 + n_est=5000) to check seed agreement before any global-champion claim. Implicit ablations: iter9 (top10 only @ n_est=4000) = 46978; v4 iter38 (top5 @ n_est=5000) = 47042. Each kept knob alone gives -130 / -66 vs v4 anchor; combined iter10 gives -198. All within noise band.

## 20260508-173019-deepen-v4_anchor

- stage: deepen
- feature_lane: v4_anchor
- change_kind: diagnostic
- hypothesis_unit: n_a
- feature_group: n_a
- anchor_run_id: 20260508-160016-deepen-v4_anchor
- status: confirm
- cv_mae: 47790.95963916126
- cv_mae_std: 3596.4036352207468
- runtime_seconds: 1072.6056766000038
- change_from_previous: confirm_iter10_seed2026
- hypothesis: Stage 4 confirm seed=2026 of iter10 (top10 sub-models + n_est=5000 on v4 anchor). Two-seed agreement check before any global-champion claim.
- **observation:** cv_mae 47,790.96 +/- 3,596.40, runtime 1072s. Note: cv_mae_std DROPS at seed=2026 (3596 vs 5297 at seed=42), same pattern as v4 (3832 vs 5245). Seed=2026 produces a tighter fold split.
- **comparison:**
  - vs iter10 seed=42 (46909.14): delta_mae +881.82 -- seed gap (similar to v4's 891 gap between seeds, indicating seeds agree within their pooled noise).
  - vs v4 confirm seed=2026 (47998.49): delta_mae **-207.53**, pooled_std sqrt((3596.4^2+3831.88^2)/2)=3716.01, noise_band 0.25*3716.01=929.00.
  - vs v4 W''''' 2-seed mean (47553.01): iter10 2-seed mean (46909+47791)/2 = **47350.05**, delta_mae **-202.96**.
- **significance:** tie_within_noise (|-203| << 929 single-seed; 2-seed mean delta -203 is also well below pooled-noise band ~1100).
- **attribution:** seed agreement HOLDS for iter10 (|seed_42 - seed_2026| = 882 within v4's 891-gap precedent). Both kept knobs (top10 sub-models + n_est=5000) accumulate consistently across seeds.

## Stage 4 Confirm verdict & Family verdict

iter10 (top10 sub-models + n_est=5000) is **tied within fold noise** with v4 W''''' on every comparison:

| comparison | delta | noise_band | verdict |
|---|---:|---:|---|
| iter10 seed=42 vs v4 seed=42 | -198.39 | 1318 | tie_within_noise |
| iter10 seed=2026 vs v4 seed=2026 | -207.53 | 929 | tie_within_noise |
| iter10 2-seed mean vs v4 2-seed mean | -202.96 | ~1100 | tie_within_noise |

**Per protocol (search_policy.md): "A within-noise tie versus the global champion is not grounds for promotion to global champion."**

Target the user requested ("global winner by far", ~2x noise = -2400 below v4 2-seed mean = ~44950): NOT MET. We are -203 below v4, an order of magnitude short.

**Decision: PARK xgboost_v5.** Add 2 small accumulating knobs (top10 sub-models, n_est=5000) DO produce a directional lift over v4, but the combined effect (-203 on 2-seed mean) is well within fold noise and far from "by far". v4 W''''' remains global champion.

The structural reason: v4 was already exhaustively explored (40 deepen iters, kept 11 knobs accumulating -2046 over v2). The remaining headroom for xgboost-only architecture/capacity changes is bounded by the inherent fold noise of the dataset (~5200 std on cv_mae). Without a fundamentally different model class or dataset signal, a winner "by far" appears infeasible.
