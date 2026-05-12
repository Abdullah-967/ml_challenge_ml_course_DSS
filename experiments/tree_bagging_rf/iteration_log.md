# tree_bagging_rf Iteration Log

Append-only. One block per reflected canonical CV run.

Required fields per entry: stage, change_kind, hypothesis_unit, feature_group, anchor_run_id, change_from_previous, hypothesis, observation, comparison, significance, attribution, next_hypothesis.

## 20260506-235058-smoke-all_numeric

- stage: smoke
- feature_lane: all_numeric
- change_kind: feature
- hypothesis_unit: structural_numeric_baseline
- feature_group: structural_numeric
- anchor_run_id: n/a
- status: keep
- cv_mae: 61056.896543641415
- cv_mae_std: 3650.7592905866345
- runtime_seconds: 17.876190599999973
- change_from_previous: single_knob=all_numeric
- hypothesis: Stage 1 smoke iter1: RandomForestRegressor(n_est=200,max_depth=18,mls=2,max_features=sqrt) on all_numeric lane (excl parcel_ids/transferred_parcel_ids). Fair anchor vs xgboost smoke iter1 (53600.06) and HGB iter1 (70431.74).
- observation: First RF family run; 200 trees max_depth=18 + SimpleImputer(median) on the same all_numeric scope as xgboost smoke iter1 ran in 17.9s -- about half xgboost's wall time (39.7s). Note: sklearn RF default criterion is "squared_error", which is a structural mismatch for an MAE objective (MAE-criterion split is available but ~10x slower). Sets family best at 61056.90.
- comparison: vs xgboost smoke iter1 (same lane, 53600.06 +/- 4575.50) -> +7457; vs HGB iter2 (same lane absolute_error, 56069.80 +/- 4771.19) -> +4987; vs HGB iter1 (same lane squared_error, 70431.74 +/- 3908.36) -> -9375; vs global best xgboost confirm 49827.48 -> +11229.
- significance: Pooled-std vs xgboost lane1 = sqrt((3650.76^2+4575.50^2)/2) ~= 4139, threshold (0.25x) ~= 1035; |Delta| 7457 >> 1035 -> REAL gap, RF is meaningfully worse than xgboost on this lane. vs HGB iter2: pooled ~= 4248, threshold ~= 1062; |Delta| 4987 >> 1062 -> REAL gap. vs HGB iter1: pooled ~= 3782, threshold ~= 946; |Delta| 9375 >> 946 -> RF beats HGB-with-squared-error meaningfully (expected, since HGB iter1 used the wrong loss). Global best gap is ~11k; expected for first smoke.
- attribution: one-knob smoke; pure feature-lane choice on default-criterion RF, no bundled changes.
- next_hypothesis: STAGE 1 GATE: 1/3 lanes done. Continue smoke. Lane 2 = numeric_plus_basic_cats: one-hot encode property_type (25 vals) + transaction_type (6 vals) on top of all_numeric. Hypothesis_unit = property_transaction_categories. Note RF has no native cat support (unlike XGBoost), so explicit encoding required.

## 20260506-235444-smoke-numeric_plus_basic_cats

- stage: smoke
- feature_lane: numeric_plus_basic_cats
- change_kind: feature
- hypothesis_unit: property_transaction_categories
- feature_group: property_transaction
- anchor_run_id: n/a
- status: keep
- cv_mae: 60925.65839035219
- cv_mae_std: 3521.6953111850885
- runtime_seconds: 18.90166920000047
- change_from_previous: single_knob=numeric_plus_basic_cats
- hypothesis: Smoke iter2: all_numeric + OHE(property_type, transaction_type) -- low-card cat lift on RF (no native cats).
- observation: OHE'ing property_type (25) + transaction_type (6) on top of all_numeric moved CV MAE -131 in 18.9s; runtime nearly unchanged (one-hot adds ~30 cols, sqrt(features) goes 6 -> 8). Sets new family best, but only marginally.
- comparison: vs lane1 (61056.90 +/- 3650.76) -> -131.24. vs xgboost lane2 (52771.66) -> +8154 (RF still real-gap behind boosting on the same lane). vs HGB iter6 (commune+property cats, 52355.69) -> +8570. vs global best xgboost confirm 49827.48 -> +11098.
- significance: Pooled-std vs lane1 = sqrt((3521.70^2+3650.76^2)/2) ~= 3587, threshold (0.25x) ~= 897; |Delta| 131 << 897 -> WITHIN NOISE, treat as tie. Reflector tag "keep" by lowest MAE only; not a real win.
- attribution: one-knob lane swap; OHE preprocessing added, model+seed unchanged.
- next_hypothesis: STAGE 1 GATE: 2/3 lanes done. Lane 3 = derived_ratios: drop OHE cats; recipe = all_numeric + 5 structural ratios (built_per_premise, land_per_lot, commercial_share, apt_share, houses_per_premise). Hypothesis_unit = structural_ratios.

## 20260506-235558-smoke-derived_ratios

