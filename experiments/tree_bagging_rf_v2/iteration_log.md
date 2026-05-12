# tree_bagging_rf_v2 Iteration Log

Append-only. One block per canonical CV run. See the bundled `plugins/model-family-mae/references/reflection_protocol.md`.

Required metadata per entry: stage, change_kind, hypothesis_unit, feature_group, anchor_run_id, change_from_previous, hypothesis, observation, comparison, significance, attribution, next_hypothesis.

## 20260508-222002-smoke-v1_anchor_plus_built_rel_type

- stage: smoke
- feature_lane: v1_anchor_plus_built_rel_type
- change_kind: feature
- hypothesis_unit: built_rel_type
- feature_group: derived_ratios
- anchor_run_id: n/a
- status: keep
- cv_mae: 50565.974406053036
- cv_mae_std: 4813.843905796193
- runtime_seconds: 222.44242870000016
- change_from_previous: single_knob=built_rel_type
- hypothesis: v2 Smoke lane A: v1 promoted recipe + fold-safe built_rel_type = built_area / mean(built_area | property_type). Anchor = v1 promoted recipe (50663.64 seed=42). xgboost_v4 saw -245 from this exact unit.
- observation: Adding fold-safe built_rel_type on top of v1 promoted recipe moved CV MAE 50663.64 -> 50565.97 in 222s (run cost +26s on top of v1's 196s). Sets v2 family best, but only marginally.
- comparison: vs v1 anchor (50663.64 +/- 4749.88) -> -97.66. vs HGB iter21 global (50934.78 +/- 4795.53) -> -368.81. vs xgboost_v4 confirm (47998.49) -> +2567 (still real-gap behind).
- significance: pooled_std vs v1 = sqrt((4813.84^2+4749.88^2)/2) ~= 4781.95, threshold (0.25x) ~= 1195; |Delta| 98 << 1195 -> WITHIN NOISE; tie. vs HGB iter21: pooled ~= 4805, threshold ~= 1201; |Delta| 369 << 1201 -> tie. Lane A keeps the family rolling but isn't a real lift on its own.
- attribution: one-knob: built_rel_type fold-safe group stat added on top of v1 promoted recipe; model+seed unchanged.
- next_hypothesis: STAGE 1 GATE: 1/3 lanes done. Continue smoke. Lane B = v1_anchor + id_token_counts (parcel_count, transferred_count from comma-split lengths). Hypothesis: ID tokens encode multi-parcel structure; counts are bounded and proven helpful in xgboost_v5 lane.

## 20260508-222453-smoke-v1_anchor_plus_id_token_counts

- stage: smoke
- feature_lane: v1_anchor_plus_id_token_counts
- change_kind: feature
- hypothesis_unit: id_token_counts
- feature_group: id_derived
- anchor_run_id: n/a
- status: keep
- cv_mae: 50824.03756664677
- cv_mae_std: 4823.656796312327
- runtime_seconds: 234.95753129999503
- change_from_previous: single_knob=id_token_counts
- hypothesis: v2 Smoke lane B: v1 promoted recipe + parcel_id_count and transferred_parcel_id_count (comma-split lengths). Anchor v1 (50663.64). Hypothesis: ID tokens encode multi-parcel structure; bounded counts dodge the high-cardinality leakage warning in feature_search_space.md.
- observation: id_token_counts cumulative on v1 anchor moved CV MAE 50663.64 -> 50824.04 in 235s. Slight regression -- tokens count inflated noise rather than added structural signal. Family best stays with lane A (50565.97).
- comparison: vs v1 anchor (50663.64 +/- 4749.88) -> +160.40. vs lane A (50565.97 +/- 4813.84) -> +258.06. vs HGB iter21 (50934.78) -> -110.75.
- significance: pooled_std vs v1 = sqrt((4823.66^2+4749.88^2)/2) ~= 4786.85, threshold ~= 1197; |Delta| 160 << 1197 -> WITHIN NOISE; tie. Drop signal; lane A remains family best.
- attribution: one-knob: parcel_id_count + transferred_parcel_id_count added; OHE off, model+seed unchanged.
- next_hypothesis: STAGE 1 GATE: 2/3 lanes done. Lane C = v1_anchor + room_layout_distribution (num_apt_*_rooms, num_house_*_rooms, area_apt_*_rooms, area_house_*_rooms as one bundle). Hypothesis: room-layout signal might give RF the granular dwelling-mix info that aggregate counts miss.

## 20260508-223005-smoke-v1_anchor_plus_room_density

- stage: smoke
- feature_lane: v1_anchor_plus_room_density
- change_kind: feature
- hypothesis_unit: room_area_density_ratios
- feature_group: derived_ratios
- anchor_run_id: n/a
- status: keep
- cv_mae: 50575.66355554756
- cv_mae_std: 4719.43985934277
- runtime_seconds: 245.74999270000262
- change_from_previous: single_knob=room_area_density_ratios
- hypothesis: v2 Smoke lane C: v1 promoted recipe + 10 room density ratios (area_*/num_* per apt/house room bucket). Anchor v1 (50663.64). Hypothesis: per-room area is a per-dwelling size signal that aggregate built_area misses; protected against zero-num denominators.
- observation: 10 per-room density ratios cumulative on v1 anchor moved CV MAE 50663.64 -> 50575.66 in 246s. Tied with lane A; std slightly tighter (4719 vs lane A 4814).
- comparison: vs v1 anchor (50663.64 +/- 4749.88) -> -87.98. vs lane A best (50565.97 +/- 4813.84) -> +9.69. vs lane B (50824.04) -> -248.37. vs HGB iter21 (50934.78) -> -359.12.
- significance: pooled_std vs v1 = sqrt((4719.44^2+4749.88^2)/2) ~= 4734.66, threshold ~= 1184; |Delta| 88 << 1184 -> WITHIN NOISE; tie. vs lane A: pooled ~= 4767, threshold ~= 1192; |Delta| 10 << 1192 -> tie. All three smoke lanes are statistical ties.
- attribution: one-knob: 10 room density ratios added on top of v1 anchor; model+seed unchanged.
- next_hypothesis: STAGE 1 GATE SATISFIED (3/3 lanes). Best by lowest MAE = lane A (built_rel_type, 50565.97). Lanes A and C both moved family lower (-98, -88) within noise; lane B regressed +160. Enter Stage 2 deepen on top of lane A. First single-knob: built_per_land = built_area/land_area (xgboost_v4 saw -116 from this exact unit). Then room_area_density_ratios cumulative if built_per_land sticks; both small, both untried.

## 20260508-223520-deepen-lane_a_plus_built_per_land

- stage: deepen
- feature_lane: lane_a_plus_built_per_land
- change_kind: feature
- hypothesis_unit: built_per_land
- feature_group: derived_ratios
- anchor_run_id: 20260508-222002-smoke-v1_anchor_plus_built_rel_type
- status: discard
- cv_mae: 50941.89248977143
- cv_mae_std: 4770.09149264999
- runtime_seconds: 228.3066675000009
- change_from_previous: single_knob=built_per_land
- hypothesis: v2 Deepen iter1: lane A best (built_rel_type) + built_per_land = built_area/land_area cumulative. xgboost_v4 saw -116 from this exact unit.
- observation: built_per_land cumulative on lane A regressed CV MAE 50565.97 -> 50941.89 in 228s. Discard. Land-area zeros are common (commercial/agricultural records); the 1/0 pattern collapsed to NaN imputed at the median may have created a mode confused signal for RF.
- comparison: vs lane A (50565.97 +/- 4813.84) -> +375.92. vs v1 anchor (50663.64) -> +278.25. vs HGB iter21 (50934.78) -> +7.11.
- significance: pooled_std vs lane A = sqrt((4770.09^2+4813.84^2)/2) ~= 4791.99, threshold ~= 1198; |Delta| 376 << 1198 -> WITHIN NOISE; tie but trending wrong. Discard signal: built_per_land does not cumulate on lane A.
- attribution: one-knob: built_per_land = built_area/land_area added in derived ratios; revert.
- next_hypothesis: D2 = lane A + room_area_density_ratios cumulative (10 per-room area/num ratios). Lane C alone showed -88 vs anchor; combined lane A+C may push -180 if the two signals are non-redundant.

## 20260508-224002-deepen-lane_a_plus_room_density

- stage: deepen
- feature_lane: lane_a_plus_room_density
- change_kind: feature
- hypothesis_unit: room_area_density_ratios
- feature_group: derived_ratios
- anchor_run_id: 20260508-222002-smoke-v1_anchor_plus_built_rel_type
- status: discard
- cv_mae: 50705.800985136455
- cv_mae_std: 4712.801637229877
- runtime_seconds: 256.7480080999958
- change_from_previous: single_knob=room_density_cumulative
- hypothesis: v2 Deepen iter2: lane A (built_rel_type) + room_area_density_ratios cumulative. Lane C alone showed -88 vs anchor; cumulative may push -180 if the two signals are non-redundant.
- observation: room_density cumulative on lane A regressed CV MAE 50565.97 -> 50705.80 in 257s. Slight regression. The two signals (built_rel_type and per-room density) are partially redundant -- both encode size relative to a unit -- and stacking them adds noise at split selection time without new information.
- comparison: vs lane A (50565.97 +/- 4813.84) -> +139.83. vs v1 anchor (50663.64) -> +42.16. vs HGB iter21 (50934.78) -> -228.98.
- significance: pooled_std vs lane A = sqrt((4712.80^2+4813.84^2)/2) ~= 4763.62, threshold ~= 1191; |Delta| 140 << 1191 -> WITHIN NOISE; tie. Discard cumulative; lane A remains family best.
- attribution: one-knob: 10 room density ratios added on top of lane A; revert.
- next_hypothesis: D3 = ExtraTreesRegressor swap on lane A (replace RandomForestRegressor with ExtraTreesRegressor; same hyperparams). Random splits add variance reduction via averaging across less-correlated trees; might unlock a noise-aware lift where features alone plateaued.

## 20260508-224538-deepen-lane_a_extra_trees

- stage: deepen
- feature_lane: lane_a_extra_trees
- change_kind: hyperparameter
- hypothesis_unit: extra_trees_variant
- feature_group: structural_numeric
- anchor_run_id: 20260508-222002-smoke-v1_anchor_plus_built_rel_type
- status: discard
- cv_mae: 52459.34464378886
- cv_mae_std: 5079.249908112944
- runtime_seconds: 174.52049799999804
- change_from_previous: single_knob=extra_trees
- hypothesis: v2 Deepen iter3: ExtraTreesRegressor swap on lane A (built_rel_type). Same hyperparams (criterion=absolute_error, n_est=200, depth=18, mls=2, mf=0.4, bootstrap=False). Random splits trade some bias for less-correlated trees + variance reduction; might reach a noise-aware lift where features alone plateaued.
- observation: ExtraTrees swap regressed CV MAE 50565.97 -> 52459.34 in 175s (faster splits, but worse accuracy). The random-split bias dominates: with 0.4 max_features + bootstrap=False, RF was already de-correlating trees enough; ExtraTrees added more bias than variance gain.
- comparison: vs lane A (50565.97 +/- 4813.84) -> +1893.37. vs v1 anchor (50663.64) -> +1795.71. vs HGB iter21 (50934.78) -> +1524.57.
- significance: pooled_std vs lane A = sqrt((5079.25^2+4813.84^2)/2) ~= 4948.18, threshold ~= 1237; |Delta| 1893 > 1237 -> REAL regression. Discard ExtraTrees; revert to RF.
- attribution: one-knob: ExtraTreesRegressor swap, all other params unchanged.
- next_hypothesis: D4 = capacity bump n_est=200 -> n_est=400 on lane A with RF restored. Tune iter2 in v1 (n_est=500 with depth=None) was within noise; with depth=18 fixed and max_features=0.4, doubling trees may now show a real lift since each tree is shallower and deeper-correlated. Expected runtime ~444s = 7.4 min, within hard stop.

## 20260508-224945-deepen-lane_a_n_est_400

- stage: deepen
- feature_lane: lane_a_n_est_400
- change_kind: hyperparameter
- hypothesis_unit: n_est_400
- feature_group: structural_numeric
- anchor_run_id: 20260508-222002-smoke-v1_anchor_plus_built_rel_type
- status: discard
- cv_mae: 50660.718221578405
- cv_mae_std: 4806.290153603561
- runtime_seconds: 439.6818416000024
- change_from_previous: single_knob=n_est_400
- hypothesis: v2 Deepen iter4: capacity bump n_est 200 -> 400 on lane A. v1 tune iter2 (n_est=500) was within noise but with depth=None; depth=18 + bagging=False trees are smaller and benefit from more averaging.
- observation: n_est=400 cumulative on lane A moved CV MAE 50565.97 -> 50660.72 in 440s (2x runtime). Tied within noise; capacity scaling has saturated -- doubling trees does not extract additional signal at depth=18.
- comparison: vs lane A (50565.97 +/- 4813.84) -> +94.74. vs v1 anchor (50663.64) -> -2.92. vs HGB iter21 (50934.78) -> -274.06.
- significance: pooled_std vs lane A = sqrt((4806.29^2+4813.84^2)/2) ~= 4810.07, threshold ~= 1203; |Delta| 95 << 1203 -> WITHIN NOISE; tie. Capacity does not lift; revert to n_est=200.
- attribution: one-knob: n_est 200 -> 400, all other params and features unchanged.
- next_hypothesis: D5 = max_depth tuning. v1 ablate showed depth=None was harmful and depth=18 was the sweet spot, but exact local search beyond 18 wasn't done. Try max_depth=22 first (small step up); if it regresses or ties, drop to 16 next. With lane A's built_rel_type adding type-relative info, a slightly deeper tree may find the right interactions.

## 20260508-225821-deepen-lane_a_max_depth_22

- stage: deepen
- feature_lane: lane_a_max_depth_22
- change_kind: hyperparameter
- hypothesis_unit: max_depth_22
- feature_group: structural_numeric
- anchor_run_id: 20260508-222002-smoke-v1_anchor_plus_built_rel_type
- status: discard
- cv_mae: 50908.38698550225
- cv_mae_std: 4766.490908810376
- runtime_seconds: 240.79730750000454
- change_from_previous: single_knob=max_depth_22
- hypothesis: v2 Deepen iter5: max_depth 18 -> 22 on lane A. v1 ablate found depth=None harmful and depth=18 the sweet spot, but local search beyond 18 wasn't done. With built_rel_type now in the feature mix, a slightly deeper tree may capture missed type-x-size interactions.
- observation: max_depth=22 regressed CV MAE 50565.97 -> 50908.39 in 241s. Slight regression direction. Depth=18 is confirmed sweet spot; deeper trees overfit fold-internal noise.
- comparison: vs lane A (50565.97 +/- 4813.84) -> +342.41. vs v1 anchor (50663.64) -> +244.75. vs HGB iter21 (50934.78) -> -26.39.
- significance: pooled_std vs lane A = sqrt((4766.49^2+4813.84^2)/2) ~= 4790.21, threshold ~= 1198; |Delta| 342 << 1198 -> WITHIN NOISE; tie but trending wrong. Discard; revert depth to 18.
- attribution: one-knob: max_depth 18 -> 22, all other params and features unchanged.
- next_hypothesis: D6 = per-property-type sub-models architecture (xgboost_v4 winning move, -215 cumulative there). Train top-3 property type sub-RFs (n_est=80 each, same recipe) on type subset; blend 0.3 sub / 0.7 global. Lighter than xgboost_v4's 5-type variant to fit RF budget. Expected runtime ~3x = ~660s = ~11 min -- at hard stop boundary, will profile and trim if needed.

## 20260508-230358-deepen-lane_a_mls_1

- stage: deepen
- feature_lane: lane_a_mls_1
- change_kind: hyperparameter
- hypothesis_unit: min_samples_leaf_1
- feature_group: structural_numeric
- anchor_run_id: 20260508-222002-smoke-v1_anchor_plus_built_rel_type
- status: discard
- cv_mae: 50740.327766803974
- cv_mae_std: 4650.1529962172
- runtime_seconds: 233.31889530000626
- change_from_previous: single_knob=mls_1
- hypothesis: v2 Deepen iter6: min_samples_leaf 2 -> 1 with depth=18 fixed. v1 tested mls=1 with depth=None and saw regression -- but with depth=18 cap, mls=1 may give finer terminal granularity without overfitting.
- observation: mls=1 + depth=18 regressed CV MAE 50565.97 -> 50740.33 in 233s. Tied within noise but trending wrong. Mls=2 stays the better leaf-size with these data; finer leaves overfit fold-internal noise even with depth cap.
- comparison: vs lane A (50565.97 +/- 4813.84) -> +174.35. vs v1 anchor (50663.64) -> +76.69. vs HGB iter21 (50934.78) -> -194.45.
- significance: pooled_std vs lane A = sqrt((4650.15^2+4813.84^2)/2) ~= 4732.94, threshold ~= 1183; |Delta| 174 << 1183 -> WITHIN NOISE; tie. Discard; revert mls to 2.
- attribution: one-knob: min_samples_leaf 2 -> 1, all other params and features unchanged.
- next_hypothesis: D7 = per-property-type sub-models architecture. Top 3 property types in train: UNE MAISON (10085), UN APPARTEMENT (6443), TERRAIN DE TYPE TERRE ET PRE (2020). Train per-type RF (same recipe, n_est=100) on each type subset; blend 0.3*sub + 0.7*global for predictions of that type, pure global elsewhere. Proven xgboost_v4 lift -215 cumulative. With smaller per-sub n_est=100 and 3 sub-types, expected runtime 1.5x global = ~330s.

## 20260508-230947-deepen-lane_a_per_type_submodels

- stage: deepen
- feature_lane: lane_a_per_type_submodels
- change_kind: hyperparameter
- hypothesis_unit: per_property_type_submodels
- feature_group: structural_numeric
- anchor_run_id: 20260508-222002-smoke-v1_anchor_plus_built_rel_type
- status: discard
- cv_mae: 50602.36259056847
- cv_mae_std: 4808.996309306984
- runtime_seconds: 344.6681021999975
- change_from_previous: single_knob=per_type_submodels_top3
- hypothesis: v2 Deepen iter7: per-property-type sub-model architecture on lane A. Train top-3 type sub-RFs (n_est=100, same recipe) on type subsets of train; blend 0.3*sub + 0.7*global for predictions of that type. xgboost_v4 saw -215 cumulative from this exact architecture. Top types: UNE MAISON (10085), UN APPARTEMENT (6443), TERRAIN DE TYPE TERRE ET PRE (2020).
- observation: per-type sub-models with 0.3 blend essentially tied lane A: 50565.97 -> 50602.36 in 345s (1.5x runtime). Architecture didn't lift RF the way it lifted xgboost_v4 (-215). Hypothesis: RF already de-correlates trees via mf=0.4 + bootstrap=False per-tree subsampling, so per-type sub-models add redundant variance averaging rather than bias correction. Boosting wins from per-type because each sub-model refines residuals on its own subset.
- comparison: vs lane A (50565.97 +/- 4813.84) -> +36.39. vs v1 anchor (50663.64) -> -61.27. vs HGB iter21 (50934.78) -> -332.42.
- significance: pooled_std vs lane A = sqrt((4809.00^2+4813.84^2)/2) ~= 4811.42, threshold ~= 1203; |Delta| 36 << 1203 -> WITHIN NOISE; tie. Discard sub-models architecture; revert.
- attribution: one-knob: per-type sub-model wrapper around lane A pipeline (3 extra fits, blend 0.3 sub / 0.7 global at predict).
- next_hypothesis: PLATEAU OBSERVED. Family best 50565.97 (lane A) is structurally tied with HGB iter21 (50934.78) -- |Delta|=369 << 1201 noise threshold. 7 deepen iters tried (built_per_land, room_density_cumulative, ExtraTrees, n_est=400, max_depth=22, mls=1, per-type sub-models); all tied or regressed. Promotion to global champion requires Delta <= -1201, i.e. cv_mae <= 49,741 -- ~825 more drop with no obvious knob remaining. Pause and consult user on whether to (a) continue exploring less-likely knobs (log_skewed_numerics, smooth=15, n_est=600 capacity push) or (b) park v2 as a tie/runner-up like v1 was.

## 20260508-232044-deepen-lane_a_log_skewed

- stage: deepen
- feature_lane: lane_a_log_skewed
- change_kind: feature
- hypothesis_unit: log_skewed_numerics
- feature_group: structural_numeric
- anchor_run_id: 20260508-222002-smoke-v1_anchor_plus_built_rel_type
- status: discard
- cv_mae: 50691.822254380015
- cv_mae_std: 4755.8706782729605
- runtime_seconds: 362.91667289999896
- change_from_previous: single_knob=log_skewed_numerics
- hypothesis: v2 Deepen iter8: add log1p of 9 heavily-skewed numeric columns (areas + count-of-X). Hypothesis: depth=18 trees may struggle to find split points in heavy-tailed distributions; explicit log transforms give RF easier-to-split linear-scaled features. Untried lift in this family.
- observation: log1p of 9 heavily-skewed numerics regressed CV MAE 50565.97 -> 50691.82 in 363s. Tied within noise but trending wrong. Tree models are scale-invariant; log transforms duplicate information already present in the raw columns and add column-count noise.
- comparison: vs lane A (50565.97 +/- 4813.84) -> +125.85. vs v1 anchor (50663.64) -> +28.18. vs HGB iter21 (50934.78) -> -242.96.
- significance: pooled_std vs lane A = sqrt((4755.87^2+4813.84^2)/2) ~= 4784.96, threshold ~= 1196; |Delta| 126 << 1196 -> WITHIN NOISE; tie. Discard signal; revert log_skewed_numerics.
- attribution: one-knob: 9 *_log columns appended to numeric pipeline; revert.
- next_hypothesis: D9 = smooth=15 (mid-point between v1's tested smooth=10 winner and smooth=20 baseline). Tests whether lane A's 4 target encoders prefer slightly more smoothing. Cheap, ~3 min.

## 20260508-232800-deepen-lane_a_smooth_15

- stage: deepen
- feature_lane: lane_a_smooth_15
- change_kind: hyperparameter
- hypothesis_unit: te_smoothing
- feature_group: geography
- anchor_run_id: 20260508-222002-smoke-v1_anchor_plus_built_rel_type
- status: discard
- cv_mae: 50767.984414555816
- cv_mae_std: 4851.364059014033
- runtime_seconds: 287.66904429999704
- change_from_previous: single_knob=smooth_15
- hypothesis: v2 Deepen iter9: target_enc smooth 10 -> 15 on lane A. Mid-point between v1's tested 10 (winner) and 20 (baseline). With built_rel_type added in lane A, the optimal smoothing may have shifted slightly higher.
- observation: smooth=15 regressed CV MAE 50565.97 -> 50767.98 in 288s. Tied within noise; smooth=10 confirmed family-wide local optimum.
- comparison: vs lane A (50565.97 +/- 4813.84) -> +202.01. vs v1 anchor (50663.64) -> +104.34. vs HGB iter21 (50934.78) -> -166.80.
- significance: pooled_std vs lane A = sqrt((4851.36^2+4813.84^2)/2) ~= 4832.65, threshold ~= 1208; |Delta| 202 << 1208 -> WITHIN NOISE; tie. Discard; revert smooth to 10.
- attribution: one-knob: TARGET_ENC_SMOOTH 10 -> 15 in target_encoding_columns; revert.
- next_hypothesis: D10 = max_features 0.4 -> 0.3 on lane A. v1 swept 0.4, 0.5, 0.7, sqrt; 0.4 was best. Below 0.4 untested; more decorrelation between trees may now help with built_rel_type added.

## 20260508-233359-deepen-lane_a_mf_0_3

- stage: deepen
- feature_lane: lane_a_mf_0_3
- change_kind: hyperparameter
- hypothesis_unit: max_features_0_3
- feature_group: structural_numeric
- anchor_run_id: 20260508-222002-smoke-v1_anchor_plus_built_rel_type
- status: discard
- cv_mae: 50886.083752301245
- cv_mae_std: 4890.892148741692
- runtime_seconds: 272.05011780001223
- change_from_previous: single_knob=mf_0_3
- hypothesis: v2 Deepen iter10: max_features 0.4 -> 0.3 on lane A. v1 tested 0.5/0.7/sqrt + 0.4 won. Below 0.4 untested; more aggressive feature decorrelation between trees may help with the built_rel_type addition.
- observation: max_features=0.3 regressed CV MAE 50565.97 -> 50886.08 in 272s. Tied within noise but trending wrong; mf=0.4 confirmed family-wide local optimum.
- comparison: vs lane A (50565.97 +/- 4813.84) -> +320.11. vs v1 anchor (50663.64) -> +222.44. vs HGB iter21 (50934.78) -> -48.69.
- significance: pooled_std vs lane A = sqrt((4890.89^2+4813.84^2)/2) ~= 4852.51, threshold ~= 1213; |Delta| 320 << 1213 -> WITHIN NOISE; tie. Discard; revert mf to 0.4.
- attribution: one-knob: max_features 0.4 -> 0.3, all other params and features unchanged.
- next_hypothesis: STAGE 2 GATE: 10 single-knob deepen iters complete; family conclusively plateaued at 50565.97. None of (built_per_land, room_density_cumulative, ExtraTrees, n_est=400, max_depth=22, mls=1, per-type sub-models, log_skewed_numerics, smooth=15, mf=0.3) yielded a noise-aware lift. RF on this dataset has structural ceiling near v1's promoted recipe. Cannot honestly promote v2 over HGB iter21 -- the gap is real signal-noise tied. Recommend (a) park v2 as runner-up tie like v1 was, OR (b) confirm seed=2026 of lane A built_rel_type as documentation of the new family-best (still not a promoted global winner).

## 20260509-152129-deepen-lane_a_plus_built_rel_commune

- stage: deepen
- feature_lane: lane_a_plus_built_rel_commune
- change_kind: feature
- hypothesis_unit: built_rel_commune
- feature_group: derived_ratios
- anchor_run_id: 20260508-222002-smoke-v1_anchor_plus_built_rel_type
- status: discard
- cv_mae: 50676.005090102015
- cv_mae_std: 4791.533029200295
- runtime_seconds: 278.9065866000019
- change_from_previous: single_knob=built_rel_commune
- hypothesis: v2 Deepen iter11: lane A + built_rel_commune = built_area / mean(built_area | commune_first), fold-safe. Different group than built_rel_type (commune ~196 vs property_type ~25); injects geographic-relative size signal.
- observation: built_rel_commune cumulative on lane A regressed CV MAE 50565.97 -> 50676.01 in 279s. Slight regression. Commune-grouped built area is too sparse (196 communes, many with <30 records); the relative ratio noise overwhelms the signal that property_type-grouped (25 levels) captured cleanly.
- comparison: vs lane A (50565.97 +/- 4813.84) -> +110.03. vs v1 anchor (50663.64) -> +12.36. vs HGB iter21 (50934.78) -> -258.78.
- significance: pooled_std vs lane A = sqrt((4791.53^2+4813.84^2)/2) ~= 4802.71, threshold ~= 1201; |Delta| 110 << 1201 -> WITHIN NOISE; tie. Discard; revert.
- attribution: one-knob: built_rel_commune feature added in prepare_frames; revert.
- next_hypothesis: D12 = capacity push n_est=200 -> n_est=600 on lane A. Last untested big-knob within hard-stop budget (~10 min projected). With family plateaued on every cheap knob, capacity is the only structural lever remaining.

## 20260509-152757-deepen-lane_a_n_est_600

- stage: deepen
- feature_lane: lane_a_n_est_600
- change_kind: hyperparameter
- hypothesis_unit: n_est_600
- feature_group: structural_numeric
- anchor_run_id: 20260508-222002-smoke-v1_anchor_plus_built_rel_type
- status: discard
- cv_mae: 50632.06873056925
- cv_mae_std: 4788.252718488825
- runtime_seconds: 735.3870284000004
- change_from_previous: single_knob=n_est_600
- hypothesis: v2 Deepen iter12: capacity push n_est 200 -> 600 on lane A. Last big-knob within hard-stop budget (~10 min projected). n_est=400 was tied; n_est=600 is the next reasonable step under the policy ceiling.
- observation: n_est=600 ran 735s (over hard stop, within 900s timeout) and tied lane A: 50565.97 -> 50632.07. Capacity is fully saturated. n_est sweep: 200=50566, 400=50661, 600=50632 -- non-monotonic noise around the same level.
- comparison: vs lane A (50565.97 +/- 4813.84) -> +66.09. vs v1 anchor (50663.64) -> -31.57. vs HGB iter21 (50934.78) -> -302.71.
- significance: pooled_std vs lane A = sqrt((4788.25^2+4813.84^2)/2) ~= 4801.06, threshold ~= 1200; |Delta| 66 << 1200 -> WITHIN NOISE; tie. Capacity confirmed exhausted.
- attribution: one-knob: n_est 200 -> 600, all other params and features unchanged.
- next_hypothesis: D13 = inline two-seed averaging within fit_predict (train RF seed=42 and seed=2026, average predictions). v1 iter10 tested 3-seed at depth=None and was within noise; with v2's lane A built_rel_type, two-seed variance reduction may finally yield a real lift. Expected runtime 2x = ~440s = 7.4 min, within budget.

## 20260509-154227-deepen-lane_a_two_seed_avg

- stage: deepen
- feature_lane: lane_a_two_seed_avg
- change_kind: hyperparameter
- hypothesis_unit: two_seed_average
- feature_group: structural_numeric
- anchor_run_id: 20260508-222002-smoke-v1_anchor_plus_built_rel_type
- status: discard
- cv_mae: 50581.7320080845
- cv_mae_std: 4773.425564122345
- runtime_seconds: 469.6930085000058
- change_from_previous: single_knob=two_seed_avg
- hypothesis: v2 Deepen iter13: train RF seed=42 and seed=2026 inline, average predictions. Pure variance reduction (no bias change). v1 iter10 tested 3-seed at depth=None and was within noise; with v2's lane A (built_rel_type, depth=18), two-seed averaging may yield -150 to -250 from noise reduction.
- observation: two-seed averaging tied lane A: 50565.97 -> 50581.73 in 470s (2x runtime). Variance reduction saturated -- 200 trees already average enough that adding a second seed-shifted ensemble doesn't reduce fold MAE further. Mirror of v1 iter10's 3-seed null result on a different anchor. Family is fully exhausted.
- comparison: vs lane A (50565.97 +/- 4813.84) -> +15.76. vs v1 anchor (50663.64) -> -81.91. vs HGB iter21 (50934.78) -> -353.05.
- significance: pooled_std vs lane A = sqrt((4773.43^2+4813.84^2)/2) ~= 4793.66, threshold ~= 1198; |Delta| 16 << 1198 -> WITHIN NOISE; tie. Discard.
- attribution: one-knob: build_model now takes random_state arg; fit_predict trains 2 RFs (seeds 42, 2026) and averages predictions; revert.
- next_hypothesis: STAGE 2 EXHAUSTED. 13 single-knob deepen iters complete (max policy budget 15; spent 13 with no real lift). Family conclusively plateaued at 50565.97 (lane A built_rel_type only). vs HGB iter21 global champion (50934.78): -369, threshold ~1201, |Delta|=369 << 1201 -- TIE WITHIN NOISE. Promotion impossible: tree_bagging_rf class is structurally limited to ~50500-50700 cv_mae on this dataset; HGB iter21 is in the same band. Decision: park v2 as runner-up tie (mirror of v1's outcome). Confirm seed=2026 of lane A best for documentation, then formally close family. Recommend user pivot promotion path to xgboost_v4 (47998 confirm seed=2026; -2937 vs HGB, well past noise threshold).

## 20260509-155212-deepen-v1_anchor_plus_built_rel_type

- stage: deepen
- feature_lane: v1_anchor_plus_built_rel_type
- change_kind: diagnostic
- hypothesis_unit: confirm_seed2026
- feature_group: confirmation
- anchor_run_id: 20260508-222002-smoke-v1_anchor_plus_built_rel_type
- status: confirm
- cv_mae: 50900.22586500195
- cv_mae_std: 4520.902571888611
- runtime_seconds: 236.55387570001767
- change_from_previous: confirm_seed2026
- hypothesis: v2 Confirm: seed=2026 of family-best lane A (built_rel_type cumulative on v1 anchor). Documents the family-best on a second shuffled-fold seed; promotion blocked because seed=42 best already ties HGB iter21 within noise (no path to global winner).
- observation: seed=2026 of lane A produced cv_mae 50900.23 +/- 4520.90 (vs seed=42 same recipe 50565.97 +/- 4813.84, |Delta|=334 within pooled noise ~1167). Two-seed mean = 50733.10. Family-best confirmed; reproducibility good across seeds.
- comparison: 2-seed mean 50733 vs HGB iter21 global champion 50934.78: -201.68. Pooled std vs HGB iter21 ~= sqrt((4520.90^2+4795.53^2)/2) ~= 4660.30, threshold ~1165. |Delta| 202 << 1165 -> TIE WITHIN NOISE.
- significance: family-best 2-seed mean is statistically tied with the existing global champion. Promotion blocked by noise-aware gate.
- attribution: one-knob: random_state 42 -> 2026 for both KFold and RF; recipe and features unchanged.
- next_hypothesis: STAGE 4 GATE FAILED for promotion. tree_bagging_rf_v2 family CLOSED as runner-up tie. Final state: best_run lane A (50565.97 seed=42, 50900.23 seed=2026, 2-seed mean 50733.10). RF class on this dataset has a structural ceiling at ~50500-50800 -- same band as HGB iter21. Path to a global promoted winner requires a different model class (xgboost_v4 already at 47998 confirm seed=2026, -2937 vs HGB, well past noise threshold).
