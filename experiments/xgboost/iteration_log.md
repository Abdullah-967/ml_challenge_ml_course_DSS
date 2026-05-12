# xgboost Iteration Log

Append-only. One block per reflected canonical CV run.

Required fields per entry: stage, change_from_previous, hypothesis, observation, comparison, significance, attribution, next_hypothesis.

## 20260506-220015-smoke-all_numeric

- stage: smoke
- feature_lane: all_numeric
- status: keep
- cv_mae: 53600.062606851476
- cv_mae_std: 4575.502188530879
- runtime_seconds: 39.73877110000467
- change_from_previous: single_knob=all_numeric
- hypothesis: smoke test for xgboost using all_numeric
- observation: First xgboost run; reg:absoluteerror + tree_method=hist on 35+ numeric/bool columns runs in ~40s. Required excluding parcel_ids/transferred_parcel_ids (string ID concatenations that coerce to ~1e259) and replacing inf->NaN.
- comparison: First family run -> sets family best at 53600.06. Cross-family reference: HGB iter2 with absolute_error on the same all_numeric scope was 56069.80 -> xgboost beats matched HGB lane by 2469.74 (well above noise).
- significance: No prior xgboost run, so pooled-std rule does not apply within family. Cross-family delta (-2469.74) is roughly 0.5x pooled std (~4683) -> meaningful, not within noise.
- attribution: one-knob work item; verify no bundled changes before promotion.
- next_hypothesis: Add low-cardinality cats (property_type, transaction_type) via XGBoost native categorical support to test whether basic cats add lift at parity model.

## 20260506-220906-smoke-numeric_plus_basic_cats

- stage: smoke
- feature_lane: numeric_plus_basic_cats
- status: keep
- cv_mae: 52771.658732630705
- cv_mae_std: 4871.868458665871
- runtime_seconds: 57.295557599994936
- change_from_previous: single_knob=numeric_plus_basic_cats
- hypothesis: smoke test for xgboost adding low-cardinality categoricals via XGBoost native cat support
- observation: Adding property_type (25 cats) + transaction_type (6 cats) via enable_categorical=True moved CV MAE down 828; runtime bumped 17s (40 -> 57). Reflector marked status=keep, but the gain is statistically a tie (see significance).
- comparison: vs lane1 family best 53600.06 -> -828.40. vs HGB iter6 (which added commune_codes+property_type as native cats and got 52355.69) -> +416 (xgboost slightly worse, but lanes differ: HGB iter6 included commune_codes which is the geo_signal feature here).
- significance: Pooled std vs lane1 = sqrt((4575.50^2 + 4871.87^2)/2) ~= 4726. Noise threshold (0.25 x pooled) ~= 1182. |Delta| 828 < 1182 -> WITHIN NOISE. This is a tie, not a real win, despite reflector tag.
- attribution: one-knob work item; verify no bundled changes before promotion.
- next_hypothesis: Switch lane to geo_signal (commune_codes + cadastral_sections as native cats) to capture per-commune price level, the strongest known signal from HGB experience.

## 20260506-221254-smoke-geo_signal

- stage: smoke
- feature_lane: geo_signal
- status: keep
- cv_mae: 51530.01409025637
- cv_mae_std: 5125.226149662434
- runtime_seconds: 38.719082399999024
- change_from_previous: single_knob=geo_signal
- hypothesis: smoke test for xgboost adding commune_codes + cadastral_sections as native cats
- observation: geo_signal lane (numeric + commune_first 103 cats + cadastral_first letter cats, dropping property_type/transaction_type) cut CV MAE to 51530.01 in 38.7s. dept/region collapse to single value in this dataset, so commune is the only meaningful geographic granularity.
- comparison: vs lane2 family best 52771.66 -> -1241.65 (sits right at the noise threshold of ~1250, statistically tied). vs lane1 53600.06 -> -2070.05 (real improvement). vs global best HGB iter21 50934.78 -> +595 (xgboost geo_signal smoke is a statistical tie with the HGB champion despite no tuning).
- significance: vs lane2: pooled std ~= 5000, threshold ~= 1250, |Delta| 1241.65 < 1250 -> WITHIN NOISE (just barely). vs lane1: pooled ~= 4856, threshold ~= 1214, |Delta| 2070 > 1214 -> REAL WIN. vs HGB iter21: pooled ~= 4965, threshold ~= 1241, |Delta| 595 << 1241 -> tie with global champion.
- attribution: one-knob work item; lane-level scope swap (replaced lane2 cats with geo cats), not cumulative.
- next_hypothesis: Stage 1 gate satisfied (3 lanes). Best lane = geo_signal. Enter Stage 2 (deepen) with single-knob feature additions on geo_signal: derived ratios, missingness indicators, or fold-safe commune target encoding. Track 10+ deepen iters before tune.

