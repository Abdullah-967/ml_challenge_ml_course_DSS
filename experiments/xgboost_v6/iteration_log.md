# xgboost_v6 Iteration Log

Append-only. One block per canonical CV run. See the bundled `plugins/model-family-mae/references/reflection_protocol.md`.

Required metadata per entry: stage, change_kind, hypothesis_unit, feature_group, anchor_run_id, change_from_previous, hypothesis, observation, comparison, significance, attribution, next_hypothesis.

## 20260508-221818-smoke-v5_plus_parcel_numeric

- stage: smoke
- feature_lane: v5_plus_parcel_numeric
- change_kind: feature
- hypothesis_unit: parcel_numeric_components
- feature_group: id_derived
- anchor_run_id: 20260508-160016-deepen-v4_anchor
- status: timeout
- cv_mae: None
- cv_mae_std: None
- runtime_seconds: 3600.0924554999947
- change_from_previous: smoke_laneA_parcel_numeric_components
- hypothesis: Smoke Lane A: v5 iter10 anchor + bounded numeric components parsed from first parcel_id (prefix code and parcel number). Train-only inspection found structured cadastral IDs; tests whether within-section parcel positioning carries signal beyond commune_first/cadastral_first cats without using raw high-cardinality IDs.
- observation: pending: interpret fold/runtime signal before next action.
- comparison: pending: compare against previous, family best, and global best.
- significance: pending: apply pooled-std noise rule.
- attribution: one-knob work item; verify no bundled changes before promotion.
- next_hypothesis: pending: one-knob next action or gate decision.

## 20260508-232100-smoke-v4_plus_parcel_numeric

- stage: smoke
- feature_lane: v4_plus_parcel_numeric
- change_kind: feature
- hypothesis_unit: parcel_numeric_components
- feature_group: id_derived
- anchor_run_id: 20260507-235645-deepen-v2_plus_geo_hierarchy
- status: revert
- cv_mae: 48219.94573006666
- cv_mae_std: 5176.027676682433
- runtime_seconds: 1554.5094884999999
- change_from_previous: smoke_laneB_v4_parcel_numeric_components
- hypothesis: Smoke Lane B: v4 W''''' anchor + bounded numeric components parsed from first parcel_id (prefix code and parcel number). Tests whether within-section parcel positioning adds signal to the promoted v4 recipe without using raw high-cardinality IDs.
- observation: pending: interpret fold/runtime signal before next action.
- comparison: pending: compare against previous, family best, and global best.
- significance: pending: apply pooled-std noise rule.
- attribution: one-knob work item; verify no bundled changes before promotion.
- next_hypothesis: pending: one-knob next action or gate decision.

## 20260508-234913-smoke-v4_plus_commune_section_cat

- stage: smoke
- feature_lane: v4_plus_commune_section_cat
- change_kind: feature
- hypothesis_unit: geo_granularity
- feature_group: geography
- anchor_run_id: 20260507-235645-deepen-v2_plus_geo_hierarchy
- status: keep
- cv_mae: 48512.35639364937
- cv_mae_std: 5012.684910929423
- runtime_seconds: 1476.2219324000034
- change_from_previous: smoke_laneC_commune_section_cat
- hypothesis: Smoke Lane C: v4 W''''' anchor + combined commune_section categorical (commune_first + cadastral_first). Tests geo_granularity: section codes repeat across communes, so a nested combined category may preserve cadastral geography that separate native cats only approximate.
- observation: pending: interpret fold/runtime signal before next action.
- comparison: pending: compare against previous, family best, and global best.
- significance: pending: apply pooled-std noise rule.
- attribution: one-knob work item; verify no bundled changes before promotion.
- next_hypothesis: pending: one-knob next action or gate decision.

## 20260509-161727-deepen-v4_anchor

- stage: deepen
- feature_lane: v4_anchor
- change_kind: hyperparameter
- hypothesis_unit: n_a
- feature_group: n_a
- anchor_run_id: 20260507-235645-deepen-v2_plus_geo_hierarchy
- status: keep
- cv_mae: 46946.756808930135
- cv_mae_std: 5238.026247768363
- runtime_seconds: 906.6694830000051
- change_from_previous: deepen_iter1_top15_submodels
- hypothesis: Deepen iter1: extend per-type sub-models from promoted v4 top 5 types to top 15 types, keeping n_estimators=4000 and blend=0.3. v5 top10 gave a small lift; this tests whether additional type coverage continues that direction as one architecture knob.
- observation: pending: interpret fold/runtime signal before next action.
- comparison: pending: compare against previous, family best, and global best.
- significance: pending: apply pooled-std noise rule.
- attribution: one-knob work item; verify no bundled changes before promotion.
- next_hypothesis: pending: one-knob next action or gate decision.

