# xgboost_v3 Iteration Log

Append-only. One block per canonical CV run. See the bundled `plugins/model-family-mae/references/reflection_protocol.md`.

Required metadata per entry: stage, change_kind, hypothesis_unit, feature_group, anchor_run_id, change_from_previous, hypothesis, observation, comparison, significance, attribution, next_hypothesis.

## 20260507-211730-smoke-baseline_three_only

- stage: smoke
- feature_lane: baseline_three_only
- change_kind: feature
- hypothesis_unit: baseline_three_features
- feature_group: structural_minimal
- anchor_run_id: n/a
- status: keep
- cv_mae: 62517.14795512785
- cv_mae_std: 4529.718975639667
- runtime_seconds: 21.386237099999562
- change_from_previous: smoke_iter1_baseline_three_only
- hypothesis: Smoke iter1: XGBoost on ONLY the Ridge baseline's 3 features (built_area, num_lots, num_commercial). Family premise -- the hypothesis IS the feature set, so a single smoke lane is correct here; multi-lane smoke would defeat the purpose of testing this exact constraint. Compare CV MAE vs xgboost_v2 promoted (49247) and Ridge baseline.
- observation: pending: interpret fold/runtime signal before next action.
- comparison: pending: compare against previous, family best, and global best.
- significance: pending: apply pooled-std noise rule.
- attribution: one-knob work item; verify no bundled changes before promotion.
- next_hypothesis: pending: one-knob next action or gate decision.

## 20260507-212215-deepen-baseline_three_only

- stage: deepen
- feature_lane: baseline_three_only
- change_kind: target
- hypothesis_unit: log1p_target
- feature_group: target_transform
- anchor_run_id: 20260507-211730-smoke-baseline_three_only
- status: revert
- cv_mae: 62653.73344068973
- cv_mae_std: 4618.923422684576
- runtime_seconds: 25.42759730000398
- change_from_previous: deepen_iter1_log1p_target
- hypothesis: Deepen iter1: wrap target with log1p (expm1 inverse). xgboost_v2 found this tie-positive (-322); test if it ports under feature-starved 3-feature regime.
- observation: pending: interpret fold/runtime signal before next action.
- comparison: pending: compare against previous, family best, and global best.
- significance: pending: apply pooled-std noise rule.
- attribution: one-knob work item; verify no bundled changes before promotion.
- next_hypothesis: pending: one-knob next action or gate decision.

## 20260507-212419-deepen-baseline_three_only

- stage: deepen
- feature_lane: baseline_three_only
- change_kind: preprocessing
- hypothesis_unit: monotone_constraints
- feature_group: model_constraints
- anchor_run_id: 20260507-211730-smoke-baseline_three_only
- status: revert
- cv_mae: 64766.37274688234
- cv_mae_std: 4383.116797265103
- runtime_seconds: 24.668069700011984
- change_from_previous: deepen_iter2_monotone_constraints
- hypothesis: Deepen iter2: monotone_constraints={built_area:+1, num_lots:+1, num_commercial:+1}. Domain knowledge: more area/lots/commercial units => higher value. Should reduce overfitting noise when the model is feature-starved.
- observation: pending: interpret fold/runtime signal before next action.
- comparison: pending: compare against previous, family best, and global best.
- significance: pending: apply pooled-std noise rule.
- attribution: one-knob work item; verify no bundled changes before promotion.
- next_hypothesis: pending: one-knob next action or gate decision.

## 20260507-212614-deepen-baseline_three_only

- stage: deepen
- feature_lane: baseline_three_only
- change_kind: target
- hypothesis_unit: target_clip_99p5
- feature_group: target_transform
- anchor_run_id: 20260507-211730-smoke-baseline_three_only
- status: revert
- cv_mae: 62496.041697297514
- cv_mae_std: 4704.809125413401
- runtime_seconds: 30.619018500001403
- change_from_previous: deepen_iter3_target_clip_99p5
- hypothesis: Deepen iter3: clip y_train at 99.5th percentile during fit (cap extreme outliers); MAE eval still uses raw y. Tail outliers may be hurting MAE in feature-starved 3-feature regime.
- observation: pending: interpret fold/runtime signal before next action.
- comparison: pending: compare against previous, family best, and global best.
- significance: pending: apply pooled-std noise rule.
- attribution: one-knob work item; verify no bundled changes before promotion.
- next_hypothesis: pending: one-knob next action or gate decision.

## 20260507-212746-deepen-baseline_three_only

