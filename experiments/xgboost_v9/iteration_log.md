# xgboost_v9 Iteration Log

Append-only. One block per canonical CV run. See the bundled `plugins/model-family-mae/references/reflection_protocol.md`.

Required metadata per entry: stage, change_kind, hypothesis_unit, feature_group, anchor_run_id, change_from_previous, hypothesis, observation, comparison, significance, attribution, next_hypothesis.

## 20260510-111145-smoke-top_target_corr_3

- stage: smoke
- feature_lane: top_target_corr_3
- change_kind: feature
- hypothesis_unit: top_target_corr_triplet
- feature_group: structural_numeric
- anchor_run_id: n/a
- status: keep
- cv_mae: 62279.782098542106
- cv_mae_std: 4358.228277139309
- runtime_seconds: 20.991749500040896
- change_from_previous: smoke_iter1_top_target_corr_3
- hypothesis: Smoke iter1: XGBoost on top-3 target-correlated non-redundant features (built_area, num_lots, num_commercial) per mfm_cli analyze. First-principles 3-feature anchor analogous to baseline. Compare to xgboost_v3 baseline_three_only smoke (62674) and Ridge baseline.
- observation: pending: interpret fold/runtime signal before next action.
- comparison: pending: compare against previous, family best, and global best.
- significance: pending: apply pooled-std noise rule.
- attribution: one-knob work item; verify no bundled changes before promotion.
- next_hypothesis: pending: one-knob next action or gate decision.

## 20260510-111326-smoke-area_only_3

- stage: smoke
- feature_lane: area_only_3
- change_kind: feature
- hypothesis_unit: area_only_triplet
- feature_group: structural_numeric
- anchor_run_id: n/a
- status: keep
- cv_mae: 61254.41649508566
- cv_mae_std: 4639.942229404033
- runtime_seconds: 22.54091489990242
- change_from_previous: smoke_iter2_area_only_3
- hypothesis: Smoke iter2: XGBoost on pure-area triplet (built_area, land_area, house_area). Tests whether size dimensions alone carry signal vs Lane 1 (top-corr mixed counts+area).
- observation: pending: interpret fold/runtime signal before next action.
- comparison: pending: compare against previous, family best, and global best.
- significance: pending: apply pooled-std noise rule.
- attribution: one-knob work item; verify no bundled changes before promotion.
- next_hypothesis: pending: one-knob next action or gate decision.

## 20260510-111428-smoke-count_only_3

- stage: smoke
- feature_lane: count_only_3
- change_kind: feature
- hypothesis_unit: count_only_triplet
- feature_group: structural_numeric
- anchor_run_id: n/a
- status: keep
- cv_mae: 72560.97973430352
- cv_mae_std: 4784.348261271077
- runtime_seconds: 25.111969099962153
- change_from_previous: smoke_iter3_count_only_3
- hypothesis: Smoke iter3: XGBoost on pure-count triplet (num_lots, num_commercial, num_premises). Closes the first-principles smoke triad (mixed vs area-only vs count-only).
- observation: pending: interpret fold/runtime signal before next action.
- comparison: pending: compare against previous, family best, and global best.
- significance: pending: apply pooled-std noise rule.
- attribution: one-knob work item; verify no bundled changes before promotion.
- next_hypothesis: pending: one-knob next action or gate decision.

## 20260510-111630-deepen-backward_select_pool10

- stage: deepen
- feature_lane: backward_select_pool10
- change_kind: feature
- hypothesis_unit: backward_selection_pool10
- feature_group: structural_numeric
- anchor_run_id: 20260510-111326-smoke-area_only_3
- status: keep
- cv_mae: 58606.437389618266
- cv_mae_std: 4400.7033103746635
- runtime_seconds: 24.92731180007104
- change_from_previous: deepen_iter1_anchor_pool10
- hypothesis: Deepen iter1: anchor for backward selection. 10-feature pool selected via mfm analyze (top non-redundant target correlations + redundancy-group reps). Subsequent iters drop one feature each (one-knob).
- observation: pending: interpret fold/runtime signal before next action.
- comparison: pending: compare against previous, family best, and global best.
- significance: pending: apply pooled-std noise rule.
- attribution: one-knob work item; verify no bundled changes before promotion.
- next_hypothesis: pending: one-knob next action or gate decision.

## 20260510-111748-deepen-backward_select_drop_built_area