- stage: smoke
- feature_lane: derived_ratios
- change_kind: feature
- hypothesis_unit: structural_ratios
- feature_group: structural_ratios
- anchor_run_id: n/a
- status: keep
- cv_mae: 61040.7628259043
- cv_mae_std: 3561.8936066842016
- runtime_seconds: 18.694125499998336
- change_from_previous: single_knob=derived_ratios
- hypothesis: Smoke iter3: all_numeric + 5 structural ratios (drops OHE cats from iter2). Tests interpretable ratio lift.
- observation: Ratios alone (no cats) gave CV MAE 61040.76 in 18.7s -- statistical tie with both lane1 and lane2; ratios add no decisive signal on RF beyond raw counts/areas.
- comparison: vs lane2 family best (60925.66 +/- 3521.70) -> +115. vs lane1 (61056.90) -> -16. vs xgboost smoke iter3 geo_signal (51530.01) -> +9511. vs global best xgboost confirm 49827.48 -> +11214.
- significance: Pooled-std vs lane2 = sqrt((3521.70^2+3561.89^2)/2) ~= 3542, threshold (0.25x) ~= 885; |Delta| 115 << 885 -> WITHIN NOISE; tie. All three RF smoke lanes lie within a 132 MAE band -- lane choice does not move RF much when limited to local features (no geo).
- attribution: one-knob lane swap (added ratios, dropped OHE cats from iter2).
- next_hypothesis: STAGE 1 GATE SATISFIED (3/3 lanes). Best lane by lowest MAE = numeric_plus_basic_cats (60925.66, smoke iter2). Enter Stage 2 deepen on top of smoke iter2 baseline (all_numeric + OHE cats). First single-knob: cumulative add of 5 structural ratios (carry-over from lane3). Bigger expected lifts later: ordinal commune_first (geo signal, biggest expected on parallel to xgboost), criterion=absolute_error (loss-metric alignment for sklearn RF default squared_error mismatch with MAE).

## 20260506-235748-deepen-numeric_plus_basic_cats

- stage: deepen
- feature_lane: numeric_plus_basic_cats
- change_kind: feature
- hypothesis_unit: structural_ratios
- feature_group: structural_ratios
- anchor_run_id: 20260506-235444-smoke-numeric_plus_basic_cats
- status: keep
- cv_mae: 60429.906926533884
- cv_mae_std: 3686.8048528938684
- runtime_seconds: 19.489033800011384
- change_from_previous: single_knob=add_ratios
- hypothesis: Deepen iter1: add 5 structural ratios on top of smoke iter2 cats baseline.
- observation: Ratios cumulative on cats moved CV MAE -496 to 60429.91 in 19.5s. Family low; runtime stable. Note: ratios alone (smoke iter3) tied lane1; ratios+cats together do better than either alone -- tiny synergy.
- comparison: vs cats baseline (60925.66) -> -495.75. vs lane1 ratios-only (61040.76) -> -610.86. vs xgboost deepen iter2 ratios on geo (51520.50) -> +8909 (RF still way behind boosting). vs global best 49827.48 -> +10602.
- significance: Pooled-std vs cats baseline = sqrt((3686.80^2+3521.70^2)/2) ~= 3604, threshold (0.25x) ~= 901; |Delta| 496 < 901 -> WITHIN NOISE; tie. Keep ratios cumulative since they don't hurt and are interpretable; lowest MAE.
- attribution: one-knob: 5 ratios added on top of smoke iter2; OHE cats kept, model+seed unchanged.
- next_hypothesis: Deepen iter2: add commune_first target encoding (smoothed=20, fold-safe from train fold only). RF has no native cat support; target encoding is the proper way to inject geo signal. Expected biggest single lift in deepen, mirroring xgboost's geo_signal smoke (-1241).

## 20260507-000004-deepen-numeric_plus_basic_cats

- stage: deepen
- feature_lane: numeric_plus_basic_cats
- change_kind: feature
- hypothesis_unit: commune_first_target_enc
- feature_group: geography
- anchor_run_id: 20260506-235748-deepen-numeric_plus_basic_cats
- status: keep
- cv_mae: 59018.931977166314
- cv_mae_std: 3243.107523028975
- runtime_seconds: 17.09326900000451
- change_from_previous: single_knob=commune_target_enc20
- hypothesis: Deepen iter2: add commune_first target encoding (smoothed=20, fold-safe). Geo signal injection for a no-native-cats family.
- observation: Smoothed-target-encoded commune_first dropped CV MAE -1411 to 59018.93 in 17.1s -- biggest single-knob lift in this family so far. Runtime even slightly faster than iter1 (one extra numeric col vs imputed numerics + OHE). std also tightened (3686 -> 3243). Confirms hypothesis: RF needs explicit numeric geo signal since no native cat support.
- comparison: vs deepen iter1 (60429.91 +/- 3686.80) -> -1410.97. vs xgboost smoke iter3 same lane (51530.01) -> +7489 (still real gap). vs HGB iter6 commune+property cats (52355.69) -> +6663. vs global best xgboost 49827.48 -> +9192.
- significance: Pooled-std vs iter1 = sqrt((3243.11^2+3686.80^2)/2) ~= 3475, threshold (0.25x) ~= 869; |Delta| 1411 > 869 -> REAL WIN. New family best.
- attribution: one-knob: commune_target_enc on top of deepen iter1; smoothing fitted train-fold-only.
- next_hypothesis: Deepen iter3: add cadastral_first target encoding (smooth=20) for finer geo granularity. Cadastral is sub-commune (846 vals) -- a smaller-area price level signal that may complement commune.

## 20260507-000122-deepen-numeric_plus_basic_cats

- stage: deepen
- feature_lane: numeric_plus_basic_cats
- change_kind: feature
- hypothesis_unit: cadastral_first_target_enc
- feature_group: geography
- anchor_run_id: 20260507-000004-deepen-numeric_plus_basic_cats
- status: keep
- cv_mae: 58363.15745959924
- cv_mae_std: 3050.9804392186143
- runtime_seconds: 17.35959449999791
- change_from_previous: single_knob=cadastral_target_enc20
- hypothesis: Deepen iter3: add cadastral_first target encoding (smooth=20). Sub-commune (846 vals) finer geo granularity.
- observation: Cadastral target_enc dropped CV MAE -656 to 58363.16 in 17.4s; std tightened further (3243 -> 3051). Stacks with commune_target_enc since cadastral is a sub-commune partition giving sub-municipal price level.
- comparison: vs deepen iter2 (59018.93 +/- 3243.11) -> -655.77. vs xgboost smoke iter3 51530.01 -> +6833. vs global best 49827.48 -> +8536.
- significance: Pooled-std vs iter2 = sqrt((3243.11^2+3050.98^2)/2) ~= 3148, threshold (0.25x) ~= 787; |Delta| 656 < 787 -> WITHIN NOISE; tie. Keep cumulative; lowest MAE.
- attribution: one-knob: cadastral_target_enc on top of iter2; smoothing fitted train-fold-only.
- next_hypothesis: Deepen iter4: add transaction_date as date_ordinal (days since 2014-01-01). Mirrors xgboost deepen iter5 which added -134; for RF the lift may be larger since RF has fewer split features without it.