- stage: deepen
- feature_lane: baseline_three_only
- change_kind: hyperparameter
- hypothesis_unit: max_depth_4
- feature_group: model_capacity
- anchor_run_id: 20260507-211730-smoke-baseline_three_only
- status: keep
- cv_mae: 62450.70419487223
- cv_mae_std: 4612.418798589422
- runtime_seconds: 29.45780800000648
- change_from_previous: deepen_iter4_max_depth_4
- hypothesis: Deepen iter4 (capacity-knob): max_depth=4 (vs 6). With 3 features, depth-6 trees may overfit interactions. Less capacity = stronger generalization in feature-starved regime.
- observation: pending: interpret fold/runtime signal before next action.
- comparison: pending: compare against previous, family best, and global best.
- significance: pending: apply pooled-std noise rule.
- attribution: one-knob work item; verify no bundled changes before promotion.
- next_hypothesis: pending: one-knob next action or gate decision.

## 20260507-213035-deepen-baseline_three_only

- stage: deepen
- feature_lane: baseline_three_only
- change_kind: capacity_pair
- hypothesis_unit: lr03_nest1000
- feature_group: model_capacity
- anchor_run_id: 20260507-212746-deepen-baseline_three_only
- status: revert
- cv_mae: 62479.879280996494
- cv_mae_std: 4381.991505252917
- runtime_seconds: 48.3679509999929
- change_from_previous: deepen_iter5_lr03_nest1000
- hypothesis: Deepen iter5: lr=0.03 + n_est=1000 (capacity-pair, slower learning, more trees). Helps converge to a finer optimum on a feature-starved 3-feature problem.
- observation: pending: interpret fold/runtime signal before next action.
- comparison: pending: compare against previous, family best, and global best.
- significance: pending: apply pooled-std noise rule.
- attribution: one-knob work item; verify no bundled changes before promotion.
- next_hypothesis: pending: one-knob next action or gate decision.

## 20260507-213211-deepen-baseline_three_only

- stage: deepen
- feature_lane: baseline_three_only
- change_kind: hyperparameter
- hypothesis_unit: colsample_full
- feature_group: model_sampling
- anchor_run_id: 20260507-212746-deepen-baseline_three_only
- status: keep
- cv_mae: 62402.51738046277
- cv_mae_std: 4558.998043525508
- runtime_seconds: 31.53268659999594
- change_from_previous: deepen_iter6_colsample_full
- hypothesis: Deepen iter6: colsample_bytree=1.0 (vs 0.8). With only 3 features, 0.8 samples ~2 cols/tree = throws away info every tree.
- observation: pending: interpret fold/runtime signal before next action.
- comparison: pending: compare against previous, family best, and global best.
- significance: pending: apply pooled-std noise rule.
- attribution: one-knob work item; verify no bundled changes before promotion.
- next_hypothesis: pending: one-knob next action or gate decision.

## 20260507-213339-deepen-baseline_three_only

- stage: deepen
- feature_lane: baseline_three_only
- change_kind: hyperparameter
- hypothesis_unit: subsample_full
- feature_group: model_sampling
- anchor_run_id: 20260507-213211-deepen-baseline_three_only
- status: revert
- cv_mae: 62515.9551895547
- cv_mae_std: 4474.297275841361
- runtime_seconds: 36.55469419999281
- change_from_previous: deepen_iter7_subsample_full
- hypothesis: Deepen iter7: subsample=1.0 (vs 0.8). Drop row-sampling randomness; with feature-starved 3 cols the variance from sampling may not pay for itself.
- observation: pending: interpret fold/runtime signal before next action.
- comparison: pending: compare against previous, family best, and global best.
- significance: pending: apply pooled-std noise rule.
- attribution: one-knob work item; verify no bundled changes before promotion.
- next_hypothesis: pending: one-knob next action or gate decision.

## 20260507-213501-deepen-baseline_three_only

- stage: deepen
- feature_lane: baseline_three_only
- change_kind: hyperparameter
- hypothesis_unit: max_depth_3
- feature_group: model_capacity
- anchor_run_id: 20260507-213211-deepen-baseline_three_only
- status: keep
- cv_mae: 62365.37148419507
- cv_mae_std: 4525.38242005847
- runtime_seconds: 32.312174899998354
- change_from_previous: deepen_iter8_max_depth_3
- hypothesis: Deepen iter8: max_depth=3 (vs 4). Push Occam direction further -- with 3 features depth 3 may regularize even better.
- observation: pending: interpret fold/runtime signal before next action.
- comparison: pending: compare against previous, family best, and global best.
- significance: pending: apply pooled-std noise rule.
- attribution: one-knob work item; verify no bundled changes before promotion.
- next_hypothesis: pending: one-knob next action or gate decision.

## 20260507-213647-deepen-baseline_three_only

