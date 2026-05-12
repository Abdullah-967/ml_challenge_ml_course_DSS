# xgboost_v4 Iteration Log

Append-only. One block per canonical CV run. See the bundled `plugins/model-family-mae/references/reflection_protocol.md`.

Required metadata per entry: stage, change_kind, hypothesis_unit, feature_group, anchor_run_id, change_from_previous, hypothesis, observation, comparison, significance, attribution, next_hypothesis.

## 20260507-215240-smoke-v2_plus_geo_hierarchy

- stage: smoke
- feature_lane: v2_plus_geo_hierarchy
- change_kind: feature
- hypothesis_unit: dept_region_native_cats
- feature_group: geography
- anchor_run_id: n/a
- status: keep
- cv_mae: 49111.52847980654
- cv_mae_std: 4975.370853959067
- runtime_seconds: 43.246474300016416
- change_from_previous: smoke_laneA_dept_region_cats
- hypothesis: Smoke Lane A: v2 base + dept_code (native cat) + region_code (native cat). Tests whether geographic hierarchy above commune adds signal not captured by commune_first cat alone.
- observation: pending: interpret fold/runtime signal before next action.
- comparison: pending: compare against previous, family best, and global best.
- significance: pending: apply pooled-std noise rule.
- attribution: one-knob work item; verify no bundled changes before promotion.
- next_hypothesis: pending: one-knob next action or gate decision.

## 20260507-215422-smoke-v2_plus_temporal_cats

- stage: smoke
- feature_lane: v2_plus_temporal_cats
- change_kind: feature
- hypothesis_unit: year_month_future_sale
- feature_group: temporal
- anchor_run_id: n/a
- status: revert
- cv_mae: 49343.363936814145
- cv_mae_std: 4921.882504418601
- runtime_seconds: 40.7212329999893
- change_from_previous: smoke_laneB_temporal_cats
- hypothesis: Smoke Lane B: v2 base + year (native cat) + month (native cat) + future_sale (numeric). Tests temporal granularity beyond date_ordinal.
- observation: pending: interpret fold/runtime signal before next action.
- comparison: pending: compare against previous, family best, and global best.
- significance: pending: apply pooled-std noise rule.
- attribution: one-knob work item; verify no bundled changes before promotion.
- next_hypothesis: pending: one-knob next action or gate decision.

## 20260507-215605-smoke-v2_plus_fold_te

- stage: smoke
- feature_lane: v2_plus_fold_te
- change_kind: feature
- hypothesis_unit: fold_safe_commune_te30
- feature_group: geography_te
- anchor_run_id: n/a
- status: revert
- cv_mae: 49505.39206268833
- cv_mae_std: 4921.569910062281
- runtime_seconds: 37.68759719998343
- change_from_previous: smoke_laneC_fold_te30
- hypothesis: Smoke Lane C: v2 base + fold-safe target encoding on commune_first (smooth=30). TE computed on train fold only, applied to validation. Adds smoothed mean(log1p(value)) signal beyond native cat encoding.
- observation: pending: interpret fold/runtime signal before next action.
- comparison: pending: compare against previous, family best, and global best.
- significance: pending: apply pooled-std noise rule.
- attribution: one-knob work item; verify no bundled changes before promotion.
- next_hypothesis: pending: one-knob next action or gate decision.

## 20260507-215826-deepen-v2_plus_geo_hierarchy

- stage: deepen
- feature_lane: v2_plus_geo_hierarchy
- change_kind: feature
- hypothesis_unit: geo_count_features
- feature_group: geography_counts
- anchor_run_id: 20260507-215240-smoke-v2_plus_geo_hierarchy
- status: revert
- cv_mae: 49173.36111639334
- cv_mae_std: 4989.365310530165
- runtime_seconds: 39.644306200003484
- change_from_previous: deepen_iter1_geo_counts
- hypothesis: Deepen iter1: add num_communes, num_sections, num_parcels (geographic granularity counts). Single idea: properties spanning multiple geographic units may have different value distributions.
- observation: pending: interpret fold/runtime signal before next action.
- comparison: pending: compare against previous, family best, and global best.
- significance: pending: apply pooled-std noise rule.
- attribution: one-knob work item; verify no bundled changes before promotion.
- next_hypothesis: pending: one-knob next action or gate decision.

## 20260507-220033-deepen-v2_plus_geo_hierarchy

- stage: deepen
- feature_lane: v2_plus_geo_hierarchy
- change_kind: feature
- hypothesis_unit: dept_te_fold_safe
- feature_group: geography_te
- anchor_run_id: 20260507-215240-smoke-v2_plus_geo_hierarchy
- status: revert
- cv_mae: 49354.93376944717
- cv_mae_std: 4778.189697728564
- runtime_seconds: 39.831907999992836
- change_from_previous: deepen_iter2_dept_te20
- hypothesis: Deepen iter2: add fold-safe dept-level TE (smooth=20). 96 dept levels = much more reliable than 36k commune levels; commune TE failed but dept TE may aggregate signal at the right granularity.
- observation: pending: interpret fold/runtime signal before next action.
- comparison: pending: compare against previous, family best, and global best.
- significance: pending: apply pooled-std noise rule.
- attribution: one-knob work item; verify no bundled changes before promotion.
- next_hypothesis: pending: one-knob next action or gate decision.

## 20260507-220239-deepen-v2_plus_geo_hierarchy