## 20260507-000239-deepen-numeric_plus_basic_cats

- stage: deepen
- feature_lane: numeric_plus_basic_cats
- change_kind: feature
- hypothesis_unit: transaction_date_ordinal
- feature_group: temporal
- anchor_run_id: 20260507-000122-deepen-numeric_plus_basic_cats
- status: keep
- cv_mae: 58712.07500926192
- cv_mae_std: 3223.626843862468
- runtime_seconds: 18.82493020000402
- change_from_previous: single_knob=date_ordinal
- hypothesis: Deepen iter4: add transaction_date as date_ordinal (days since 2014-01-01).
- observation: date_ordinal regressed +349 to 58712.08 in 18.8s. Reflector kept best as iter3. RF was unable to extract additional signal from raw transaction-day; year/month already in numeric set may already capture annual price drift.
- comparison: vs iter3 best (58363.16 +/- 3050.98) -> +348.91. vs xgboost deepen iter5 (51386.02) -> +7326.
- significance: Pooled-std vs iter3 = sqrt((3050.98^2+3223.63^2)/2) ~= 3138, threshold (0.25x) ~= 784; |Delta| 349 < 784 -> WITHIN NOISE; small regression. Treat as tie-with-overhead; REVERT date_ordinal in next iter.
- attribution: one-knob: date_ordinal on top of iter3.
- next_hypothesis: REVERT date_ordinal. Deepen iter5: add commune frequency encoding (count of records per commune in train fold). Different geo signal than target_enc (does not depend on target), may capture commune-size effects orthogonal to target_enc.

## 20260507-000421-deepen-numeric_plus_basic_cats

- stage: deepen
- feature_lane: numeric_plus_basic_cats
- change_kind: feature
- hypothesis_unit: commune_frequency
- feature_group: geography
- anchor_run_id: 20260507-000122-deepen-numeric_plus_basic_cats
- status: keep
- cv_mae: 58265.0065211728
- cv_mae_std: 3235.011745017061
- runtime_seconds: 17.93248859999585
- change_from_previous: single_knob=commune_freq
- hypothesis: Deepen iter5: REVERT date_ordinal, add commune frequency encoding (count of train records per commune). Different geo signal (target-independent) that may capture commune-size effects orthogonal to target_enc.
- observation: commune_freq cumulative dropped CV MAE -98 to 58265.01 in 17.9s. Marginal lift; new family low.
- comparison: vs iter3 baseline (58363.16 +/- 3050.98) -> -98.15. vs xgboost smoke iter3 51530.01 -> +6735. vs global best 49827.48 -> +8438.
- significance: Pooled-std vs iter3 = sqrt((3050.98^2+3235.01^2)/2) ~= 3144, threshold (0.25x) ~= 786; |Delta| 98 << 786 -> WITHIN NOISE; tie. Keep cumulatively since no hurt.
- attribution: one-knob: commune_freq added; date_ordinal reverted from iter4; remaining recipe unchanged.
- next_hypothesis: Deepen iter6: add property_type target encoding (smooth=20) on top of OHE property_type. xgboost iter10 saw the biggest deepen lift from property_type cat (-429); for RF a numeric target_enc may also help despite OHE already present.

## 20260507-000534-deepen-numeric_plus_basic_cats

- stage: deepen
- feature_lane: numeric_plus_basic_cats
- change_kind: feature
- hypothesis_unit: property_type_target_enc
- feature_group: property_transaction
- anchor_run_id: 20260507-000421-deepen-numeric_plus_basic_cats
- status: keep
- cv_mae: 57734.63421002294
- cv_mae_std: 3422.8383701797306
- runtime_seconds: 18.108412399989902
- change_from_previous: single_knob=property_type_te20
- hypothesis: Deepen iter6: add property_type target encoding (smooth=20) alongside OHE. Numeric encoding may help splits the OHE columns alone cannot find at the same depth.
- observation: property_type_target_enc dropped CV MAE -530 to 57734.63 in 18.1s; fairly tightened (std 3235 -> 3423). New family low.
- comparison: vs iter5 (58265.01 +/- 3235.01) -> -530.37. vs xgboost deepen iter10 property_type cat (50957.36) -> +6777. vs global best 49827.48 -> +7907.
- significance: Pooled-std vs iter5 = sqrt((3235.01^2+3422.84^2)/2) ~= 3330, threshold (0.25x) ~= 832; |Delta| 530 < 832 -> WITHIN NOISE; tie. Keep cumulative; lowest MAE.
- attribution: one-knob: property_type_target_enc added; OHE retained.
- next_hypothesis: Deepen iter7: add log1p target (USE_LOG_TARGET=True) -- mirrors HGB iter21 winning move (-307). xgboost deepen iter1 saw log1p hurt (+137) due to MAE-in-log != MAE-in-original misalignment, but RF default criterion is squared_error (which matches well with log-y), so log1p may actually help RF the way it helped HGB.

## 20260507-000647-deepen-numeric_plus_basic_cats