- stage: deepen
- feature_lane: backward_select_drop_built_area
- change_kind: feature
- hypothesis_unit: drop_built_area
- feature_group: structural_numeric
- anchor_run_id: 20260510-111630-deepen-backward_select_pool10
- status: keep
- cv_mae: 60525.94208083863
- cv_mae_std: 4698.611726073157
- runtime_seconds: 23.829465999966487
- change_from_previous: deepen_iter2_drop_built_area
- hypothesis: Deepen iter2: backward selection drop=built_area. Tests keystone hypothesis (smoke triad showed built_area dominant).
- observation: pending: interpret fold/runtime signal before next action.
- comparison: pending: compare against previous, family best, and global best.
- significance: pending: apply pooled-std noise rule.
- attribution: one-knob work item; verify no bundled changes before promotion.
- next_hypothesis: pending: one-knob next action or gate decision.

## 20260510-111842-deepen-backward_select_drop_land_area

- stage: deepen
- feature_lane: backward_select_drop_land_area
- change_kind: feature
- hypothesis_unit: drop_land_area
- feature_group: structural_numeric
- anchor_run_id: 20260510-111630-deepen-backward_select_pool10
- status: keep
- cv_mae: 60556.746833864236
- cv_mae_std: 4846.071198192248
- runtime_seconds: 25.477950599975884
- change_from_previous: deepen_iter3_drop_land_area
- hypothesis: Deepen iter3: backward selection drop=land_area.
- observation: pending: interpret fold/runtime signal before next action.
- comparison: pending: compare against previous, family best, and global best.
- significance: pending: apply pooled-std noise rule.
- attribution: one-knob work item; verify no bundled changes before promotion.
- next_hypothesis: pending: one-knob next action or gate decision.

## 20260510-111927-deepen-backward_select_drop_house_area

- stage: deepen
- feature_lane: backward_select_drop_house_area
- change_kind: feature
- hypothesis_unit: drop_house_area
- feature_group: structural_numeric
- anchor_run_id: 20260510-111630-deepen-backward_select_pool10
- status: keep
- cv_mae: 59021.5712117504
- cv_mae_std: 4296.612804239064
- runtime_seconds: 24.22816599998623
- change_from_previous: deepen_iter4_drop_house_area
- hypothesis: Deepen iter4: backward selection drop=house_area.
- observation: pending: interpret fold/runtime signal before next action.
- comparison: pending: compare against previous, family best, and global best.
- significance: pending: apply pooled-std noise rule.
- attribution: one-knob work item; verify no bundled changes before promotion.
- next_hypothesis: pending: one-knob next action or gate decision.

## 20260510-112013-deepen-backward_select_drop_apartment_area

- stage: deepen
- feature_lane: backward_select_drop_apartment_area
- change_kind: feature
- hypothesis_unit: drop_apartment_area
- feature_group: structural_numeric
- anchor_run_id: 20260510-111630-deepen-backward_select_pool10
- status: keep
- cv_mae: 58843.5686494626
- cv_mae_std: 4542.645310221029
- runtime_seconds: 23.316720300004818
- change_from_previous: deepen_iter5_drop_apartment_area
- hypothesis: Deepen iter5: backward selection drop=apartment_area.
- observation: pending: interpret fold/runtime signal before next action.
- comparison: pending: compare against previous, family best, and global best.
- significance: pending: apply pooled-std noise rule.
- attribution: one-knob work item; verify no bundled changes before promotion.
- next_hypothesis: pending: one-knob next action or gate decision.

## 20260510-112058-deepen-backward_select_drop_num_lots

- stage: deepen
- feature_lane: backward_select_drop_num_lots
- change_kind: feature
- hypothesis_unit: drop_num_lots
- feature_group: structural_numeric
- anchor_run_id: 20260510-111630-deepen-backward_select_pool10
- status: keep
- cv_mae: 59213.56637429617
- cv_mae_std: 4579.0220721811165
- runtime_seconds: 24.526002599974163
- change_from_previous: deepen_iter6_drop_num_lots
- hypothesis: Deepen iter6: backward selection drop=num_lots.
- observation: pending: interpret fold/runtime signal before next action.
- comparison: pending: compare against previous, family best, and global best.
- significance: pending: apply pooled-std noise rule.
- attribution: one-knob work item; verify no bundled changes before promotion.
- next_hypothesis: pending: one-knob next action or gate decision.