- stage: deepen
- feature_lane: v2_plus_geo_hierarchy
- change_kind: feature
- hypothesis_unit: built_per_land_ratio
- feature_group: derived_ratios
- anchor_run_id: 20260507-215240-smoke-v2_plus_geo_hierarchy
- status: keep
- cv_mae: 48995.7063068141
- cv_mae_std: 4856.334854204683
- runtime_seconds: 38.31473179999739
- change_from_previous: deepen_iter3_built_per_land
- hypothesis: Deepen iter3: add built_per_land = built_area/land_area (terrain density). Trees struggle with explicit ratios; this captures urban-vs-rural density even when both inputs are present.
- observation: pending: interpret fold/runtime signal before next action.
- comparison: pending: compare against previous, family best, and global best.
- significance: pending: apply pooled-std noise rule.
- attribution: one-knob work item; verify no bundled changes before promotion.
- next_hypothesis: pending: one-knob next action or gate decision.

## 20260507-220411-deepen-v2_plus_geo_hierarchy

- stage: deepen
- feature_lane: v2_plus_geo_hierarchy
- change_kind: feature
- hypothesis_unit: total_rooms
- feature_group: derived_aggregates
- anchor_run_id: 20260507-220239-deepen-v2_plus_geo_hierarchy
- status: revert
- cv_mae: 49002.776662187556
- cv_mae_std: 5037.333167720818
- runtime_seconds: 44.47224119998282
- change_from_previous: deepen_iter4_total_rooms
- hypothesis: Deepen iter4: add total_rooms = sum of all num_*_rooms columns. Different size proxy than area features.
- observation: pending: interpret fold/runtime signal before next action.
- comparison: pending: compare against previous, family best, and global best.
- significance: pending: apply pooled-std noise rule.
- attribution: one-knob work item; verify no bundled changes before promotion.
- next_hypothesis: pending: one-knob next action or gate decision.

## 20260507-220558-deepen-v2_plus_geo_hierarchy

- stage: deepen
- feature_lane: v2_plus_geo_hierarchy
- change_kind: feature
- hypothesis_unit: built_relative_to_type_mean
- feature_group: group_aggregates
- anchor_run_id: 20260507-220239-deepen-v2_plus_geo_hierarchy
- status: keep
- cv_mae: 48750.97281865328
- cv_mae_std: 5086.0908388036605
- runtime_seconds: 39.60768200000166
- change_from_previous: deepen_iter5_built_rel_type
- hypothesis: Deepen iter5: add fold-safe built_rel_type = built_area / mean(built_area|property_type) computed from train. Measures property size relative to type norm.
- observation: pending: interpret fold/runtime signal before next action.
- comparison: pending: compare against previous, family best, and global best.
- significance: pending: apply pooled-std noise rule.
- attribution: one-knob work item; verify no bundled changes before promotion.
- next_hypothesis: pending: one-knob next action or gate decision.

## 20260507-220755-deepen-v2_plus_geo_hierarchy

- stage: deepen
- feature_lane: v2_plus_geo_hierarchy
- change_kind: feature
- hypothesis_unit: built_relative_to_commune_mean
- feature_group: group_aggregates
- anchor_run_id: 20260507-220558-deepen-v2_plus_geo_hierarchy
- status: revert
- cv_mae: 49242.50034998362
- cv_mae_std: 4916.367987889474
- runtime_seconds: 38.881374999997206
- change_from_previous: deepen_iter6_built_rel_commune
- hypothesis: Deepen iter6: add fold-safe built_rel_commune = built_area / mean(built_area|commune_first). Measures size relative to local market norm.
- observation: pending: interpret fold/runtime signal before next action.
- comparison: pending: compare against previous, family best, and global best.
- significance: pending: apply pooled-std noise rule.
- attribution: one-knob work item; verify no bundled changes before promotion.
- next_hypothesis: pending: one-knob next action or gate decision.

## 20260507-220939-deepen-v2_plus_geo_hierarchy

- stage: deepen
- feature_lane: v2_plus_geo_hierarchy
- change_kind: feature
- hypothesis_unit: built_relative_to_dept_mean
- feature_group: group_aggregates
- anchor_run_id: 20260507-220558-deepen-v2_plus_geo_hierarchy
- status: revert
- cv_mae: 49390.11934002062
- cv_mae_std: 4909.1608640967015
- runtime_seconds: 37.8819318000169
- change_from_previous: deepen_iter7_built_rel_dept
- hypothesis: Deepen iter7: add fold-safe built_rel_dept = built_area / mean(built_area|dept_code). 96 dept levels means more reliable group means than commune-level.
- observation: pending: interpret fold/runtime signal before next action.
- comparison: pending: compare against previous, family best, and global best.
- significance: pending: apply pooled-std noise rule.
- attribution: one-knob work item; verify no bundled changes before promotion.
- next_hypothesis: pending: one-knob next action or gate decision.

## 20260507-221123-deepen-v2_plus_geo_hierarchy

- stage: deepen
- feature_lane: v2_plus_geo_hierarchy
- change_kind: feature
- hypothesis_unit: land_rel_type
- feature_group: group_aggregates
- anchor_run_id: 20260507-220558-deepen-v2_plus_geo_hierarchy
- status: revert
- cv_mae: 49111.687894809074
- cv_mae_std: 4922.482745280399
- runtime_seconds: 42.97461020000628
- change_from_previous: deepen_iter8_land_rel_type
- hypothesis: Deepen iter8: add fold-safe land_rel_type = land_area / mean(land_area|property_type). Analogous to iter5 winner but for land area.
- observation: pending: interpret fold/runtime signal before next action.
- comparison: pending: compare against previous, family best, and global best.
- significance: pending: apply pooled-std noise rule.
- attribution: one-knob work item; verify no bundled changes before promotion.
- next_hypothesis: pending: one-knob next action or gate decision.