- stage: deepen
- feature_lane: numeric_plus_basic_cats
- change_kind: target
- hypothesis_unit: log1p_target
- feature_group: target_transform
- anchor_run_id: 20260507-000534-deepen-numeric_plus_basic_cats
- status: keep
- cv_mae: 54221.87142798641
- cv_mae_std: 5216.213253376055
- runtime_seconds: 18.101488799991785
- change_from_previous: single_knob=log1p_target
- hypothesis: Deepen iter7: log1p target. RF default criterion=squared_error optimizes mean in log-space, which approximates median in original space for skewed price distributions; this is a structural fix for the squared_error/MAE mismatch.
- observation: log1p target dropped CV MAE -3513 to 54221.87 in 18.1s -- DOMINANT single-knob lift in this family. Per-fold std bumped (3423 -> 5216) since log target makes per-fold variance larger, but absolute MAE gain is huge. Now within striking distance of xgboost (49827) and HGB iter21 (50934).
- comparison: vs iter6 (57734.63 +/- 3422.84) -> -3512.76. vs HGB iter21 log1p target (50934.78 +/- 4795.53) -> +3287. vs xgboost confirm 49827.48 -> +4394.
- significance: Pooled-std vs iter6 = sqrt((3422.84^2+5216.21^2)/2) ~= 4413, threshold (0.25x) ~= 1103; |Delta| 3513 >> 1103 -> REAL WIN, biggest deepen lift. New family low.
- attribution: one-knob: USE_LOG_TARGET=True; everything else unchanged from iter6.
- next_hypothesis: Deepen iter8: add transaction_type target encoding (smooth=20). transaction_type already OHE'd; numeric encoding may add complementary signal at log scale.

## 20260507-000809-deepen-numeric_plus_basic_cats

- stage: deepen
- feature_lane: numeric_plus_basic_cats
- change_kind: feature
- hypothesis_unit: transaction_type_target_enc
- feature_group: property_transaction
- anchor_run_id: 20260507-000647-deepen-numeric_plus_basic_cats
- status: keep
- cv_mae: 54241.39953240492
- cv_mae_std: 5157.209132619465
- runtime_seconds: 17.923641099987435
- change_from_previous: single_knob=transaction_type_te20
- hypothesis: Deepen iter8: add transaction_type target encoding (smooth=20). Numeric encoding may complement OHE at log scale.
- observation: transaction_type_target_enc tied iter7 at 54241.40 (+19) -- transaction_type has only 6 values, so the OHE columns already give RF clean access; target_enc is largely redundant.
- comparison: vs iter7 (54221.87 +/- 5216.21) -> +19.5. vs HGB iter21 50934.78 -> +3306. vs xgboost confirm 49827.48 -> +4414.
- significance: Pooled-std vs iter7 = sqrt((5216.21^2+5157.21^2)/2) ~= 5187, threshold (0.25x) ~= 1297; |Delta| 19 << 1297 -> WITHIN NOISE; tie. Reflector best stays at iter7 (lowest MAE). Drop in ablate as redundant; keep cumulatively now.
- attribution: one-knob: transaction_type_target_enc added on top of iter7 (log1p target retained).
- next_hypothesis: Deepen iter9: add presence_flags (has_apt, has_house, has_land, has_commercial, has_built) as int8 indicators. xgboost saw +28 (within noise) but RF with sqrt(features) random subselection may benefit more from explicit booleans since RF's per-split feature pool is smaller.

## 20260507-000930-deepen-numeric_plus_basic_cats

- stage: deepen
- feature_lane: numeric_plus_basic_cats
- change_kind: feature
- hypothesis_unit: presence_flags
- feature_group: structural_numeric
- anchor_run_id: 20260507-000647-deepen-numeric_plus_basic_cats
- status: keep
- cv_mae: 53939.82286275828
- cv_mae_std: 5161.078514777752
- runtime_seconds: 18.495922299989616
- change_from_previous: single_knob=presence_flags
- hypothesis: Deepen iter9: add 5 presence flags (has_apt, has_house, has_land, has_commercial, has_built). RF's sqrt(features) sub-sampling makes explicit booleans more accessible per split than xgboost saw.
- observation: presence_flags dropped CV MAE -302 to 53939.82 in 18.5s. Modest cumulative lift; new family low. Interesting cross-family contrast: xgboost saw +28 (regress), RF sees -302 -- consistent with the hypothesis that RF's smaller per-split feature pool benefits from explicit indicators where xgboost finds them via numeric splits anyway.
- comparison: vs iter8 (54241.40 +/- 5157.21) -> -301.58. vs iter7 (54221.87) -> -282.05. vs HGB iter21 50934.78 -> +3005. vs xgboost confirm 49827.48 -> +4112.
- significance: Pooled-std vs iter7 = sqrt((5216.21^2+5161.08^2)/2) ~= 5189, threshold (0.25x) ~= 1297; |Delta| 282 << 1297 -> WITHIN NOISE; tie. Keep cumulative; lowest MAE.
- attribution: one-knob: 5 presence_flags added on top of iter8.
- next_hypothesis: Deepen iter10: drop OHE cats (use only target_enc and presence_flags for cat info). xgboost found OHE redundant when geo native cats were present; for RF the parallel test is whether OHE adds value when target_enc is already there.

## 20260507-001053-deepen-numeric_plus_basic_cats

- stage: deepen
- feature_lane: numeric_plus_basic_cats
- change_kind: preprocessing
- hypothesis_unit: drop_ohe_cats
- feature_group: property_transaction
- anchor_run_id: 20260507-000930-deepen-numeric_plus_basic_cats
- status: keep
- cv_mae: 53716.08787165639
- cv_mae_std: 5057.265049319357
- runtime_seconds: 18.252606200010632
- change_from_previous: single_knob=drop_ohe
- hypothesis: Deepen iter10: drop OHE cats; rely solely on target_enc + presence_flags for cat signal. Simplification test: target_enc carries the same signal as OHE for tree splits.
- observation: Dropping OHE actually IMPROVED CV MAE -224 to 53716.09 in 18.3s. Confirms OHE was redundant once target_enc is present; OHE's many sparse columns were diluting the per-split max_features=sqrt random pool.
- comparison: vs iter9 (53939.82 +/- 5161.08) -> -223.74. vs HGB iter21 50934.78 -> +2781. vs xgboost confirm 49827.48 -> +3889.
- significance: Pooled-std vs iter9 = sqrt((5161.08^2+5057.27^2)/2) ~= 5109, threshold (0.25x) ~= 1277; |Delta| 224 << 1277 -> WITHIN NOISE; tie. Keep simplification; new family low.
- attribution: one-knob: USE_OHE=False; rest unchanged.
- next_hypothesis: STAGE 2 GATE SATISFIED (10 deepen iters). Best deepen recipe = log1p target + ratios + commune_te + cadastral_te + commune_freq + property_type_te + transaction_type_te + presence_flags (no OHE). Enter Stage 3 tune: single-knob hyperparameter sweeps starting with criterion="absolute_error" (loss-metric alignment, biggest expected lift), then n_estimators, max_depth, min_samples_leaf, max_features. 10+ iters needed.

