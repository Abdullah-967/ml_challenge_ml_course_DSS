# xgboost_v7 Iteration Log

Append-only. One block per canonical CV run. See the bundled `plugins/model-family-mae/references/reflection_protocol.md`.

Required metadata per entry: stage, change_kind, hypothesis_unit, feature_group, anchor_run_id, change_from_previous, hypothesis, observation, comparison, significance, attribution, next_hypothesis.

## 20260509-182620-smoke-v6_plus_top20_submodels

- stage: smoke
- feature_lane: v6_plus_top20_submodels
- change_kind: hyperparameter
- hypothesis_unit: n_a
- feature_group: n_a
- anchor_run_id: 20260509-173002-deepen-v4_anchor
- status: revert
- cv_mae: 47216.67523576734
- cv_mae_std: 5263.901532688135
- runtime_seconds: 1046.3768020000134
- change_from_previous: smoke_laneA_top20_submodels_min100
- hypothesis: Smoke Lane A: v6 promoted anchor + extend per-type sub-models from top15/min200 to top20/min100. Wide architecture coverage test: determine whether remaining mid-frequency property types add specialized signal before local tuning.
- observation: pending: interpret fold/runtime signal before next action.
- comparison: pending: compare against previous, family best, and global best.
- significance: pending: apply pooled-std noise rule.
- attribution: one-knob work item; verify no bundled changes before promotion.
- next_hypothesis: pending: one-knob next action or gate decision.

## 20260509-184448-smoke-v6_blend02

- stage: smoke
- feature_lane: v6_blend02
- change_kind: hyperparameter
- hypothesis_unit: n_a
- feature_group: n_a
- anchor_run_id: 20260509-173002-deepen-v4_anchor
- status: revert
- cv_mae: 46726.018134161466
- cv_mae_std: 5530.229087518746
- runtime_seconds: 1055.034175400011
- change_from_previous: smoke_laneB_blend02
- hypothesis: Smoke Lane B: v6 promoted anchor with submodel BLEND lowered from 0.3 to 0.2. Wide architecture-weight test: v6 gained from more type coverage, but less submodel weight may reduce variance while keeping type-specific signal.
- observation: pending: interpret fold/runtime signal before next action.
- comparison: pending: compare against previous, family best, and global best.
- significance: pending: apply pooled-std noise rule.
- attribution: one-knob work item; verify no bundled changes before promotion.
- next_hypothesis: pending: one-knob next action or gate decision.

## 20260509-190305-smoke-v6_nest7000

- stage: smoke
- feature_lane: v6_nest7000
- change_kind: capacity_pair
- hypothesis_unit: n_a
- feature_group: n_a
- anchor_run_id: 20260509-173002-deepen-v4_anchor
- status: keep
- cv_mae: 46498.55547269377
- cv_mae_std: 5582.213214663211
- runtime_seconds: 1395.0827468000061
- change_from_previous: smoke_laneC_nest7000
- hypothesis: Smoke Lane C: v6 promoted anchor with n_estimators increased from 6000 to 7000 in both global and sub-models. Wide capacity-axis test before any local deepen/tune loop.
- observation: pending: interpret fold/runtime signal before next action.
- comparison: pending: compare against previous, family best, and global best.
- significance: pending: apply pooled-std noise rule.
- attribution: one-knob work item; verify no bundled changes before promotion.
- next_hypothesis: pending: one-knob next action or gate decision.

## 20260509-192702-deepen-v6_capacity_path

- stage: deepen
- feature_lane: v6_capacity_path
- change_kind: capacity_pair
- hypothesis_unit: n_a
- feature_group: n_a
- anchor_run_id: 20260509-190305-smoke-v6_nest7000
- status: keep
- cv_mae: 46308.018576336806
- cv_mae_std: 5754.242728236756
- runtime_seconds: 1504.9191178000183
- change_from_previous: deepen_iter1_nest8000
- hypothesis: Deepen iter1: after wide smoke selected the capacity lane, increase n_estimators from 7000 to 8000 in both global and top15 sub-models. Tests whether the v6/v7 capacity curve still has headroom before confirmation.
- observation: pending: interpret fold/runtime signal before next action.
- comparison: pending: compare against previous, family best, and global best.
- significance: pending: apply pooled-std noise rule.
- attribution: one-knob work item; verify no bundled changes before promotion.
- next_hypothesis: pending: one-knob next action or gate decision.

## 20260509-195253-deepen-v6_capacity_path

- stage: deepen
- feature_lane: v6_capacity_path
- change_kind: diagnostic
- hypothesis_unit: n_a
- feature_group: n_a
- anchor_run_id: 20260509-192702-deepen-v6_capacity_path
- status: confirm
- cv_mae: 47233.08442877121
- cv_mae_std: 3051.7208944912677
- runtime_seconds: 1597.704832599993
- change_from_previous: confirm_iter1_seed2026
- hypothesis: Stage 4 confirm seed=2026 of v7 iter1 (top15 per-type sub-models + n_est=8000). Verify the new raw global best before promotion.
- observation: pending: interpret fold/runtime signal before next action.
- comparison: pending: compare against previous, family best, and global best.
- significance: pending: apply pooled-std noise rule.
- attribution: one-knob work item; verify no bundled changes before promotion.
- next_hypothesis: pending: one-knob next action or gate decision.

## 20260509-212520-deepen-v6_capacity_path

- stage: deepen
- feature_lane: v6_capacity_path
- change_kind: capacity_pair
- hypothesis_unit: tree_capacity_with_internal_early_stopping
- feature_group: model_capacity
- anchor_run_id: 20260509-192702-deepen-v6_capacity_path
- status: keep
- cv_mae: 48273.93593932717
- cv_mae_std: 5075.167590456663
- runtime_seconds: 299.4286166999955
- change_from_previous: deepen_iter2_internal_early_stopping
- hypothesis: Deepen iter2: on top of promoted v7 top15 plus n_est=8000, replace fixed 8000 trees with n_estimators=12000 and fold-internal early_stopping_rounds=200. The internal eval split is drawn only from each outer training split; the outer validation fold remains untouched.
- observation: pending: interpret fold/runtime signal before next action.
- comparison: pending: compare against previous, family best, and global best.
- significance: pending: apply pooled-std noise rule.
- attribution: one-knob work item; verify no bundled changes before promotion.
- next_hypothesis: pending: one-knob next action or gate decision.