## 20260507-221317-deepen-v2_plus_geo_hierarchy

- stage: deepen
- feature_lane: v2_plus_geo_hierarchy
- change_kind: feature
- hypothesis_unit: property_type_te20
- feature_group: target_encoding
- anchor_run_id: 20260507-220558-deepen-v2_plus_geo_hierarchy
- status: revert
- cv_mae: 49208.416856617674
- cv_mae_std: 4914.076428971509
- runtime_seconds: 38.557882499997504
- change_from_previous: deepen_iter9_proptype_te20
- hypothesis: Deepen iter9: add fold-safe TE on property_type (smooth=20). Low cardinality (~10 types) gives stable means; trees can use the continuous TE complementarily to the cat.
- observation: pending: interpret fold/runtime signal before next action.
- comparison: pending: compare against previous, family best, and global best.
- significance: pending: apply pooled-std noise rule.
- attribution: one-knob work item; verify no bundled changes before promotion.
- next_hypothesis: pending: one-knob next action or gate decision.

## 20260507-221501-deepen-v2_plus_geo_hierarchy

- stage: deepen
- feature_lane: v2_plus_geo_hierarchy
- change_kind: feature
- hypothesis_unit: drop_dept_region_cats
- feature_group: model_simplify
- anchor_run_id: 20260507-220558-deepen-v2_plus_geo_hierarchy
- status: revert
- cv_mae: 49181.91691021415
- cv_mae_std: 5115.375392947686
- runtime_seconds: 36.97576729999855
- change_from_previous: deepen_iter10_drop_geo_hierarchy
- hypothesis: Deepen iter10: drop dept_code and region_code native cats. Test whether they're load-bearing in W''.
- observation: pending: interpret fold/runtime signal before next action.
- comparison: pending: compare against previous, family best, and global best.
- significance: pending: apply pooled-std noise rule.
- attribution: one-knob work item; verify no bundled changes before promotion.
- next_hypothesis: pending: one-knob next action or gate decision.

## 20260507-221635-deepen-v2_plus_geo_hierarchy

- stage: deepen
- feature_lane: v2_plus_geo_hierarchy
- change_kind: feature
- hypothesis_unit: house_area_rel_type
- feature_group: group_aggregates
- anchor_run_id: 20260507-220558-deepen-v2_plus_geo_hierarchy
- status: revert
- cv_mae: 49355.507787047754
- cv_mae_std: 4997.755468688103
- runtime_seconds: 45.38944739999715
- change_from_previous: deepen_iter11_house_rel_type
- hypothesis: Deepen iter11: add fold-safe house_area_rel_type = house_area / mean(house_area|property_type). Replicate iter5 winner pattern for second-most-important area feature.
- observation: pending: interpret fold/runtime signal before next action.
- comparison: pending: compare against previous, family best, and global best.
- significance: pending: apply pooled-std noise rule.
- attribution: one-knob work item; verify no bundled changes before promotion.
- next_hypothesis: pending: one-knob next action or gate decision.

## 20260507-221832-deepen-v2_plus_geo_hierarchy

- stage: deepen
- feature_lane: v2_plus_geo_hierarchy
- change_kind: preprocessing
- hypothesis_unit: ensemble_3seeds
- feature_group: ensemble
- anchor_run_id: 20260507-220558-deepen-v2_plus_geo_hierarchy
- status: revert
- cv_mae: 48682.66586717632
- cv_mae_std: 4964.278827265432
- runtime_seconds: 103.53393630002392
- change_from_previous: deepen_iter12_ensemble_3seeds
- hypothesis: Deepen iter12: predict by averaging 3 XGBoost models with seeds 42, 100, 200. Variance reduction often gives consistent small lift orthogonal to feature engineering.
- observation: pending: interpret fold/runtime signal before next action.
- comparison: pending: compare against previous, family best, and global best.
- significance: pending: apply pooled-std noise rule.
- attribution: one-knob work item; verify no bundled changes before promotion.
- next_hypothesis: pending: one-knob next action or gate decision.

## 20260507-222114-deepen-v2_plus_geo_hierarchy

- stage: deepen
- feature_lane: v2_plus_geo_hierarchy
- change_kind: hyperparameter
- hypothesis_unit: max_depth_8
- feature_group: model_capacity
- anchor_run_id: 20260507-220558-deepen-v2_plus_geo_hierarchy
- status: revert
- cv_mae: 48782.978997950304
- cv_mae_std: 5086.373793119057
- runtime_seconds: 49.57264969998505
- change_from_previous: deepen_iter13_max_depth_8
- hypothesis: Deepen iter13: max_depth=8 (vs 6). v4 has more features than v2; deeper trees may catch new interactions.
- observation: pending: interpret fold/runtime signal before next action.
- comparison: pending: compare against previous, family best, and global best.
- significance: pending: apply pooled-std noise rule.
- attribution: one-knob work item; verify no bundled changes before promotion.
- next_hypothesis: pending: one-knob next action or gate decision.

## 20260507-222309-deepen-v2_plus_geo_hierarchy

- stage: deepen
- feature_lane: v2_plus_geo_hierarchy
- change_kind: preprocessing
- hypothesis_unit: blend_log_raw_targets
- feature_group: ensemble
- anchor_run_id: 20260507-220558-deepen-v2_plus_geo_hierarchy
- status: revert
- cv_mae: 48895.985932576834
- cv_mae_std: 4834.686555363277
- runtime_seconds: 74.09865780000109
- change_from_previous: deepen_iter14_blend_log_raw
- hypothesis: Deepen iter14: predict by averaging log-target and raw-target XGBoost predictions (50/50). Different target scales = different residual structures, often additive lift.
- observation: pending: interpret fold/runtime signal before next action.
- comparison: pending: compare against previous, family best, and global best.
- significance: pending: apply pooled-std noise rule.
- attribution: one-knob work item; verify no bundled changes before promotion.
- next_hypothesis: pending: one-knob next action or gate decision.