## 20260510-112144-deepen-backward_select_drop_num_commercial

- stage: deepen
- feature_lane: backward_select_drop_num_commercial
- change_kind: feature
- hypothesis_unit: drop_num_commercial
- feature_group: structural_numeric
- anchor_run_id: 20260510-111630-deepen-backward_select_pool10
- status: keep
- cv_mae: 58968.75675150424
- cv_mae_std: 4679.597725620433
- runtime_seconds: 25.303467899910174
- change_from_previous: deepen_iter7_drop_num_commercial
- hypothesis: Deepen iter7: backward selection drop=num_commercial.
- observation: pending: interpret fold/runtime signal before next action.
- comparison: pending: compare against previous, family best, and global best.
- significance: pending: apply pooled-std noise rule.
- attribution: one-knob work item; verify no bundled changes before promotion.
- next_hypothesis: pending: one-knob next action or gate decision.

## 20260510-112229-deepen-backward_select_drop_num_apt_2_rooms

- stage: deepen
- feature_lane: backward_select_drop_num_apt_2_rooms
- change_kind: feature
- hypothesis_unit: drop_num_apt_2_rooms
- feature_group: structural_numeric
- anchor_run_id: 20260510-111630-deepen-backward_select_pool10
- status: keep
- cv_mae: 58593.389696704515
- cv_mae_std: 4521.515025328495
- runtime_seconds: 23.84642410010565
- change_from_previous: deepen_iter8_drop_num_apt_2_rooms
- hypothesis: Deepen iter8: backward selection drop=num_apt_2_rooms.
- observation: pending: interpret fold/runtime signal before next action.
- comparison: pending: compare against previous, family best, and global best.
- significance: pending: apply pooled-std noise rule.
- attribution: one-knob work item; verify no bundled changes before promotion.
- next_hypothesis: pending: one-knob next action or gate decision.

## 20260510-112316-deepen-backward_select_drop_num_house_2_rooms

- stage: deepen
- feature_lane: backward_select_drop_num_house_2_rooms
- change_kind: feature
- hypothesis_unit: drop_num_house_2_rooms
- feature_group: structural_numeric
- anchor_run_id: 20260510-111630-deepen-backward_select_pool10
- status: keep
- cv_mae: 58868.00173755053
- cv_mae_std: 4727.940656307578
- runtime_seconds: 23.95592889992986
- change_from_previous: deepen_iter9_drop_num_house_2_rooms
- hypothesis: Deepen iter9: backward selection drop=num_house_2_rooms.
- observation: pending: interpret fold/runtime signal before next action.
- comparison: pending: compare against previous, family best, and global best.
- significance: pending: apply pooled-std noise rule.
- attribution: one-knob work item; verify no bundled changes before promotion.
- next_hypothesis: pending: one-knob next action or gate decision.

## 20260510-112409-deepen-backward_select_drop_year

- stage: deepen
- feature_lane: backward_select_drop_year
- change_kind: feature
- hypothesis_unit: drop_year
- feature_group: date_time
- anchor_run_id: 20260510-111630-deepen-backward_select_pool10
- status: keep
- cv_mae: 59369.263454479864
- cv_mae_std: 4478.0281173694175
- runtime_seconds: 24.3517113000853
- change_from_previous: deepen_iter10_drop_year
- hypothesis: Deepen iter10: backward selection drop=year.
- observation: pending: interpret fold/runtime signal before next action.
- comparison: pending: compare against previous, family best, and global best.
- significance: pending: apply pooled-std noise rule.
- attribution: one-knob work item; verify no bundled changes before promotion.
- next_hypothesis: pending: one-knob next action or gate decision.

## 20260510-112454-deepen-backward_select_drop_month

- stage: deepen
- feature_lane: backward_select_drop_month
- change_kind: feature
- hypothesis_unit: drop_month
- feature_group: date_time
- anchor_run_id: 20260510-111630-deepen-backward_select_pool10
- status: keep
- cv_mae: 58580.21417733059
- cv_mae_std: 4671.434279324438
- runtime_seconds: 25.52451239991933
- change_from_previous: deepen_iter11_drop_month
- hypothesis: Deepen iter11: backward selection drop=month.
- observation: pending: interpret fold/runtime signal before next action.
- comparison: pending: compare against previous, family best, and global best.
- significance: pending: apply pooled-std noise rule.
- attribution: one-knob work item; verify no bundled changes before promotion.
- next_hypothesis: pending: one-knob next action or gate decision.