## 20260507-001214-deepen-numeric_plus_basic_cats

- stage: deepen
- feature_lane: numeric_plus_basic_cats
- change_kind: hyperparameter
- hypothesis_unit: criterion_absolute_error
- feature_group: loss_alignment
- anchor_run_id: 20260507-001053-deepen-numeric_plus_basic_cats
- status: keep
- cv_mae: 52688.63016186476
- cv_mae_std: 5089.047706090005
- runtime_seconds: 76.17260889998579
- change_from_previous: single_knob=criterion_absolute_error
- stage_correction: tune (CLI recorded "deepen" by default; this is functionally Stage 3 tune iter1).
- hypothesis: Tune iter1: criterion=absolute_error -- direct loss-metric alignment for sklearn RF.
- observation: criterion=absolute_error dropped CV MAE -1027 to 52688.63 in 76s (4.2x slower than squared_error baseline 18.3s). Loss alignment paid off; new family low. Less slowdown than feared (predicted ~10x).
- comparison: vs deepen iter10 (53716.09 +/- 5057.27) -> -1027.46. vs HGB iter21 50934.78 -> +1754. vs xgboost confirm 49827.48 -> +2861.
- significance: Pooled-std vs deepen iter10 = sqrt((5057.27^2+5089.05^2)/2) ~= 5073, threshold (0.25x) ~= 1268; |Delta| 1027 < 1268 -> WITHIN NOISE; tie. New family low though, and the lift trend is cumulative with ratios+geo_te+log1p+criterion making >7000 cumulative gain over smoke. Keep.
- attribution: one-knob: criterion swap from "squared_error" to "absolute_error".
- next_hypothesis: Tune iter2: n_estimators=500 (more trees, better averaging). Will also slow runtime ~2.5x but should reduce variance and tighten CV mean estimate.

## 20260507-001442-deepen-numeric_plus_basic_cats

- stage: deepen
- feature_lane: numeric_plus_basic_cats
- change_kind: hyperparameter
- hypothesis_unit: n_estimators_500
- feature_group: capacity
- anchor_run_id: 20260507-001214-deepen-numeric_plus_basic_cats
- status: keep
- cv_mae: 52630.892352328556
- cv_mae_std: 5122.855965872652
- runtime_seconds: 172.86690370000724
- change_from_previous: single_knob=n_est500
- stage_correction: tune (Stage 3 tune iter2).
- hypothesis: Tune iter2: n_estimators=500 (was 200). More trees -> tighter averaging.
- observation: n_est=500 dropped CV MAE only -57 to 52630.89 in 173s (2.3x slowdown for negligible gain). RF averaging plateau around 200 trees on this dataset.
- comparison: vs tune iter1 (52688.63 +/- 5089.05) -> -57.74. vs HGB iter21 50934.78 -> +1696.
- significance: Pooled-std vs tune iter1 = sqrt((5089.05^2+5122.86^2)/2) ~= 5106, threshold (0.25x) ~= 1276; |Delta| 58 << 1276 -> WITHIN NOISE; tie. Not worth 2.3x runtime cost. REVERT n_est to 200 in next iter.
- attribution: one-knob: n_est 200->500.
- next_hypothesis: REVERT n_est=200. Tune iter3: max_depth=None (unlimited depth). xgboost found max_depth=6 best at log+ratios; RF is structurally different (averaging weaker than boosting), may benefit from deeper unrestricted trees.

## 20260507-001822-deepen-numeric_plus_basic_cats

- stage: deepen
- feature_lane: numeric_plus_basic_cats
- change_kind: hyperparameter
- hypothesis_unit: max_depth_none
- feature_group: capacity
- anchor_run_id: 20260507-001214-deepen-numeric_plus_basic_cats
- status: keep
- cv_mae: 52467.122797858625
- cv_mae_std: 5107.172303974341
- runtime_seconds: 78.87662019999698
- change_from_previous: single_knob=max_depth_none
- stage_correction: tune (Stage 3 tune iter3).
- hypothesis: Tune iter3: max_depth=None (unlimited), reverted n_est to 200. Test if RF wants deeper unrestricted trees on log-target signal-rich recipe.
- observation: max_depth=None dropped CV MAE -222 to 52467.12 in 78.9s. New family low. With min_samples_leaf=2 still preventing pure overfitting, deeper trees help RF capture finer commune_te interaction patterns.
- comparison: vs tune iter1 (52688.63 +/- 5089.05) -> -221.51. vs HGB iter21 50934.78 -> +1532. vs xgboost confirm 49827.48 -> +2640.
- significance: Pooled-std vs tune iter1 = sqrt((5089.05^2+5107.17^2)/2) ~= 5098, threshold (0.25x) ~= 1275; |Delta| 222 << 1275 -> WITHIN NOISE; tie but lowest MAE.
- attribution: one-knob: max_depth 18->None.
- next_hypothesis: Tune iter4: min_samples_leaf=1 (was 2). With max_depth=None and mls=2, trees stop at 2-sample leaves; mls=1 lets them go to 1-sample, increasing capacity but also overfitting risk. With log target this might help.

## 20260507-002028-deepen-numeric_plus_basic_cats