## 20260507-222526-deepen-v2_plus_geo_hierarchy

- stage: deepen
- feature_lane: v2_plus_geo_hierarchy
- change_kind: feature
- hypothesis_unit: type_mean_built
- feature_group: group_aggregates
- anchor_run_id: 20260507-220558-deepen-v2_plus_geo_hierarchy
- status: revert
- cv_mae: 49313.35150507747
- cv_mae_std: 4960.001018498237
- runtime_seconds: 39.84119370000553
- change_from_previous: deepen_iter15_type_mean_built
- hypothesis: Deepen iter15: add type_mean_built = mean(built_area | property_type) per row, fold-safe. Direct group-stat (not ratio) telling model the typical built_area for the type.
- observation: pending: interpret fold/runtime signal before next action.
- comparison: pending: compare against previous, family best, and global best.
- significance: pending: apply pooled-std noise rule.
- attribution: one-knob work item; verify no bundled changes before promotion.
- next_hypothesis: pending: one-knob next action or gate decision.

## 20260507-222706-deepen-v2_plus_geo_hierarchy

- stage: deepen
- feature_lane: v2_plus_geo_hierarchy
- change_kind: capacity_pair
- hypothesis_unit: lr03_nest1000
- feature_group: model_capacity
- anchor_run_id: 20260507-220558-deepen-v2_plus_geo_hierarchy
- status: revert
- cv_mae: 48939.33835785744
- cv_mae_std: 5110.865558091598
- runtime_seconds: 70.46746829999029
- change_from_previous: deepen_iter16_lr03_nest1000
- hypothesis: Deepen iter16 (tune): lr=0.03 + n_est=1000. Slower learning, more iterations may extract more signal from current feature set.
- observation: pending: interpret fold/runtime signal before next action.
- comparison: pending: compare against previous, family best, and global best.
- significance: pending: apply pooled-std noise rule.
- attribution: one-knob work item; verify no bundled changes before promotion.
- next_hypothesis: pending: one-knob next action or gate decision.

## 20260507-222934-deepen-v2_plus_geo_hierarchy

- stage: deepen
- feature_lane: v2_plus_geo_hierarchy
- change_kind: preprocessing
- hypothesis_unit: early_stopping
- feature_group: model_optimization
- anchor_run_id: 20260507-220558-deepen-v2_plus_geo_hierarchy
- status: revert
- cv_mae: 49406.92913666605
- cv_mae_std: 5336.266224201862
- runtime_seconds: 52.27017419997719
- change_from_previous: deepen_iter17_early_stopping
- hypothesis: Deepen iter17: train with internal 90/10 train/eval split + early_stopping_rounds=30 + n_est=2000. Picks optimal stopping point per fold.
- observation: pending: interpret fold/runtime signal before next action.
- comparison: pending: compare against previous, family best, and global best.
- significance: pending: apply pooled-std noise rule.
- attribution: one-knob work item; verify no bundled changes before promotion.
- next_hypothesis: pending: one-knob next action or gate decision.

## 20260507-223141-deepen-v2_plus_geo_hierarchy

- stage: deepen
- feature_lane: v2_plus_geo_hierarchy
- change_kind: preprocessing
- hypothesis_unit: heterogeneous_ensemble_5
- feature_group: ensemble
- anchor_run_id: 20260507-220558-deepen-v2_plus_geo_hierarchy
- status: revert
- cv_mae: 48930.975521915985
- cv_mae_std: 5077.527710962177
- runtime_seconds: 540.9199617000122
- change_from_previous: deepen_iter18_hetero_ensemble_5
- hypothesis: Deepen iter18: 5-model heterogeneous ensemble averaging (vary max_depth, lr, subsample). Greater diversity than seed averaging.
- observation: pending: interpret fold/runtime signal before next action.
- comparison: pending: compare against previous, family best, and global best.
- significance: pending: apply pooled-std noise rule.
- attribution: one-knob work item; verify no bundled changes before promotion.
- next_hypothesis: pending: one-knob next action or gate decision.

## 20260507-224237-deepen-v2_plus_geo_hierarchy

- stage: deepen
- feature_lane: v2_plus_geo_hierarchy
- change_kind: preprocessing
- hypothesis_unit: ridge_residual_stack
- feature_group: stacking
- anchor_run_id: 20260507-220558-deepen-v2_plus_geo_hierarchy
- status: revert
- cv_mae: 88130.68012469506
- cv_mae_std: 6568.899177801657
- runtime_seconds: 864.6259515999991
- change_from_previous: deepen_iter19_ridge_residual
- hypothesis: Deepen iter19: stack Ridge regression on XGB residuals. Captures linear patterns the boosted trees miss.
- observation: pending: interpret fold/runtime signal before next action.
- comparison: pending: compare against previous, family best, and global best.
- significance: pending: apply pooled-std noise rule.
- attribution: one-knob work item; verify no bundled changes before promotion.
- next_hypothesis: pending: one-knob next action or gate decision.

## 20260507-225841-deepen-v2_plus_geo_hierarchy