- stage: deepen
- feature_lane: baseline_three_only
- change_kind: hyperparameter
- hypothesis_unit: max_depth_2
- feature_group: model_capacity
- anchor_run_id: 20260507-213501-deepen-baseline_three_only
- status: keep
- cv_mae: 62354.50739262222
- cv_mae_std: 4564.555204551495
- runtime_seconds: 32.45371920001344
- change_from_previous: deepen_iter9_max_depth_2
- hypothesis: Deepen iter9: max_depth=2 (vs 3). Test Occam ceiling -- tiny trees, max info per split with 3 features.
- observation: pending: interpret fold/runtime signal before next action.
- comparison: pending: compare against previous, family best, and global best.
- significance: pending: apply pooled-std noise rule.
- attribution: one-knob work item; verify no bundled changes before promotion.
- next_hypothesis: pending: one-knob next action or gate decision.

## 20260507-213821-deepen-baseline_three_only

- stage: deepen
- feature_lane: baseline_three_only
- change_kind: hyperparameter
- hypothesis_unit: lr_0p1
- feature_group: model_optimization
- anchor_run_id: 20260507-213647-deepen-baseline_three_only
- status: revert
- cv_mae: 62500.85771768569
- cv_mae_std: 4503.934541247204
- runtime_seconds: 31.305395700008376
- change_from_previous: deepen_iter10_lr_0p1
- hypothesis: Deepen iter10: lr=0.1 (vs 0.05). With shallow depth=2 trees, faster learning may find a better optimum within 500 iters.
- observation: pending: interpret fold/runtime signal before next action.
- comparison: pending: compare against previous, family best, and global best.
- significance: pending: apply pooled-std noise rule.
- attribution: one-knob work item; verify no bundled changes before promotion.
- next_hypothesis: pending: one-knob next action or gate decision.

## 20260507-214129-ablate-baseline_three_only

- stage: ablate
- feature_lane: baseline_three_only
- change_kind: diagnostic
- hypothesis_unit: ablate_max_depth
- feature_group: ablation
- anchor_run_id: 20260507-213647-deepen-baseline_three_only
- status: ablate
- cv_mae: 62689.65696317666
- cv_mae_std: 4456.985345426711
- runtime_seconds: 34.576040499989176
- change_from_previous: ablate_a1_revert_max_depth
- hypothesis: Ablate a1: revert max_depth to default 6 (keep colsample=1.0). Test whether max_depth=2 was load-bearing vs W'''.
- observation: pending: interpret fold/runtime signal before next action.
- comparison: pending: compare against previous, family best, and global best.
- significance: pending: apply pooled-std noise rule.
- attribution: one-knob work item; verify no bundled changes before promotion.
- next_hypothesis: pending: one-knob next action or gate decision.

## 20260507-214312-ablate-baseline_three_only

- stage: ablate
- feature_lane: baseline_three_only
- change_kind: diagnostic
- hypothesis_unit: ablate_colsample
- feature_group: ablation
- anchor_run_id: 20260507-213647-deepen-baseline_three_only
- status: ablate
- cv_mae: 62626.24094467664
- cv_mae_std: 4390.195211933284
- runtime_seconds: 30.975452400016366
- change_from_previous: ablate_a2_revert_colsample
- hypothesis: Ablate a2: revert colsample_bytree to default 0.8 (keep max_depth=2). Test whether colsample=1.0 was load-bearing vs W'''.
- observation: pending: interpret fold/runtime signal before next action.
- comparison: pending: compare against previous, family best, and global best.
- significance: pending: apply pooled-std noise rule.
- attribution: one-knob work item; verify no bundled changes before promotion.
- next_hypothesis: pending: one-knob next action or gate decision.

## 20260507-214500-confirm-baseline_three_only

- stage: confirm
- feature_lane: baseline_three_only
- change_kind: diagnostic
- hypothesis_unit: seed_confirm
- feature_group: validation
- anchor_run_id: 20260507-213647-deepen-baseline_three_only
- status: confirm
- cv_mae: 62674.07920276711
- cv_mae_std: 4330.881818507029
- runtime_seconds: 26.216053999989526
- change_from_previous: confirm_seed2026
- hypothesis: Stage 4 confirm seed=2026 of W''' (deepen iter9 winner: max_depth=2 + colsample=1.0). Verify seed agreement before promotion.
- observation: pending: interpret fold/runtime signal before next action.
- comparison: pending: compare against previous, family best, and global best.
- significance: pending: apply pooled-std noise rule.
- attribution: one-knob work item; verify no bundled changes before promotion.
- next_hypothesis: pending: one-knob next action or gate decision.