- stage: deepen
- feature_lane: numeric_plus_basic_cats
- change_kind: hyperparameter
- hypothesis_unit: min_samples_leaf_1
- feature_group: capacity
- anchor_run_id: 20260507-001822-deepen-numeric_plus_basic_cats
- status: keep
- cv_mae: 52817.51747549382
- cv_mae_std: 5167.958500265736
- runtime_seconds: 87.47083310000016
- change_from_previous: single_knob=mls1
- stage_correction: tune (Stage 3 tune iter4).
- hypothesis: Tune iter4: min_samples_leaf=1 -- max capacity per tree.
- observation: mls=1 regressed +350 to 52817.52 in 87.5s. Single-sample leaves overfit; bagging alone cannot recover. mls=2 is the sweet spot.
- comparison: vs tune iter3 (52467.12 +/- 5107.17) -> +350.40. vs HGB iter21 50934.78 -> +1883.
- significance: Pooled-std vs iter3 = sqrt((5107.17^2+5167.96^2)/2) ~= 5138, threshold (0.25x) ~= 1284; |Delta| 350 << 1284 -> WITHIN NOISE; small regress. REVERT mls to 2.
- attribution: one-knob: mls 2->1.
- next_hypothesis: REVERT mls=2. Tune iter5: max_features=0.5 (was sqrt~=0.16). More features per split should let trees find stronger commune_te+ratio combinations.

## 20260507-002240-deepen-numeric_plus_basic_cats

- stage: deepen
- feature_lane: numeric_plus_basic_cats
- change_kind: hyperparameter
- hypothesis_unit: max_features_0_5
- feature_group: capacity
- anchor_run_id: 20260507-001822-deepen-numeric_plus_basic_cats
- status: keep
- cv_mae: 51735.626204209766
- cv_mae_std: 4968.570036687513
- runtime_seconds: 170.58139639999717
- change_from_previous: single_knob=mf0.5
- stage_correction: tune (Stage 3 tune iter5).
- hypothesis: Tune iter5: max_features=0.5 (was sqrt~=0.16). More features per split lets RF find stronger commune_te + structural interactions.
- observation: max_features=0.5 dropped CV MAE -732 to 51735.63 in 170.6s -- the biggest tune lift. With strong-signal features (commune_te, cadastral_te, log target), restricting to sqrt was starving each split of useful candidates. Runtime ~2x slower.
- comparison: vs tune iter3 (52467.12 +/- 5107.17) -> -731.49. vs HGB iter21 50934.78 -> +801. vs xgboost confirm 49827.48 -> +1908.
- significance: Pooled-std vs iter3 = sqrt((5107.17^2+4968.57^2)/2) ~= 5039, threshold (0.25x) ~= 1260; |Delta| 732 < 1260 -> WITHIN NOISE; tie but lowest. vs HGB iter21: pooled ~= 4882, threshold ~= 1221; |Delta| 801 < 1221 -> within noise of HGB iter21 -- RF now ties HGB statistically.
- attribution: one-knob: max_features sqrt -> 0.5.
- next_hypothesis: Tune iter6: max_features=0.7 -- push capacity further to see if monotonic gain continues.

## 20260507-002621-deepen-numeric_plus_basic_cats

- stage: deepen
- feature_lane: numeric_plus_basic_cats
- change_kind: hyperparameter
- hypothesis_unit: max_features_0_7
- feature_group: capacity
- anchor_run_id: 20260507-002240-deepen-numeric_plus_basic_cats
- status: keep
- cv_mae: 51790.62261097178
- cv_mae_std: 4998.576552286635
- runtime_seconds: 234.4091485000099
- change_from_previous: single_knob=mf0.7
- stage_correction: tune (Stage 3 tune iter6).
- hypothesis: Tune iter6: max_features=0.7 -- push past 0.5 for more capacity.
- observation: max_features=0.7 tied iter5 at 51790.62 (+55) in 234s. mf=0.5 is at the lift plateau; 0.7 adds runtime without lift.
- comparison: vs tune iter5 (51735.63 +/- 4968.57) -> +55. vs HGB iter21 50934.78 -> +856.
- significance: Pooled-std vs iter5 = sqrt((4968.57^2+4998.58^2)/2) ~= 4984, threshold (0.25x) ~= 1246; |Delta| 55 << 1246 -> WITHIN NOISE; tie. mf=0.5 retained.
- attribution: one-knob: max_features 0.5 -> 0.7.
- next_hypothesis: REVERT mf=0.5. Tune iter7: bootstrap=False -- pasting (no replacement) often beats bagging when training set is small relative to model capacity.

## 20260507-003114-deepen-numeric_plus_basic_cats

- stage: deepen
- feature_lane: numeric_plus_basic_cats
- change_kind: hyperparameter
- hypothesis_unit: bootstrap_false
- feature_group: averaging
- anchor_run_id: 20260507-002240-deepen-numeric_plus_basic_cats
- status: keep
- cv_mae: 51173.890738531554
- cv_mae_std: 4772.785533704006
- runtime_seconds: 266.65086779999547
- change_from_previous: single_knob=bootstrap_false
- stage_correction: tune (Stage 3 tune iter7).
- hypothesis: Tune iter7: bootstrap=False -- "pasting": each tree sees the full training set, max_features randomness alone provides diversity.
- observation: bootstrap=False dropped CV MAE -562 to 51173.89 in 266.7s. Big lift; std also tightened (4969 -> 4773). Each tree sees ~30k full train samples (not ~63% bagged) so per-tree signal is sharper; mf=0.5 still gives enough inter-tree diversity. New family low.
- comparison: vs tune iter5 (51735.63 +/- 4968.57) -> -561.74. vs HGB iter21 50934.78 -> +239. vs xgboost confirm 49827.48 -> +1346.
- significance: Pooled-std vs iter5 = sqrt((4968.57^2+4772.79^2)/2) ~= 4872, threshold (0.25x) ~= 1218; |Delta| 562 < 1218 -> WITHIN NOISE; tie but lowest. vs HGB iter21: pooled ~= 4784, threshold ~= 1196; |Delta| 239 << 1196 -> tie with HGB iter21. RF now matches HGB iter21 statistically.
- attribution: one-knob: bootstrap True->False.
- next_hypothesis: Tune iter8: max_samples=0.8 (not applicable when bootstrap=False) -- skip. Try max_features=0.4 instead -- pull back slightly to see if tightening helps.