- stage: deepen
- feature_lane: v2_plus_geo_hierarchy
- change_kind: feature
- hypothesis_unit: drop_cadastral_first
- feature_group: model_simplify
- anchor_run_id: 20260507-220558-deepen-v2_plus_geo_hierarchy
- status: revert
- cv_mae: 50596.765581078296
- cv_mae_std: 4870.511787327444
- runtime_seconds: 39.21381240000483
- change_from_previous: deepen_iter20_drop_cadastral_first
- hypothesis: Deepen iter20: drop cadastral_first cat. Cad sections nest within communes; may be redundant with commune_first cat.
- observation: pending: interpret fold/runtime signal before next action.
- comparison: pending: compare against previous, family best, and global best.
- significance: pending: apply pooled-std noise rule.
- attribution: one-knob work item; verify no bundled changes before promotion.
- next_hypothesis: pending: one-knob next action or gate decision.

## 20260507-230116-deepen-v2_plus_geo_hierarchy

- stage: deepen
- feature_lane: v2_plus_geo_hierarchy
- change_kind: feature
- hypothesis_unit: te_type_x_dept
- feature_group: group_aggregates_2d
- anchor_run_id: 20260507-220558-deepen-v2_plus_geo_hierarchy
- status: revert
- cv_mae: 49027.33264324498
- cv_mae_std: 4998.185258973675
- runtime_seconds: 42.904157999990275
- change_from_previous: deepen_iter21_te_type_x_dept
- hypothesis: Deepen iter21: 2D TE on (property_type, dept_code) with smoothing=30. Captures type-specific regional pricing differences.
- observation: pending: interpret fold/runtime signal before next action.
- comparison: pending: compare against previous, family best, and global best.
- significance: pending: apply pooled-std noise rule.
- attribution: one-knob work item; verify no bundled changes before promotion.
- next_hypothesis: pending: one-knob next action or gate decision.

## 20260507-230310-deepen-v2_plus_geo_hierarchy

- stage: deepen
- feature_lane: v2_plus_geo_hierarchy
- change_kind: preprocessing
- hypothesis_unit: per_type_submodels_blend
- feature_group: model_specialization
- anchor_run_id: 20260507-220558-deepen-v2_plus_geo_hierarchy
- status: keep
- cv_mae: 48597.97370262277
- cv_mae_std: 5091.152469846218
- runtime_seconds: 92.10068040000624
- change_from_previous: deepen_iter22_per_type_submodels
- hypothesis: Deepen iter22: train global + 2 per-type sub-models (UNE MAISON, UN APPARTEMENT). Predict global. For MAISON/APPARTEMENT rows, blend 0.5 global + 0.5 sub-model. Type-specific specialization.
- observation: pending: interpret fold/runtime signal before next action.
- comparison: pending: compare against previous, family best, and global best.
- significance: pending: apply pooled-std noise rule.
- attribution: one-knob work item; verify no bundled changes before promotion.
- next_hypothesis: pending: one-knob next action or gate decision.

## 20260507-230547-deepen-v2_plus_geo_hierarchy

- stage: deepen
- feature_lane: v2_plus_geo_hierarchy
- change_kind: preprocessing
- hypothesis_unit: per_type_5submodels
- feature_group: model_specialization
- anchor_run_id: 20260507-230310-deepen-v2_plus_geo_hierarchy
- status: keep
- cv_mae: 48540.94948438016
- cv_mae_std: 4913.946593092696
- runtime_seconds: 95.34548639997956
- change_from_previous: deepen_iter23_5_submodels
- hypothesis: Deepen iter23: extend per-type sub-models to top 5 types: UNE MAISON, UN APPARTEMENT, TERRAIN DE TYPE TERRE ET PRE, TERRAIN DE TYPE TAB, ACTIVITE. Same 0.5 blend.
- observation: pending: interpret fold/runtime signal before next action.
- comparison: pending: compare against previous, family best, and global best.
- significance: pending: apply pooled-std noise rule.
- attribution: one-knob work item; verify no bundled changes before promotion.
- next_hypothesis: pending: one-knob next action or gate decision.

## 20260507-230822-deepen-v2_plus_geo_hierarchy

- stage: deepen
- feature_lane: v2_plus_geo_hierarchy
- change_kind: hyperparameter
- hypothesis_unit: blend_ratio_0p7
- feature_group: ensemble_blend
- anchor_run_id: 20260507-230547-deepen-v2_plus_geo_hierarchy
- status: revert
- cv_mae: 48688.690971661286
- cv_mae_std: 4807.3515941977475
- runtime_seconds: 471.0752729999949
- change_from_previous: deepen_iter24_blend_0p7
- hypothesis: Deepen iter24: blend ratio 0.7 sub / 0.3 global (vs 0.5/0.5). Sub-models may have stronger type signal than global.
- observation: pending: interpret fold/runtime signal before next action.
- comparison: pending: compare against previous, family best, and global best.
- significance: pending: apply pooled-std noise rule.
- attribution: one-knob work item; verify no bundled changes before promotion.
- next_hypothesis: pending: one-knob next action or gate decision.

## 20260507-231709-deepen-v2_plus_geo_hierarchy

- stage: deepen
- feature_lane: v2_plus_geo_hierarchy
- change_kind: hyperparameter
- hypothesis_unit: blend_ratio_0p3
- feature_group: ensemble_blend
- anchor_run_id: 20260507-230547-deepen-v2_plus_geo_hierarchy
- status: keep
- cv_mae: 48535.54168071506
- cv_mae_std: 5006.717387222479
- runtime_seconds: 88.1125250000041
- change_from_previous: deepen_iter25_blend_0p3
- hypothesis: Deepen iter25: blend ratio 0.3 sub / 0.7 global. Less sub-model influence; global may be more reliable for type-specific patterns it already learned.
- observation: pending: interpret fold/runtime signal before next action.
- comparison: pending: compare against previous, family best, and global best.
- significance: pending: apply pooled-std noise rule.
- attribution: one-knob work item; verify no bundled changes before promotion.
- next_hypothesis: pending: one-knob next action or gate decision.