## 20260510-112631-deepen-backward_select_drop_date_unit

- stage: deepen
- feature_lane: backward_select_drop_date_unit
- change_kind: feature
- hypothesis_unit: drop_date_time_unit
- feature_group: date_time
- anchor_run_id: 20260510-111630-deepen-backward_select_pool10
- status: keep
- cv_mae: 59558.055295181366
- cv_mae_std: 4353.86387895412
- runtime_seconds: 26.699074000003748
- change_from_previous: deepen_iter12_drop_date_unit
- hypothesis: Deepen iter12: drop date_time unit (year+month together as one semantic group). Year and month single-drops were both within noise; testing them as a coherent unit.
- observation: pending: interpret fold/runtime signal before next action.
- comparison: pending: compare against previous, family best, and global best.
- significance: pending: apply pooled-std noise rule.
- attribution: one-knob work item; verify no bundled changes before promotion.
- next_hypothesis: pending: one-knob next action or gate decision.

## 20260510-112736-deepen-keystone_pair_only

- stage: deepen
- feature_lane: keystone_pair_only
- change_kind: feature
- hypothesis_unit: keystone_pair_essentials
- feature_group: structural_numeric
- anchor_run_id: 20260510-111630-deepen-backward_select_pool10
- status: keep
- cv_mae: 63435.11176767679
- cv_mae_std: 4757.530277543061
- runtime_seconds: 21.780248099938035
- change_from_previous: deepen_iter13_keystone_pair_only_multi_change
- hypothesis: Deepen iter13 (multi_change): keystone_pair_only = built_area + land_area. Tests whether the two backward-selection-essential features alone hold up vs the 10-feature anchor. Cumulative drop of all 8 tie-droppable features as a single recipe-level decision.
- observation: pending: interpret fold/runtime signal before next action.
- comparison: pending: compare against previous, family best, and global best.
- significance: pending: apply pooled-std noise rule.
- attribution: one-knob work item; verify no bundled changes before promotion.
- next_hypothesis: pending: one-knob next action or gate decision.

## 20260510-112836-deepen-lean_7_drop_strongest_ties

- stage: deepen
- feature_lane: lean_7_drop_strongest_ties
- change_kind: feature
- hypothesis_unit: lean_7_subset
- feature_group: structural_numeric
- anchor_run_id: 20260510-111630-deepen-backward_select_pool10
- status: keep
- cv_mae: 58720.16083605758
- cv_mae_std: 4468.142833366632
- runtime_seconds: 24.629605200025253
- change_from_previous: deepen_iter14_lean_7_multi_change
- hypothesis: Deepen iter14 (multi_change): lean_7 = anchor minus the 3 strongest tie-droppers (month -26, num_apt_2_rooms -13, apartment_area +237). Tests cumulative drop of low-information features. After keystone_pair collapse (+4828) we know aggressive drops compound badly; this is the conservative middle ground.
- observation: pending: interpret fold/runtime signal before next action.
- comparison: pending: compare against previous, family best, and global best.
- significance: pending: apply pooled-std noise rule.
- attribution: one-knob work item; verify no bundled changes before promotion.
- next_hypothesis: pending: one-knob next action or gate decision.

## 20260510-112933-deepen-lean_5_top_signal

- stage: deepen
- feature_lane: lean_5_top_signal
- change_kind: feature
- hypothesis_unit: lean_5_subset
- feature_group: structural_numeric
- anchor_run_id: 20260510-111630-deepen-backward_select_pool10
- status: keep
- cv_mae: 59958.09787476794
- cv_mae_std: 4581.789846538174
- runtime_seconds: 25.096519400016405
- change_from_previous: deepen_iter15_lean_5_multi_change
- hypothesis: Deepen iter15 (multi_change): lean_5 = essentials + top signal (built_area, land_area, house_area, num_lots, num_commercial). After lean_7 ties anchor, push to find floor by dropping num_house_2_rooms + year on top of lean_7's drops. If lean_5 ties, the 5-feature minimal is the recipe to confirm.
- observation: pending: interpret fold/runtime signal before next action.
- comparison: pending: compare against previous, family best, and global best.
- significance: pending: apply pooled-std noise rule.
- attribution: one-knob work item; verify no bundled changes before promotion.
- next_hypothesis: pending: one-knob next action or gate decision.