## 20260507-003626-deepen-numeric_plus_basic_cats

- stage: deepen
- feature_lane: numeric_plus_basic_cats
- change_kind: hyperparameter
- hypothesis_unit: max_features_0_4
- feature_group: capacity
- anchor_run_id: 20260507-003114-deepen-numeric_plus_basic_cats
- status: keep
- cv_mae: 51096.09939581265
- cv_mae_std: 4727.8442159750775
- runtime_seconds: 208.90919220000796
- change_from_previous: single_knob=mf0.4
- stage_correction: tune (Stage 3 tune iter8).
- hypothesis: Tune iter8: max_features=0.4 -- pull back slightly from 0.5 (with bootstrap=False trees benefit from a touch more inter-tree variance).
- observation: mf=0.4 dropped CV MAE -78 to 51096.10 in 209s. Tiny lift, runtime modestly faster. New family low.
- comparison: vs tune iter7 (51173.89 +/- 4772.79) -> -77.79. vs HGB iter21 50934.78 -> +161.32. vs xgboost confirm 49827.48 -> +1268.
- significance: Pooled-std vs iter7 = sqrt((4772.79^2+4727.84^2)/2) ~= 4750, threshold (0.25x) ~= 1188; |Delta| 78 << 1188 -> WITHIN NOISE; tie but lowest MAE. vs HGB iter21: |Delta| 161 well within noise -> tie with global champion family.
- attribution: one-knob: max_features 0.5 -> 0.4.
- next_hypothesis: Tune iter9: smooth=10 for target encodings (smaller smoothing = more weight to per-commune empirical mean). With log target the per-commune mean is more stable so less smoothing may help.

## 20260507-004037-deepen-numeric_plus_basic_cats

- stage: deepen
- feature_lane: numeric_plus_basic_cats
- change_kind: preprocessing
- hypothesis_unit: target_enc_smooth10
- feature_group: encoding
- anchor_run_id: 20260507-003626-deepen-numeric_plus_basic_cats
- status: keep
- cv_mae: 51017.1926377841
- cv_mae_std: 4700.916174736885
- runtime_seconds: 208.6579228000046
- change_from_previous: single_knob=smooth10
- stage_correction: tune (Stage 3 tune iter9).
- hypothesis: Tune iter9: target_enc smooth=10 (was 20). Less smoothing -> more weight on per-commune empirical mean; fine when log target stabilizes per-commune variance.
- observation: smooth=10 dropped CV MAE -79 to 51017.19 in 209s. Tiny lift; new family low.
- comparison: vs tune iter8 (51096.10 +/- 4727.84) -> -78.91. vs HGB iter21 50934.78 -> +82.41. vs xgboost confirm 49827.48 -> +1190.
- significance: Pooled-std vs iter8 = sqrt((4727.84^2+4700.92^2)/2) ~= 4714, threshold (0.25x) ~= 1179; |Delta| 79 << 1179 -> WITHIN NOISE; tie but lowest MAE. Now within 82 MAE of HGB iter21 -- effectively tied.
- attribution: one-knob: TARGET_ENC_SMOOTH 20->10.
- next_hypothesis: Tune iter10: target_enc smooth=5 -- push further to test direction. If still helping, marginal; if hurts, smooth=10 is the sweet spot.

## 20260507-004448-deepen-numeric_plus_basic_cats

- stage: deepen
- feature_lane: numeric_plus_basic_cats
- change_kind: preprocessing
- hypothesis_unit: target_enc_smooth5
- feature_group: encoding
- anchor_run_id: 20260507-004037-deepen-numeric_plus_basic_cats
- status: keep
- cv_mae: 51026.89579363486
- cv_mae_std: 4637.322503846682
- runtime_seconds: 205.7070715000009
- change_from_previous: single_knob=smooth5
- stage_correction: tune (Stage 3 tune iter10).
- hypothesis: Tune iter10: target_enc smooth=5 (was 10).
- observation: smooth=5 tied iter9 at 51026.90 (+10) in 205.7s. smooth=10 retained as best.
- comparison: vs tune iter9 (51017.19 +/- 4700.92) -> +9.70.
- significance: Pooled-std ~= 4669, threshold ~= 1167; |Delta| 10 << 1167 -> WITHIN NOISE; tie.
- attribution: one-knob: TARGET_ENC_SMOOTH 10->5.
- next_hypothesis: STAGE 3 GATE SATISFIED (10 tune iters). REVERT smooth to 10. Enter Stage 3b ablate. W=tune iter9 (51017.19), B=deepen iter10 (53716.09). Knobs B->W: c1=criterion absolute_error, c2=max_depth=None, c3=max_features=0.4, c4=bootstrap=False, c5=smooth=10. c5 already shown not load-bearing (smooth=20 vs 10 = +9 tie); ablate c1-c4 only.

## 20260507-004953-deepen-numeric_plus_basic_cats

- stage: deepen
- feature_lane: numeric_plus_basic_cats
- change_kind: hyperparameter
- hypothesis_unit: ablate_c1_criterion
- feature_group: loss_alignment
- anchor_run_id: 20260507-004037-deepen-numeric_plus_basic_cats
- status: keep
- cv_mae: 51333.953947951224
- cv_mae_std: 4628.455345566885
- runtime_seconds: 22.510062399989692
- change_from_previous: ablate_c1=criterion_squared_error
- hypothesis: Ablate c1: revert criterion to squared_error
- observation: TODO: interpret fold/runtime signal before next action.
- comparison: TODO: compare against previous, family best, and global best.
- significance: TODO: apply pooled-std noise rule.
- attribution: one-knob work item; verify no bundled changes before promotion.
- next_hypothesis: TODO: one-knob next action or gate decision.