## 20260509-165753-deepen-v4_anchor

- stage: deepen
- feature_lane: v4_anchor
- change_kind: capacity_pair
- hypothesis_unit: n_a
- feature_group: n_a
- anchor_run_id: 20260509-161727-deepen-v4_anchor
- status: keep
- cv_mae: 46879.26415887138
- cv_mae_std: 5285.137442979943
- runtime_seconds: 891.4722509999992
- change_from_previous: deepen_iter2_top15_nest5000
- hypothesis: Deepen iter2: on top of iter1 (top15 per-type sub-models kept), increase n_estimators from 4000 to 5000 in both global and sub-models. v5's top10+n_est5000 step improved by ~69 MAE; repeating it on top15 may beat the raw global best.
- observation: pending: interpret fold/runtime signal before next action.
- comparison: pending: compare against previous, family best, and global best.
- significance: pending: apply pooled-std noise rule.
- attribution: one-knob work item; verify no bundled changes before promotion.
- next_hypothesis: pending: one-knob next action or gate decision.

## 20260509-171357-deepen-v4_anchor

- stage: deepen
- feature_lane: v4_anchor
- change_kind: diagnostic
- hypothesis_unit: n_a
- feature_group: n_a
- anchor_run_id: 20260509-165753-deepen-v4_anchor
- status: confirm
- cv_mae: 47252.54237930879
- cv_mae_std: 3268.1595409099023
- runtime_seconds: 902.1386987000005
- change_from_previous: confirm_iter2_seed2026
- hypothesis: Stage 4 confirm seed=2026 of iter2 (top15 per-type sub-models + n_est=5000). Verify the new raw-best recipe against the prior v4/v5 confirmation baselines before promotion.
- observation: pending: interpret fold/runtime signal before next action.
- comparison: pending: compare against previous, family best, and global best.
- significance: pending: apply pooled-std noise rule.
- attribution: one-knob work item; verify no bundled changes before promotion.
- next_hypothesis: pending: one-knob next action or gate decision.

## 20260509-173002-deepen-v4_anchor

- stage: deepen
- feature_lane: v4_anchor
- change_kind: capacity_pair
- hypothesis_unit: n_a
- feature_group: n_a
- anchor_run_id: 20260509-165753-deepen-v4_anchor
- status: keep
- cv_mae: 46653.36317433125
- cv_mae_std: 5466.566178417204
- runtime_seconds: 1080.1104520999943
- change_from_previous: deepen_iter3_top15_nest6000
- hypothesis: Deepen iter3: on top of iter2 (top15+n_est5000), increase n_estimators from 5000 to 6000 in both global and sub-models. Tests whether the capacity ramp still has headroom after the new raw-best iter2.
- observation: pending: interpret fold/runtime signal before next action.
- comparison: pending: compare against previous, family best, and global best.
- significance: pending: apply pooled-std noise rule.
- attribution: one-knob work item; verify no bundled changes before promotion.
- next_hypothesis: pending: one-knob next action or gate decision.

## 20260509-174840-deepen-v4_anchor

- stage: deepen
- feature_lane: v4_anchor
- change_kind: diagnostic
- hypothesis_unit: n_a
- feature_group: n_a
- anchor_run_id: 20260509-173002-deepen-v4_anchor
- status: confirm
- cv_mae: 47192.52924569419
- cv_mae_std: 3177.34283831878
- runtime_seconds: 1113.4423577999987
- change_from_previous: confirm_iter3_seed2026
- hypothesis: Stage 4 confirm seed=2026 of iter3 (top15 per-type sub-models + n_est=6000). Verify the new raw global best before promotion.
- observation: pending: interpret fold/runtime signal before next action.
- comparison: pending: compare against previous, family best, and global best.
- significance: pending: apply pooled-std noise rule.
- attribution: one-knob work item; verify no bundled changes before promotion.
- next_hypothesis: pending: one-knob next action or gate decision.