## 20260506-221828-deepen-geo_signal

- stage: deepen
- feature_lane: geo_signal
- status: keep (reflector tag) — within-noise tie, NOT an improvement
- cv_mae: 51667.25117228369
- cv_mae_std: 5086.716154603519
- runtime_seconds: 38.78202709999459
- change_from_previous: single_knob=log1p_target
- hypothesis: log1p target should help (mirrors HGB iter21's winning move)
- observation: log1p target slightly hurt xgboost (51667 vs 51530, +137). HGB iter21 saw a real lift; xgboost with reg:absoluteerror does not. Likely because absolute_error in log space != absolute_error in original space, so the loss-target alignment broke.
- comparison: vs smoke geo_signal best 51530.01 -> +137.24. vs HGB iter21 50934.78 -> +732.
- significance: pooled std ~= 5106, threshold ~= 1276. |Delta| 137 << 1276 -> WITHIN NOISE. Best run stays at smoke geo_signal.
- attribution: one-knob work item.
- next_hypothesis: REVERT log1p (USE_LOG_TARGET=False). Try derived ratios (built_area_per_premise, land_per_lot, commercial_share, apt_share) on top of smoke geo_signal recipe.

## 20260506-222118-deepen-geo_signal

- stage: deepen
- feature_lane: geo_signal
- status: keep (lowest MAE so far) — within-noise tie vs smoke geo_signal
- cv_mae: 51520.49855333015
- cv_mae_std: 5075.277583572404
- runtime_seconds: 41.16572129999986
- change_from_previous: single_knob=derived_ratios (built_per_premise, land_per_lot, commercial_share, apt_share, houses_per_premise)
- hypothesis: structural ratios should add domain signal beyond raw counts
- observation: 5 derived ratios moved CV MAE -9.5 in 41s; runtime barely affected. Marginal but in the right direction.
- comparison: vs smoke geo_signal best 51530.01 -> -9.51. vs HGB iter21 50934.78 -> +586.
- significance: pooled std ~= 5100, threshold ~= 1275. |Delta| 9.5 << 1275 -> WITHIN NOISE. Treat as tie; keep ratios in recipe since they don't hurt and are interpretable.
- attribution: one-knob: ratios only (log1p reverted from iter1).
- next_hypothesis: Add presence_flags (has_apt, has_house, has_land, has_commercial, has_built) as int8 indicators. Trees may benefit from explicit booleans even though they could split on >0 directly.

## 20260506-222345-deepen-geo_signal

- stage: deepen
- feature_lane: geo_signal
- status: keep (reflector tag) — within-noise regression, REVERTED in next iter
- cv_mae: 51548.83391566288
- cv_mae_std: 5089.913847107262
- runtime_seconds: 36.40124580000702
- change_from_previous: single_knob=presence_flags (has_apt, has_house, has_land, has_commercial, has_built)
- hypothesis: explicit boolean indicators may help trees split on availability vs zero
- observation: presence flags hurt by +28 MAE; trees apparently already capture "x > 0" via splits, so explicit booleans are redundant noise.
- comparison: vs prev best 51520.50 (iter2 ratios) -> +28.33. vs HGB iter21 50934.78 -> +614.
- significance: pooled std ~= 5083, threshold ~= 1271. |Delta| 28 << 1271 -> WITHIN NOISE; small regression, no real signal.
- attribution: one-knob: presence flags only on top of iter2.
- next_hypothesis: REVERT presence flags. Try log1p of skewed numerics (built_area, land_area, apartment_area, house_area) as additional features. Note: trees are scale-invariant so this is unlikely to help, but worth ruling out.

## 20260506-222515-deepen-geo_signal

- stage: deepen
- feature_lane: geo_signal
- status: keep (reflector tag) — within-noise regression, REVERTED
- cv_mae: 51638.88023045145
- cv_mae_std: 4995.880754055436
- runtime_seconds: 47.52744140000141
- change_from_previous: single_knob=log_skewed_numerics (log1p of built_area, land_area, apartment_area, house_area as added features)
- hypothesis: log-scaled inputs may give trees finer split granularity on heavy tails
- observation: log-skewed cols hurt by +118; confirmed trees are scale-invariant -- adding log versions adds redundant features that XGBoost has to scan for splits, slightly slowing convergence.
- comparison: vs prev best 51520.50 (iter2) -> +118.38. vs HGB iter21 50934.78 -> +704.
- significance: pooled std ~= 5036, threshold ~= 1259. |Delta| 118 << 1259 -> WITHIN NOISE.
- attribution: one-knob: log_skewed only on top of iter2.
- next_hypothesis: REVERT log_skewed. Add transaction_date as ordinal day-of-epoch feature; year/month already in numeric set but full-resolution date may capture intra-year price drift.

## 20260506-222709-deepen-geo_signal

- stage: deepen
- feature_lane: geo_signal
- status: keep (lowest MAE so far in deepen) — within-noise tie vs iter2
- cv_mae: 51386.02233286221
- cv_mae_std: 5087.123976717962
- runtime_seconds: 51.58695670000452
- change_from_previous: single_knob=date_ordinal (days since 2014-01-01)
- hypothesis: full-resolution date ordinal captures price drift not visible in year/month split features
- observation: date_ordinal moved CV MAE -134.48 in 51.6s; new family low though within noise. Reasonable: data spans 2014-2021, so price trends over 8 years are continuous. Kept in recipe.
- comparison: vs prev best 51520.50 (iter2) -> -134.48. vs HGB iter21 50934.78 -> +451.
- significance: pooled std ~= 5081, threshold ~= 1270. |Delta| 134 << 1270 -> WITHIN NOISE; treat as tie but keep since lowest.
- attribution: one-knob: date_ordinal only on top of iter2 (log_skewed reverted).
- next_hypothesis: Add room count + area aggregates (total_rooms_apt, total_rooms_house, total_area_apt_check, total_area_house_check). Trees may save effort if explicit totals are pre-computed.

## 20260506-222906-deepen-geo_signal

- stage: deepen
- feature_lane: geo_signal
- status: keep (reflector tag) — within-noise regression, REVERTED
- cv_mae: 51551.79729666093
- cv_mae_std: 4968.9550815270095
- runtime_seconds: 36.07305400000769
- change_from_previous: single_knob=room_aggregates (total_rooms_apt, total_rooms_house, total_area_apt_check, total_area_house_check)
- hypothesis: pre-computed totals save trees from learning sums internally
- observation: Aggregates regressed +166; trees handle linear sums via additive splits well already, so explicit totals add redundancy without lift.
- comparison: vs prev best 51386.02 (iter5) -> +165.78. vs HGB iter21 50934.78 -> +617.
- significance: pooled std ~= 5028, threshold ~= 1257. |Delta| 166 << 1257 -> WITHIN NOISE.
- attribution: one-knob: aggregates on top of iter5.
- next_hypothesis: REVERT aggregates. Try avg_area_per_apt, avg_area_per_house (density features).

## 20260506-223101-deepen-geo_signal

- stage: deepen
- feature_lane: geo_signal
- status: keep (reflector tag) — within-noise regression, REVERTED
- cv_mae: 51471.74678372618
- cv_mae_std: 5093.853821584659
- runtime_seconds: 36.188519400006044
- change_from_previous: single_knob=avg_area_per_unit (avg_area_per_apt, avg_area_per_house)
- hypothesis: per-unit area density may beat raw totals as a price-per-unit signal
- observation: avg-area features regressed +85; trees already approximate area/count splits via co-occurring numeric splits. Net loss.
- comparison: vs prev best 51386.02 (iter5) -> +85.72. vs HGB iter21 50934.78 -> +537.
- significance: pooled std ~= 5090, threshold ~= 1273. |Delta| 86 << 1273 -> WITHIN NOISE.
- attribution: one-knob: avg-area features on top of iter5.
- next_hypothesis: REVERT avg-area. Try fold-safe smoothed commune target encoding (smooth=20). Explicit per-commune mean target may help where the commune categorical alone underfits.

## 20260506-223309-deepen-geo_signal

- stage: deepen
- feature_lane: geo_signal
- status: keep (reflector tag) — within-noise regression, REVERTED
- cv_mae: 51665.09853885014
- cv_mae_std: 4856.254048090444
- runtime_seconds: 52.57561930001248
- change_from_previous: single_knob=commune_target_enc_smooth20 (mean(target) per commune from train fold only, smoothed with 20*global_mean)
- hypothesis: smoothed per-commune target mean may capture price level better than the native categorical alone
- observation: target encoding regressed +279; commune_first as a native cat already exposes per-commune patterns to XGBoost, so adding a numerical mean-target is a near-duplicate signal that confuses early splits.
- comparison: vs prev best 51386.02 (iter5) -> +279.08. vs HGB iter21 50934.78 -> +730.
- significance: pooled std ~= 4972, threshold ~= 1243. |Delta| 279 << 1243 -> WITHIN NOISE.
- attribution: one-knob: target_enc on top of iter5; encoding fitted only on train split (fold-safe).
- next_hypothesis: REVERT target_enc. Try dropping sparse per-room/per-area columns (20 cols mostly zero) to reduce feature noise.

## 20260506-223517-deepen-geo_signal

- stage: deepen
- feature_lane: geo_signal
- status: keep (reflector tag) — within-noise regression, REVERTED
- cv_mae: 51764.760431975985
- cv_mae_std: 4898.769151304853
- runtime_seconds: 32.89937490000739
- change_from_previous: single_knob=drop_per_room_cols (removed 20 per-room count + per-room area columns >85% zero)
- hypothesis: highly sparse columns may be adding more noise than signal; pruning should help
- observation: pruning regressed +379; despite being sparse, these columns DO carry residual signal for trees on the populated rows. Subsample/colsample already manage their cost.
- comparison: vs prev best 51386.02 (iter5) -> +378.74. vs HGB iter21 50934.78 -> +830.
- significance: pooled std ~= 4994, threshold ~= 1248. |Delta| 379 << 1248 -> WITHIN NOISE but clear directional regression.
- attribution: one-knob: drop_per_room on top of iter5 (after target_enc revert).
- next_hypothesis: REVERT drop_per_room. Re-add property_type as a third native categorical (in addition to commune_first + cadastral_first) -- these were dropped during the smoke geo_signal lane swap, but property_type carried real signal in HGB iter6.

## 20260506-223720-deepen-geo_signal

- stage: deepen
- feature_lane: geo_signal
- status: keep — NEW FAMILY BEST; statistical tie with global champion HGB iter21
- cv_mae: 50957.359509219066
- cv_mae_std: 5039.36687295536
- runtime_seconds: 40.64352939999662
- change_from_previous: single_knob=property_type_cat (added property_type as third native categorical alongside commune_first and cadastral_first)
- hypothesis: property_type was helpful in HGB iter6 (lane2 smoke for xgboost was numeric+property+transaction = 52771); on top of geo_signal+ratios+date it should add complementary signal trees can't infer from area/count alone
- observation: property_type cat dropped CV MAE -428.66 to 50957.36, the biggest lift in deepen so far. This is the strongest feature signal we have found for xgboost. Runtime stable at 40.6s.
- comparison: vs prev best 51386.02 (iter5) -> -428.66. vs HGB iter21 50934.78 -> +22.58 (essentially identical, statistical tie with global champion).
- significance: pooled std ~= 5063, threshold ~= 1266. |Delta| 429 < 1266 -> within noise vs iter5; vs HGB iter21 |Delta|=22.58 << 1266 -> tie. Best by lowest MAE.
- attribution: one-knob: property_type cat on top of iter5 recipe (commune_first + cadastral_first + property_type as native cats; numeric all_numeric + ratios + date_ordinal).
- next_hypothesis: STAGE 2 GATE SATISFIED (10 deepen iters). Best xgboost recipe = geo_signal + ratios + date_ordinal + property_type_cat. Enter Stage 3 (tune): single-knob hyperparameter sweeps starting with (lr=0.025, n_est=1000), then max_depth, then min_child_weight, then subsample/colsample, then reg_lambda, etc. 10+ iters needed.

## 20260506-224330-deepen-geo_signal

- stage: tune
- feature_lane: geo_signal
- status: keep
- cv_mae: 50991.88965467175
- cv_mae_std: 5083.452934073871
- runtime_seconds: 67.0195243999915
- change_from_previous: single_knob=lr025_nest1000
- hypothesis: tune iter1: lr=0.025, n_est=1000
- observation: TODO: interpret fold/runtime signal before next action.
- comparison: TODO: compare against previous, family best, and global best.
- significance: TODO: apply pooled-std noise rule.
- attribution: one-knob work item; verify no bundled changes before promotion.
- next_hypothesis: TODO: one-knob next action or gate decision.

## 20260506-224614-deepen-geo_signal

- stage: tune
- feature_lane: geo_signal
- status: keep
- cv_mae: 50242.19529221515
- cv_mae_std: 4836.676870755888
- runtime_seconds: 39.57568660000106
- change_from_previous: single_knob=max_depth5
- hypothesis: tune iter2: max_depth=5
- observation: TODO: interpret fold/runtime signal before next action.
- comparison: TODO: compare against previous, family best, and global best.
- significance: TODO: apply pooled-std noise rule.
- attribution: one-knob work item; verify no bundled changes before promotion.
- next_hypothesis: TODO: one-knob next action or gate decision.

## 20260506-224823-deepen-geo_signal

- stage: tune
- feature_lane: geo_signal
- status: keep
- cv_mae: 49685.49644571084
- cv_mae_std: 4670.674481579977
- runtime_seconds: 68.55342130000645
- change_from_previous: single_knob=max_depth6
- hypothesis: tune iter3: max_depth=6
- observation: TODO: interpret fold/runtime signal before next action.
- comparison: TODO: compare against previous, family best, and global best.
- significance: TODO: apply pooled-std noise rule.
- attribution: one-knob work item; verify no bundled changes before promotion.
- next_hypothesis: TODO: one-knob next action or gate decision.

## 20260506-225731-deepen-geo_signal

- stage: tune
- feature_lane: geo_signal
- status: keep
- cv_mae: 50082.47997755841
- cv_mae_std: 4496.452224992034
- runtime_seconds: 119.80705620000663
- change_from_previous: single_knob=mcw3
- hypothesis: tune iter4: min_child_weight=3
- observation: TODO: interpret fold/runtime signal before next action.
- comparison: TODO: compare against previous, family best, and global best.
- significance: TODO: apply pooled-std noise rule.
- attribution: one-knob work item; verify no bundled changes before promotion.
- next_hypothesis: TODO: one-knob next action or gate decision.

## 20260506-230036-deepen-geo_signal

- stage: tune
- feature_lane: geo_signal
- status: keep
- cv_mae: 49748.41288823503
- cv_mae_std: 4753.791470983807
- runtime_seconds: 63.95837659999961
- change_from_previous: single_knob=mcw10
- hypothesis: tune iter5: min_child_weight=10
- observation: TODO: interpret fold/runtime signal before next action.
- comparison: TODO: compare against previous, family best, and global best.
- significance: TODO: apply pooled-std noise rule.
- attribution: one-knob work item; verify no bundled changes before promotion.
- next_hypothesis: TODO: one-knob next action or gate decision.

## 20260506-230230-deepen-geo_signal

- stage: tune
- feature_lane: geo_signal
- status: keep
- cv_mae: 50066.92214053607
- cv_mae_std: 4858.944692183741
- runtime_seconds: 66.3244657000032
- change_from_previous: single_knob=subsample07
- hypothesis: tune iter6: subsample=0.7
- observation: TODO: interpret fold/runtime signal before next action.
- comparison: TODO: compare against previous, family best, and global best.
- significance: TODO: apply pooled-std noise rule.
- attribution: one-knob work item; verify no bundled changes before promotion.
- next_hypothesis: TODO: one-knob next action or gate decision.

## 20260506-230431-deepen-geo_signal

- stage: tune
- feature_lane: geo_signal
- status: keep
- cv_mae: 49679.53033304195
- cv_mae_std: 4784.962856554062
- runtime_seconds: 55.61565710000286
- change_from_previous: single_knob=subsample09
- hypothesis: tune iter7: subsample=0.9
- observation: TODO: interpret fold/runtime signal before next action.
- comparison: TODO: compare against previous, family best, and global best.
- significance: TODO: apply pooled-std noise rule.
- attribution: one-knob work item; verify no bundled changes before promotion.
- next_hypothesis: TODO: one-knob next action or gate decision.

## 20260506-230733-deepen-geo_signal

- stage: tune
- feature_lane: geo_signal
- status: keep
- cv_mae: 49632.105104875314
- cv_mae_std: 4686.83745309055
- runtime_seconds: 45.41729369999666
- change_from_previous: single_knob=colsample07
- hypothesis: tune iter8: colsample_bytree=0.7
- observation: TODO: interpret fold/runtime signal before next action.
- comparison: TODO: compare against previous, family best, and global best.
- significance: TODO: apply pooled-std noise rule.
- attribution: one-knob work item; verify no bundled changes before promotion.
- next_hypothesis: TODO: one-knob next action or gate decision.

## 20260506-230911-deepen-geo_signal

- stage: tune
- feature_lane: geo_signal
- status: keep
- cv_mae: 49546.39624027418
- cv_mae_std: 4706.334572437609
- runtime_seconds: 45.63767419999931
- change_from_previous: single_knob=reg_lambda2
- hypothesis: tune iter9: reg_lambda=2.0
- observation: TODO: interpret fold/runtime signal before next action.
- comparison: TODO: compare against previous, family best, and global best.
- significance: TODO: apply pooled-std noise rule.
- attribution: one-knob work item; verify no bundled changes before promotion.
- next_hypothesis: TODO: one-knob next action or gate decision.

## 20260506-231056-deepen-geo_signal

- stage: tune
- feature_lane: geo_signal
- status: keep
- cv_mae: 49603.606578685736
- cv_mae_std: 4466.794159780608
- runtime_seconds: 46.17833080000128
- change_from_previous: single_knob=reg_lambda4
- hypothesis: tune iter10: reg_lambda=4.0
- observation: TODO: interpret fold/runtime signal before next action.
- comparison: TODO: compare against previous, family best, and global best.
- significance: TODO: apply pooled-std noise rule.
- attribution: one-knob work item; verify no bundled changes before promotion.
- next_hypothesis: TODO: one-knob next action or gate decision.

## 20260506-232130-deepen-geo_signal

- stage: ablate
- feature_lane: geo_signal
- status: ablate
- cv_mae: 50939.81237781404
- cv_mae_std: 5058.366401247195
- runtime_seconds: 37.56848639999225
- change_from_previous: ablate_c1=max_depth4
- hypothesis: ablate c1: drop max_depth=6 (revert to 4)
- observation: TODO: interpret fold/runtime signal before next action.
- comparison: TODO: compare against previous, family best, and global best.
- significance: TODO: apply pooled-std noise rule.
- attribution: one-knob work item; verify no bundled changes before promotion.
- next_hypothesis: TODO: one-knob next action or gate decision.

## 20260506-232300-deepen-geo_signal

- stage: ablate
- feature_lane: geo_signal
- status: ablate
- cv_mae: 49827.172864537264
- cv_mae_std: 4691.048785750445
- runtime_seconds: 45.97442879999289
- change_from_previous: ablate_c2=subsample08
- hypothesis: ablate c2: drop subsample=0.9 (revert to 0.8)
- observation: TODO: interpret fold/runtime signal before next action.
- comparison: TODO: compare against previous, family best, and global best.
- significance: TODO: apply pooled-std noise rule.
- attribution: one-knob work item; verify no bundled changes before promotion.
- next_hypothesis: TODO: one-knob next action or gate decision.

## 20260506-232455-deepen-geo_signal

- stage: ablate
- feature_lane: geo_signal
- status: ablate
- cv_mae: 49676.07383100182
- cv_mae_std: 4739.437727814112
- runtime_seconds: 45.413516500004334
- change_from_previous: ablate_c3=colsample08
- hypothesis: ablate c3: drop colsample=0.7 (revert to 0.8)
- observation: TODO: interpret fold/runtime signal before next action.
- comparison: TODO: compare against previous, family best, and global best.
- significance: TODO: apply pooled-std noise rule.
- attribution: one-knob work item; verify no bundled changes before promotion.
- next_hypothesis: TODO: one-knob next action or gate decision.

## 20260506-232747-deepen-geo_signal

- stage: ablate
- feature_lane: geo_signal
- status: ablate
- cv_mae: 49632.105104875314
- cv_mae_std: 4686.83745309055
- runtime_seconds: 45.31110880000051
- change_from_previous: ablate_c4=reg_lambda1
- hypothesis: ablate c4: drop reg_lambda=2.0 (revert to 1.0)
- observation: TODO: interpret fold/runtime signal before next action.
- comparison: TODO: compare against previous, family best, and global best.
- significance: TODO: apply pooled-std noise rule.
- attribution: one-knob work item; verify no bundled changes before promotion.
- next_hypothesis: TODO: one-knob next action or gate decision.

## ablation_summary -- after tune iter9

- **winner W:** 20260506-230911-deepen-geo_signal (tune iter9), cv_mae 49546.40 ± 4706.33
- **prior family best B:** 20260506-223720-deepen-geo_signal (deepen iter10), cv_mae 50957.36 ± 5039.37
- **changes from B to W (4 knobs):** c1 max_depth 4->6, c2 subsample 0.8->0.9, c3 colsample_bytree 0.8->0.7, c4 reg_lambda 1.0->2.0
- **LOO results (each = W minus c_i, vs W noise band ~1175-1221):**
  - W_minus_c1 (max_depth=4): 50939.81, +1393 -> drop HURTS (load-bearing)
  - W_minus_c2 (subsample=0.8): 49827.17, +281 -> tie (NOT load-bearing)
  - W_minus_c3 (colsample=0.8): 49676.07, +130 -> tie (NOT load-bearing)
  - W_minus_c4 (reg_lambda=1.0): 49632.11, +86 -> tie (NOT load-bearing)
- **load-bearing changes:** c1 (max_depth=6)
- **redundant changes:** c2 (subsample), c3 (colsample_bytree), c4 (reg_lambda)
- **harmful changes:** none
- **promoted recipe:** B + c1 = max_depth=6 only on top of deepen iter10 baseline. Equivalent to tune iter3 (49685.50) within noise of W. Simplest recipe within noise band.
- **decision:** promote simplified recipe; drop c2/c3/c4 from final.

## 20260506-233001-deepen-geo_signal

- stage: confirm
- feature_lane: geo_signal
- status: confirm
- cv_mae: 49827.4843764683
- cv_mae_std: 4929.99839871536
- runtime_seconds: 43.69406130000425
- change_from_previous: confirm_seed2026
- hypothesis: confirm seed=2026: promoted recipe (max_depth=6 only)
- observation: TODO: interpret fold/runtime signal before next action.
- comparison: TODO: compare against previous, family best, and global best.
- significance: TODO: apply pooled-std noise rule.
- attribution: one-knob work item; verify no bundled changes before promotion.
- next_hypothesis: TODO: one-knob next action or gate decision.

## 20260512-105219-deepen-geo_signal_plus_transaction_type

- stage: deepen
- feature_lane: geo_signal_plus_transaction_type
- change_kind: feature
- hypothesis_unit: transaction_type_category
- feature_group: property_transaction
- anchor_run_id: 20260506-233001-deepen-geo_signal
- status: keep
- cv_mae: 49486.34437710626
- cv_mae_std: 4818.053408615316
- runtime_seconds: 51.525845299998764
- change_from_previous: single_knob=transaction_type_cat
- hypothesis: New xgboost round: add transaction_type as a single native categorical feature on top of the promoted geo_signal recipe.
- observation: transaction_type as a native categorical lowered raw MAE to 49486.34, with runtime increasing modestly to 51.53s.
- comparison: vs confirmed promoted anchor 20260506-233001 (49827.48 +/- 4929.99), delta_mae = -341.14; pooled_std = 4874.35; noise_band = 1218.59.
- significance: tie_within_noise; raw improvement is smaller than the pooled-std noise band, and the change adds one categorical feature.
- attribution: one-knob work item; verify no bundled changes before promotion.
- next_hypothesis: do not promote from this run alone; either confirm only if this feature becomes part of a stronger path, or continue with another single feature/preprocessing knob.