## 20260507-005053-deepen-numeric_plus_basic_cats

- stage: deepen
- feature_lane: numeric_plus_basic_cats
- change_kind: hyperparameter
- hypothesis_unit: ablate_c2_max_depth
- feature_group: capacity
- anchor_run_id: 20260507-004037-deepen-numeric_plus_basic_cats
- status: keep
- cv_mae: 50663.63878578683
- cv_mae_std: 4749.875803814063
- runtime_seconds: 196.184494599991
- change_from_previous: ablate_c2=max_depth_18
- hypothesis: Ablate c2: revert max_depth to 18
- observation: TODO: interpret fold/runtime signal before next action.
- comparison: TODO: compare against previous, family best, and global best.
- significance: TODO: apply pooled-std noise rule.
- attribution: one-knob work item; verify no bundled changes before promotion.
- next_hypothesis: TODO: one-knob next action or gate decision.

## 20260507-005449-deepen-numeric_plus_basic_cats

- stage: deepen
- feature_lane: numeric_plus_basic_cats
- change_kind: hyperparameter
- hypothesis_unit: ablate_c3_max_features
- feature_group: capacity
- anchor_run_id: 20260507-004037-deepen-numeric_plus_basic_cats
- status: keep
- cv_mae: 51720.36165143864
- cv_mae_std: 5028.244521029062
- runtime_seconds: 89.04543100000592
- change_from_previous: ablate_c3=mf_sqrt
- hypothesis: Ablate c3: revert max_features to sqrt
- observation: TODO: interpret fold/runtime signal before next action.
- comparison: TODO: compare against previous, family best, and global best.
- significance: TODO: apply pooled-std noise rule.
- attribution: one-knob work item; verify no bundled changes before promotion.
- next_hypothesis: TODO: one-knob next action or gate decision.

## 20260507-005647-deepen-numeric_plus_basic_cats

- stage: deepen
- feature_lane: numeric_plus_basic_cats
- change_kind: hyperparameter
- hypothesis_unit: ablate_c4_bootstrap
- feature_group: averaging
- anchor_run_id: 20260507-004037-deepen-numeric_plus_basic_cats
- status: keep
- cv_mae: 51699.42465235492
- cv_mae_std: 4994.460605561569
- runtime_seconds: 132.39151960000163
- change_from_previous: ablate_c4=bootstrap_true
- hypothesis: Ablate c4: revert bootstrap=True
- observation: TODO: interpret fold/runtime signal before next action.
- comparison: TODO: compare against previous, family best, and global best.
- significance: TODO: apply pooled-std noise rule.
- attribution: one-knob work item; verify no bundled changes before promotion.
- next_hypothesis: TODO: one-knob next action or gate decision.

## ablation_summary -- after tune iter10

- **winner W:** 20260507-004037-deepen-numeric_plus_basic_cats (tune iter9), cv_mae 51017.19 +/- 4700.92
- **prior family best B:** 20260507-001053-deepen-numeric_plus_basic_cats (deepen iter10, all features done, no tuning), cv_mae 53716.09 +/- 5057.27
- **changes from B to W (5 knobs):** c1 criterion squared_error->absolute_error, c2 max_depth 18->None, c3 max_features sqrt->0.4, c4 bootstrap True->False, c5 target_enc smooth 20->10
- **LOO results (each = W with c_i reverted to B; vs W noise band ~1166-1217):**
  - W_minus_c1 (criterion=squared_error): 51333.95, +317 -> tie (NOT load-bearing) BUT 4x faster runtime
  - W_minus_c2 (max_depth=18): 50663.64, **-354** (BETTER than W) -> max_depth=None HURTS, drop it
  - W_minus_c3 (max_features=sqrt): 51720.36, +703 -> tie (NOT strongly load-bearing, but biggest cost)
  - W_minus_c4 (bootstrap=True): 51699.42, +682 -> tie (NOT strongly load-bearing)
  - c5 already shown: smooth=20 vs smooth=10 = +9.70 -> NOT load-bearing
- **load-bearing changes:** none individually load-bearing at 0.25*pooled_std threshold; cumulative effect is real (-2699 from B)
- **harmful changes:** c2 (max_depth=None) -- ablating it gives -354 below W
- **promoted recipe:** W minus c2 (max_depth=18 instead of None), keep c1+c3+c4+c5. Family best = 50663.64 +/- 4749.88 (W_minus_c2 run).
- **decision:** promote W_minus_c2 as the simplified winner. c1/c3/c4/c5 retained because each individually ties with W but cumulatively they're the gain over B; ablating c2 is the only ablation that improved on W. Beats HGB iter21 50934.78 by -271 (within noise threshold ~1193 -- statistical tie with prior global champion family).

## 20260507-010029-deepen-numeric_plus_basic_cats

- stage: deepen
- feature_lane: numeric_plus_basic_cats
- change_kind: diagnostic
- hypothesis_unit: confirm_seed2026
- feature_group: confirmation
- anchor_run_id: 20260507-005053-deepen-numeric_plus_basic_cats
- status: keep
- cv_mae: 50843.010772328045
- cv_mae_std: 4532.314570439293
- runtime_seconds: 196.8435865000065
- change_from_previous: confirm_seed2026
- hypothesis: Confirm seed=2026 of promoted simplified recipe (W minus max_depth=None)
- observation: TODO: interpret fold/runtime signal before next action.
- comparison: TODO: compare against previous, family best, and global best.
- significance: TODO: apply pooled-std noise rule.
- attribution: one-knob work item; verify no bundled changes before promotion.
- next_hypothesis: TODO: one-knob next action or gate decision.