## 20260507-231946-deepen-v2_plus_geo_hierarchy

- stage: deepen
- feature_lane: v2_plus_geo_hierarchy
- change_kind: hyperparameter
- hypothesis_unit: submodel_depth_4
- feature_group: model_specialization
- anchor_run_id: 20260507-231709-deepen-v2_plus_geo_hierarchy
- status: revert
- cv_mae: 48620.86017716143
- cv_mae_std: 5051.862655140313
- runtime_seconds: 76.76542839998729
- change_from_previous: deepen_iter26_submodel_depth4
- hypothesis: Deepen iter26: sub-models trained with max_depth=4 (vs global's 6). Smaller per-type datasets benefit from more regularization.
- observation: pending: interpret fold/runtime signal before next action.
- comparison: pending: compare against previous, family best, and global best.
- significance: pending: apply pooled-std noise rule.
- attribution: one-knob work item; verify no bundled changes before promotion.
- next_hypothesis: pending: one-knob next action or gate decision.

## 20260507-232225-deepen-v2_plus_geo_hierarchy

- stage: deepen
- feature_lane: v2_plus_geo_hierarchy
- change_kind: preprocessing
- hypothesis_unit: per_type_residual_stack
- feature_group: stacking
- anchor_run_id: 20260507-231709-deepen-v2_plus_geo_hierarchy
- status: revert
- cv_mae: 48525.51402434512
- cv_mae_std: 4695.468113911864
- runtime_seconds: 82.09998270001961
- change_from_previous: deepen_iter27_per_type_residual
- hypothesis: Deepen iter27: per-type sub-models trained on RESIDUALS (target - global_pred) instead of raw target. Final pred = global + sub_residual.
- observation: pending: interpret fold/runtime signal before next action.
- comparison: pending: compare against previous, family best, and global best.
- significance: pending: apply pooled-std noise rule.
- attribution: one-knob work item; verify no bundled changes before promotion.
- next_hypothesis: pending: one-knob next action or gate decision.

## 20260507-232514-deepen-v2_plus_geo_hierarchy

- stage: deepen
- feature_lane: v2_plus_geo_hierarchy
- change_kind: preprocessing
- hypothesis_unit: per_type_log_residual
- feature_group: stacking
- anchor_run_id: 20260507-231709-deepen-v2_plus_geo_hierarchy
- status: revert
- cv_mae: 48549.605673537706
- cv_mae_std: 5165.498167467937
- runtime_seconds: 43.24549090000801
- change_from_previous: deepen_iter28_per_type_log_residual
- hypothesis: Deepen iter28: per-type sub-models train on log-residuals (log_y - log_pred_global). Combine target skewness handling with stacking.
- observation: pending: interpret fold/runtime signal before next action.
- comparison: pending: compare against previous, family best, and global best.
- significance: pending: apply pooled-std noise rule.
- attribution: one-knob work item; verify no bundled changes before promotion.
- next_hypothesis: pending: one-knob next action or gate decision.

## 20260507-232717-deepen-v2_plus_geo_hierarchy

- stage: deepen
- feature_lane: v2_plus_geo_hierarchy
- change_kind: hyperparameter
- hypothesis_unit: submodel_nest_300
- feature_group: model_specialization
- anchor_run_id: 20260507-231709-deepen-v2_plus_geo_hierarchy
- status: revert
- cv_mae: 48589.68970642162
- cv_mae_std: 4995.365757098701
- runtime_seconds: 55.983583699999144
- change_from_previous: deepen_iter29_submodel_nest300
- hypothesis: Deepen iter29: sub-models with n_est=300 (vs global's 500). Smaller per-type datasets need less capacity.
- observation: pending: interpret fold/runtime signal before next action.
- comparison: pending: compare against previous, family best, and global best.
- significance: pending: apply pooled-std noise rule.
- attribution: one-knob work item; verify no bundled changes before promotion.
- next_hypothesis: pending: one-knob next action or gate decision.

## 20260507-232950-deepen-v2_plus_geo_hierarchy

- stage: deepen
- feature_lane: v2_plus_geo_hierarchy
- change_kind: hyperparameter
- hypothesis_unit: gamma_1
- feature_group: model_regularization
- anchor_run_id: 20260507-231709-deepen-v2_plus_geo_hierarchy
- status: revert
- cv_mae: 48528.17902515482
- cv_mae_std: 5131.481286048693
- runtime_seconds: 65.32716669997899
- change_from_previous: deepen_iter30_gamma_1
- hypothesis: Deepen iter30: gamma=1.0 (vs default 0). Min split gain regularization. Untested in v2 search.
- observation: pending: interpret fold/runtime signal before next action.
- comparison: pending: compare against previous, family best, and global best.
- significance: pending: apply pooled-std noise rule.
- attribution: one-knob work item; verify no bundled changes before promotion.
- next_hypothesis: pending: one-knob next action or gate decision.

## 20260507-233219-deepen-v2_plus_geo_hierarchy

- stage: deepen
- feature_lane: v2_plus_geo_hierarchy
- change_kind: feature
- hypothesis_unit: drop_room_layout
- feature_group: model_simplify
- anchor_run_id: 20260507-231709-deepen-v2_plus_geo_hierarchy
- status: revert
- cv_mae: 48944.52494883945
- cv_mae_std: 4953.788718113701
- runtime_seconds: 62.44526609999593
- change_from_previous: deepen_iter31_drop_room_layout
- hypothesis: Deepen iter31: drop num_/area_*_rooms (18 sparse cols). May reduce noise.
- observation: pending: interpret fold/runtime signal before next action.
- comparison: pending: compare against previous, family best, and global best.
- significance: pending: apply pooled-std noise rule.
- attribution: one-knob work item; verify no bundled changes before promotion.
- next_hypothesis: pending: one-knob next action or gate decision.

## 20260507-233426-deepen-v2_plus_geo_hierarchy

- stage: deepen
- feature_lane: v2_plus_geo_hierarchy
- change_kind: preprocessing
- hypothesis_unit: global_5_bag_bootstrap
- feature_group: ensemble_bagging
- anchor_run_id: 20260507-231709-deepen-v2_plus_geo_hierarchy
- status: revert
- cv_mae: 49183.3675979111
- cv_mae_std: 5021.600618710875
- runtime_seconds: 173.2060432000144
- change_from_previous: deepen_iter32_global_5bag
- hypothesis: Deepen iter32: replace global with average of 5 XGB models on bootstrap samples (with replacement). Per-type sub-models stay same. Bootstrap diversity > seed diversity.
- observation: pending: interpret fold/runtime signal before next action.
- comparison: pending: compare against previous, family best, and global best.
- significance: pending: apply pooled-std noise rule.
- attribution: one-knob work item; verify no bundled changes before promotion.
- next_hypothesis: pending: one-knob next action or gate decision.

## 20260507-233814-deepen-v2_plus_geo_hierarchy

- stage: deepen
- feature_lane: v2_plus_geo_hierarchy
- change_kind: hyperparameter
- hypothesis_unit: n_est_1000
- feature_group: model_capacity
- anchor_run_id: 20260507-231709-deepen-v2_plus_geo_hierarchy
- status: keep
- cv_mae: 48053.743012712206
- cv_mae_std: 5046.996984934976
- runtime_seconds: 108.31127239999478
- change_from_previous: deepen_iter33_nest_1000
- hypothesis: Deepen iter33: n_estimators=1000 (vs 500), keep lr=0.05. More trees may extract more signal.
- observation: pending: interpret fold/runtime signal before next action.
- comparison: pending: compare against previous, family best, and global best.
- significance: pending: apply pooled-std noise rule.
- attribution: one-knob work item; verify no bundled changes before promotion.
- next_hypothesis: pending: one-knob next action or gate decision.

## 20260507-234057-deepen-v2_plus_geo_hierarchy

- stage: deepen
- feature_lane: v2_plus_geo_hierarchy
- change_kind: hyperparameter
- hypothesis_unit: n_est_1500
- feature_group: model_capacity
- anchor_run_id: 20260507-233814-deepen-v2_plus_geo_hierarchy
- status: keep
- cv_mae: 47770.070360295285
- cv_mae_std: 5050.264853034667
- runtime_seconds: 161.99693090000073
- change_from_previous: deepen_iter34_nest_1500
- hypothesis: Deepen iter34: n_estimators=1500 (vs 1000). More trees, see if lift continues.
- observation: pending: interpret fold/runtime signal before next action.
- comparison: pending: compare against previous, family best, and global best.
- significance: pending: apply pooled-std noise rule.
- attribution: one-knob work item; verify no bundled changes before promotion.
- next_hypothesis: pending: one-knob next action or gate decision.

## 20260507-234432-deepen-v2_plus_geo_hierarchy

- stage: deepen
- feature_lane: v2_plus_geo_hierarchy
- change_kind: hyperparameter
- hypothesis_unit: n_est_2000
- feature_group: model_capacity
- anchor_run_id: 20260507-234057-deepen-v2_plus_geo_hierarchy
- status: keep
- cv_mae: 47535.233987282394
- cv_mae_std: 5103.906676696525
- runtime_seconds: 255.45842869998887
- change_from_previous: deepen_iter35_nest_2000
- hypothesis: Deepen iter35: n_estimators=2000 (vs 1500). Continue exploring capacity ceiling.
- observation: pending: interpret fold/runtime signal before next action.
- comparison: pending: compare against previous, family best, and global best.
- significance: pending: apply pooled-std noise rule.
- attribution: one-knob work item; verify no bundled changes before promotion.
- next_hypothesis: pending: one-knob next action or gate decision.

## 20260507-234936-deepen-v2_plus_geo_hierarchy

- stage: deepen
- feature_lane: v2_plus_geo_hierarchy
- change_kind: hyperparameter
- hypothesis_unit: n_est_3000
- feature_group: model_capacity
- anchor_run_id: 20260507-234432-deepen-v2_plus_geo_hierarchy
- status: keep
- cv_mae: 47408.98292294374
- cv_mae_std: 5170.389095896964
- runtime_seconds: 377.7364202000026
- change_from_previous: deepen_iter36_nest_3000
- hypothesis: Deepen iter36: n_estimators=3000. Push trees further if lift continues.
- observation: pending: interpret fold/runtime signal before next action.
- comparison: pending: compare against previous, family best, and global best.
- significance: pending: apply pooled-std noise rule.
- attribution: one-knob work item; verify no bundled changes before promotion.
- next_hypothesis: pending: one-knob next action or gate decision.

## 20260507-235645-deepen-v2_plus_geo_hierarchy

- stage: deepen
- feature_lane: v2_plus_geo_hierarchy
- change_kind: hyperparameter
- hypothesis_unit: n_est_4000
- feature_group: model_capacity
- anchor_run_id: 20260507-234936-deepen-v2_plus_geo_hierarchy
- status: keep
- cv_mae: 47107.53266242174
- cv_mae_std: 5244.6745564521725
- runtime_seconds: 459.26972019998357
- change_from_previous: deepen_iter37_nest_4000
- hypothesis: Deepen iter37: n_estimators=4000. Test if returns continue diminishing.
- observation: pending: interpret fold/runtime signal before next action.
- comparison: pending: compare against previous, family best, and global best.
- significance: pending: apply pooled-std noise rule.
- attribution: one-knob work item; verify no bundled changes before promotion.
- next_hypothesis: pending: one-knob next action or gate decision.

## 20260508-000514-deepen-v2_plus_geo_hierarchy

- stage: deepen
- feature_lane: v2_plus_geo_hierarchy
- change_kind: hyperparameter
- hypothesis_unit: n_est_5000
- feature_group: model_capacity
- anchor_run_id: 20260507-235645-deepen-v2_plus_geo_hierarchy
- status: revert
- cv_mae: 47041.54518360952
- cv_mae_std: 5297.923104301265
- runtime_seconds: 572.1049348000088
- change_from_previous: deepen_iter38_nest_5000
- hypothesis: Deepen iter38: n_estimators=5000. Push capacity ceiling further.
- observation: pending: interpret fold/runtime signal before next action.
- comparison: pending: compare against previous, family best, and global best.
- significance: pending: apply pooled-std noise rule.
- attribution: one-knob work item; verify no bundled changes before promotion.
- next_hypothesis: pending: one-knob next action or gate decision.

## 20260508-001554-deepen-v2_plus_geo_hierarchy

- stage: deepen
- feature_lane: v2_plus_geo_hierarchy
- change_kind: capacity_pair
- hypothesis_unit: lr_0p03_nest_4000
- feature_group: model_capacity
- anchor_run_id: 20260507-235645-deepen-v2_plus_geo_hierarchy
- status: revert
- cv_mae: 48228.970189480635
- cv_mae_std: 5084.448929652903
- runtime_seconds: 405.465022999997
- change_from_previous: deepen_iter39_lr03_nest4000
- hypothesis: Deepen iter39: lr=0.03 + n_est=4000. Slower learning may extract more signal at fixed tree budget.
- observation: pending: interpret fold/runtime signal before next action.
- comparison: pending: compare against previous, family best, and global best.
- significance: pending: apply pooled-std noise rule.
- attribution: one-knob work item; verify no bundled changes before promotion.
- next_hypothesis: pending: one-knob next action or gate decision.

## 20260508-002406-deepen-v2_plus_geo_hierarchy

- stage: deepen
- feature_lane: v2_plus_geo_hierarchy
- change_kind: hyperparameter
- hypothesis_unit: max_depth_8
- feature_group: model_capacity
- anchor_run_id: 20260507-235645-deepen-v2_plus_geo_hierarchy
- status: revert
- cv_mae: 48381.67854013095
- cv_mae_std: 4867.08524421596
- runtime_seconds: 516.5542075000121
- change_from_previous: deepen_iter40_depth_8
- hypothesis: Deepen iter40: max_depth=8 with n_est=4000. Test depth at higher tree count.
- observation: pending: interpret fold/runtime signal before next action.
- comparison: pending: compare against previous, family best, and global best.
- significance: pending: apply pooled-std noise rule.
- attribution: one-knob work item; verify no bundled changes before promotion.
- next_hypothesis: pending: one-knob next action or gate decision.

## 20260508-002700-ablate-v2_plus_geo_hierarchy

- stage: ablate
- feature_lane: v2_plus_geo_hierarchy
- change_kind: diagnostic
- hypothesis_unit: ablate_submodels
- feature_group: ablation
- anchor_run_id: 20260507-235645-deepen-v2_plus_geo_hierarchy
- status: ablate
- cv_mae: 47392.2161547835
- cv_mae_std: 5328.153530651825
- runtime_seconds: 176.2535659999994
- change_from_previous: ablate_a1_drop_submodels
- hypothesis: Ablate a1: drop per-type sub-models (no SUB_TYPES). Test if the per-type architecture is load-bearing in W'''''.
- observation: pending: interpret fold/runtime signal before next action.
- comparison: pending: compare against previous, family best, and global best.
- significance: pending: apply pooled-std noise rule.
- attribution: one-knob work item; verify no bundled changes before promotion.
- next_hypothesis: pending: one-knob next action or gate decision.

## 20260508-003012-confirm-v2_plus_geo_hierarchy

- stage: confirm
- feature_lane: v2_plus_geo_hierarchy
- change_kind: diagnostic
- hypothesis_unit: seed_confirm
- feature_group: validation
- anchor_run_id: 20260507-235645-deepen-v2_plus_geo_hierarchy
- status: confirm
- cv_mae: 47998.49109195428
- cv_mae_std: 3831.8809582546296
- runtime_seconds: 408.43418770001153
- change_from_previous: confirm_seed2026
- hypothesis: Stage 4 confirm seed=2026 of W''''' (iter37 winner: per-type sub-models + n_est=4000 + all kept knobs). Validate seed agreement before promotion.
- observation: pending: interpret fold/runtime signal before next action.
- comparison: pending: compare against previous, family best, and global best.
- significance: pending: apply pooled-std noise rule.
- attribution: one-knob work item; verify no bundled changes before promotion.
- next_hypothesis: pending: one-knob next action or gate decision.
