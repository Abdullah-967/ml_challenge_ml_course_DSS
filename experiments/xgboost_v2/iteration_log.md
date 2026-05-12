# xgboost_v2 Iteration Log

Append-only. One block per reflected canonical CV run.

Required fields per entry: stage, change_kind, hypothesis_unit, feature_group, anchor_run_id, change_from_previous, hypothesis, observation, comparison, significance, attribution, next_hypothesis.

## 20260507-200237-smoke-tier1_strong_solo

- stage: smoke
- feature_lane: tier1_strong_solo
- change_kind: feature
- hypothesis_unit: tier1_strong_solo: built_area + property_type + house_area + area_house_5plus_rooms
- feature_group: raw
- anchor_run_id: n/a
- status: keep
- cv_mae: 58757.97524797342
- cv_mae_std: 4788.771720636094
- runtime_seconds: 28.41705330001423
- change_from_previous: single_knob=tier1_strong_solo
- hypothesis: Stage 1 smoke iter1: 4 cols with strongest solo signal (single-col CV MAE improvement >3500 vs median baseline 92674)
- observation: TODO: interpret fold/runtime signal before next action.
- comparison: TODO: compare against previous, family best, and global best.
- significance: TODO: apply pooled-std noise rule.
- attribution: one-knob work item; verify no bundled changes before promotion.
- next_hypothesis: TODO: one-knob next action or gate decision.

## 20260507-200404-smoke-tier2_mid_solo

- stage: smoke
- feature_lane: tier2_mid_solo
- change_kind: feature
- hypothesis_unit: tier2_mid_solo: num_houses + apartment_area + num_house_5plus_rooms + num_premises
- feature_group: raw
- anchor_run_id: n/a
- status: keep
- cv_mae: 70155.7805882796
- cv_mae_std: 5476.890916661445
- runtime_seconds: 38.77326170000015
- change_from_previous: single_knob=tier2_mid_solo
- hypothesis: Stage 1 smoke iter2: 4 cols with mid-tier solo signal (single-col CV MAE improvement 0-1400 vs median baseline 92674). Disjoint from tier1.
- observation: TODO: interpret fold/runtime signal before next action.
- comparison: TODO: compare against previous, family best, and global best.
- significance: TODO: apply pooled-std noise rule.
- attribution: one-knob work item; verify no bundled changes before promotion.
- next_hypothesis: TODO: one-knob next action or gate decision.

## 20260507-200607-smoke-tier3_weak_solo

- stage: smoke
- feature_lane: tier3_weak_solo
- change_kind: feature
- hypothesis_unit: tier3_weak_solo: 29 numeric (room layout, num_*, areas, year/month, future_sale, num_sections, num_communes, land_area, num_commercial, num_parcels) + 3 cats (transaction_type, commune_first, cadastral_first)
- feature_group: raw
- anchor_run_id: n/a
- status: keep
- cv_mae: 64405.68985444998
- cv_mae_std: 4931.599639601946
- runtime_seconds: 41.33530169998994
- change_from_previous: single_knob=tier3_weak_solo
- hypothesis: Stage 1 smoke iter3: long-tail of weak/negative solo cols; tests compositional signal. Excludes constants and transaction_date.
- observation: TODO: interpret fold/runtime signal before next action.
- comparison: TODO: compare against previous, family best, and global best.
- significance: TODO: apply pooled-std noise rule.
- attribution: one-knob work item; verify no bundled changes before promotion.
- next_hypothesis: TODO: one-knob next action or gate decision.

## 20260507-200956-deepen-tier1_strong_solo

- stage: deepen
- feature_lane: tier1_strong_solo
- change_kind: feature
- hypothesis_unit: add commune_first native cat
- feature_group: geo
- anchor_run_id: 20260507-200237-smoke-tier1_strong_solo
- status: keep
- cv_mae: 55576.54062682891
- cv_mae_std: 4420.4591032547405
- runtime_seconds: 37.38934910000535
- change_from_previous: single_knob=add_commune_first
- hypothesis: Deepen iter1: + commune_first (first token of commune_codes) as native xgboost categorical
- observation: TODO: interpret fold/runtime signal before next action.
- comparison: TODO: compare against previous, family best, and global best.
- significance: TODO: apply pooled-std noise rule.
- attribution: one-knob work item; verify no bundled changes before promotion.
- next_hypothesis: TODO: one-knob next action or gate decision.

## 20260507-201108-deepen-tier1_strong_solo

- stage: deepen
- feature_lane: tier1_strong_solo
- change_kind: feature
- hypothesis_unit: add cadastral_first native cat
- feature_group: geo
- anchor_run_id: 20260507-200956-deepen-tier1_strong_solo
- status: keep
- cv_mae: 53274.56745163216
- cv_mae_std: 4604.199759907861
- runtime_seconds: 42.14200720001827
- change_from_previous: single_knob=add_cadastral_first
- hypothesis: Deepen iter2: + cadastral_first (first token) as native cat. Carry: commune_first.
- observation: pending: interpret fold/runtime signal before next action.
- comparison: pending: compare against previous, family best, and global best.
- significance: pending: apply pooled-std noise rule.
- attribution: one-knob work item; verify no bundled changes before promotion.
- next_hypothesis: pending: one-knob next action or gate decision.

## 20260507-201223-deepen-tier1_strong_solo

- stage: deepen
- feature_lane: tier1_strong_solo
- change_kind: feature
- hypothesis_unit: add transaction_type native cat
- feature_group: cat
- anchor_run_id: 20260507-201108-deepen-tier1_strong_solo
- status: keep
- cv_mae: 52889.468612364704
- cv_mae_std: 4455.238757212996
- runtime_seconds: 89.02382709999802
- change_from_previous: single_knob=add_transaction_type
- hypothesis: Deepen iter3: + transaction_type as native cat. Carry: commune_first, cadastral_first.
- observation: pending: interpret fold/runtime signal before next action.
- comparison: pending: compare against previous, family best, and global best.
- significance: pending: apply pooled-std noise rule.
- attribution: one-knob work item; verify no bundled changes before promotion.
- next_hypothesis: pending: one-knob next action or gate decision.

## 20260507-201439-deepen-tier1_strong_solo

- stage: deepen
- feature_lane: tier1_strong_solo
- change_kind: feature
- hypothesis_unit: add land_area+num_lots+num_premises
- feature_group: raw_numeric
- anchor_run_id: 20260507-201223-deepen-tier1_strong_solo
- status: keep
- cv_mae: 50676.45151250586
- cv_mae_std: 4339.200657755464
- runtime_seconds: 70.66938370000571
- change_from_previous: single_knob=add_land_lots_premises
- hypothesis: Deepen iter4: + land_area, num_lots, num_premises. Carry: tier1 + commune_first + cadastral_first + transaction_type.
- observation: pending: interpret fold/runtime signal before next action.
- comparison: pending: compare against previous, family best, and global best.
- significance: pending: apply pooled-std noise rule.
- attribution: one-knob work item; verify no bundled changes before promotion.
- next_hypothesis: pending: one-knob next action or gate decision.

## 20260507-201632-deepen-tier1_strong_solo

- stage: deepen
- feature_lane: tier1_strong_solo
- change_kind: feature
- hypothesis_unit: add num_houses+num_apartments+num_commercial
- feature_group: raw_numeric
- anchor_run_id: 20260507-201439-deepen-tier1_strong_solo
- status: keep
- cv_mae: 50478.41374983259
- cv_mae_std: 4444.5127541466945
- runtime_seconds: 46.92175870001665
- change_from_previous: single_knob=add_entity_counts
- hypothesis: Deepen iter5: + entity counts (num_houses, num_apartments, num_commercial).
- observation: pending: interpret fold/runtime signal before next action.
- comparison: pending: compare against previous, family best, and global best.
- significance: pending: apply pooled-std noise rule.
- attribution: one-knob work item; verify no bundled changes before promotion.
- next_hypothesis: pending: one-knob next action or gate decision.

## 20260507-201801-deepen-tier1_strong_solo

- stage: deepen
- feature_lane: tier1_strong_solo
- change_kind: feature
- hypothesis_unit: add room layout cluster (apartment_area + 18 room layout numerics + num_house_5plus_rooms)
- feature_group: raw_numeric
- anchor_run_id: 20260507-201632-deepen-tier1_strong_solo
- status: keep
- cv_mae: 50441.16063344024
- cv_mae_std: 4529.044437594926
- runtime_seconds: 54.95469449998927
- change_from_previous: single_knob=add_room_layout_cluster
- hypothesis: Deepen iter6: + room layout cluster as one knob (all area_house_*, num_house_*, area_apt_*, num_apt_*, plus apartment_area, num_house_5plus_rooms).
- observation: pending: interpret fold/runtime signal before next action.
- comparison: pending: compare against previous, family best, and global best.
- significance: pending: apply pooled-std noise rule.
- attribution: one-knob work item; verify no bundled changes before promotion.
- next_hypothesis: pending: one-knob next action or gate decision.

## 20260507-201943-deepen-tier1_strong_solo

- stage: deepen
- feature_lane: tier1_strong_solo
- change_kind: feature
- hypothesis_unit: add date_ordinal (transaction_date days since 2014-01-01, first token)
- feature_group: derived
- anchor_run_id: 20260507-201801-deepen-tier1_strong_solo
- status: keep
- cv_mae: 49715.844108136225
- cv_mae_std: 4667.8172959717185
- runtime_seconds: 54.2465737000166
- change_from_previous: single_knob=add_date_ordinal
- hypothesis: Deepen iter7: + date_ordinal.
- observation: pending: interpret fold/runtime signal before next action.
- comparison: pending: compare against previous, family best, and global best.
- significance: pending: apply pooled-std noise rule.
- attribution: one-knob work item; verify no bundled changes before promotion.
- next_hypothesis: pending: one-knob next action or gate decision.

## 20260507-202118-deepen-tier1_strong_solo

- stage: deepen
- feature_lane: tier1_strong_solo
- change_kind: target
- hypothesis_unit: log1p target with expm1 inverse
- feature_group: target
- anchor_run_id: 20260507-201943-deepen-tier1_strong_solo
- status: keep
- cv_mae: 49393.96131931456
- cv_mae_std: 4753.166419807848
- runtime_seconds: 56.40937040001154
- change_from_previous: single_knob=log1p_target
- hypothesis: Deepen iter8: log1p target wrap; predict in log space, inverse with expm1.
- observation: pending: interpret fold/runtime signal before next action.
- comparison: pending: compare against previous, family best, and global best.
- significance: pending: apply pooled-std noise rule.
- attribution: one-knob work item; verify no bundled changes before promotion.
- next_hypothesis: pending: one-knob next action or gate decision.

## 20260507-202310-deepen-tier1_strong_solo

- stage: deepen
- feature_lane: tier1_strong_solo
- change_kind: feature
- hypothesis_unit: add 5 derived ratios
- feature_group: derived
- anchor_run_id: 20260507-202118-deepen-tier1_strong_solo
- status: keep
- cv_mae: 49264.603537382834
- cv_mae_std: 4944.637882311921
- runtime_seconds: 73.3609830000205
- change_from_previous: single_knob=add_ratios
- hypothesis: Deepen iter9: + built_per_premise, land_per_lot, commercial_share, apt_share, houses_per_premise.
- observation: pending: interpret fold/runtime signal before next action.
- comparison: pending: compare against previous, family best, and global best.
- significance: pending: apply pooled-std noise rule.
- attribution: one-knob work item; verify no bundled changes before promotion.
- next_hypothesis: pending: one-knob next action or gate decision.

## 20260507-202514-deepen-tier1_strong_solo

- stage: deepen
- feature_lane: tier1_strong_solo
- change_kind: preprocessing
- hypothesis_unit: add commune_first smoothed target encoding (smooth=20)
- feature_group: encoded
- anchor_run_id: 20260507-202310-deepen-tier1_strong_solo
- status: revert
- cv_mae: 49424.33894356108
- cv_mae_std: 4721.35709050553
- runtime_seconds: 70.26929830000154
- change_from_previous: single_knob=add_commune_te20
- hypothesis: Deepen iter10: + commune_first_target_enc (smoothed mean, smooth=20). Encoder fit on train fold; applied to val. commune_first kept as native cat too.
- observation: pending: interpret fold/runtime signal before next action.
- comparison: pending: compare against previous, family best, and global best.
- significance: pending: apply pooled-std noise rule.
- attribution: one-knob work item; verify no bundled changes before promotion.
- next_hypothesis: pending: one-knob next action or gate decision.

## 20260507-202806-deepen-tier1_strong_solo

- stage: deepen
- feature_lane: tier1_strong_solo
- change_kind: hyperparameter
- hypothesis_unit: max_depth 6 -> 8
- feature_group: hyperparam
- anchor_run_id: 20260507-202310-deepen-tier1_strong_solo
- status: revert
- cv_mae: 49392.6041991083
- cv_mae_std: 4927.593822032411
- runtime_seconds: 85.62158020000788
- change_from_previous: single_knob=max_depth_8
- hypothesis: Stage 3 tune iter1: max_depth=8 (was 6); deeper trees on top of W (deepen iter9).
- observation: pending: interpret fold/runtime signal before next action.
- comparison: pending: compare against previous, family best, and global best.
- significance: pending: apply pooled-std noise rule.
- attribution: one-knob work item; verify no bundled changes before promotion.
- next_hypothesis: pending: one-knob next action or gate decision.

## 20260507-203005-deepen-tier1_strong_solo

- stage: deepen
- feature_lane: tier1_strong_solo
- change_kind: hyperparameter
- hypothesis_unit: max_depth 6 -> 4
- feature_group: hyperparam
- anchor_run_id: 20260507-202310-deepen-tier1_strong_solo
- status: revert
- cv_mae: 50487.64493370066
- cv_mae_std: 4904.279071133174
- runtime_seconds: 49.69205479999073
- change_from_previous: single_knob=max_depth_4
- hypothesis: Stage 3 tune iter2: max_depth=4 (was 6); shallower.
- observation: pending: interpret fold/runtime signal before next action.
- comparison: pending: compare against previous, family best, and global best.
- significance: pending: apply pooled-std noise rule.
- attribution: one-knob work item; verify no bundled changes before promotion.
- next_hypothesis: pending: one-knob next action or gate decision.

## 20260507-203130-deepen-tier1_strong_solo

- stage: deepen
- feature_lane: tier1_strong_solo
- change_kind: hyperparameter
- hypothesis_unit: lr 0.05 -> 0.03 with n_est 500 -> 1000
- feature_group: hyperparam
- anchor_run_id: 20260507-202310-deepen-tier1_strong_solo
- status: revert
- cv_mae: 49176.770675614
- cv_mae_std: 5039.636467464841
- runtime_seconds: 123.21681379998336
- change_from_previous: single_knob=lr03_nest1000
- hypothesis: Stage 3 tune iter3: lr=0.03 + n_est=1000 (capacity_pair: paired tweak; effective compute similar).
- observation: pending: interpret fold/runtime signal before next action.
- comparison: pending: compare against previous, family best, and global best.
- significance: pending: apply pooled-std noise rule.
- attribution: one-knob work item; verify no bundled changes before promotion.
- next_hypothesis: pending: one-knob next action or gate decision.

## 20260507-203406-deepen-tier1_strong_solo

- stage: deepen
- feature_lane: tier1_strong_solo
- change_kind: hyperparameter
- hypothesis_unit: min_child_weight 5 -> 2
- feature_group: hyperparam
- anchor_run_id: 20260507-202310-deepen-tier1_strong_solo
- status: revert
- cv_mae: 49660.529693770695
- cv_mae_std: 5204.301892320668
- runtime_seconds: 74.57844800001476
- change_from_previous: single_knob=mcw2
- hypothesis: Stage 3 tune iter4: min_child_weight=2 (was 5); less leaf regularization.
- observation: pending: interpret fold/runtime signal before next action.
- comparison: pending: compare against previous, family best, and global best.
- significance: pending: apply pooled-std noise rule.
- attribution: one-knob work item; verify no bundled changes before promotion.
- next_hypothesis: pending: one-knob next action or gate decision.

## 20260507-203601-deepen-tier1_strong_solo

- stage: deepen
- feature_lane: tier1_strong_solo
- change_kind: hyperparameter
- hypothesis_unit: mcw 5 -> 10
- feature_group: hyperparam
- anchor_run_id: 20260507-202310-deepen-tier1_strong_solo
- status: revert
- cv_mae: 49369.59341894639
- cv_mae_std: 4965.807291991755
- runtime_seconds: 68.74530820001382
- change_from_previous: single_knob=mcw10
- hypothesis: Stage 3 tune iter5: min_child_weight=10.
- observation: pending: interpret fold/runtime signal before next action.
- comparison: pending: compare against previous, family best, and global best.
- significance: pending: apply pooled-std noise rule.
- attribution: one-knob work item; verify no bundled changes before promotion.
- next_hypothesis: pending: one-knob next action or gate decision.

## 20260507-203740-deepen-tier1_strong_solo

- stage: deepen
- feature_lane: tier1_strong_solo
- change_kind: hyperparameter
- hypothesis_unit: subsample 0.8 -> 0.6
- feature_group: hyperparam
- anchor_run_id: 20260507-202310-deepen-tier1_strong_solo
- status: revert
- cv_mae: 49694.021847973665
- cv_mae_std: 5012.8956603399665
- runtime_seconds: 63.94058169997879
- change_from_previous: single_knob=subsample06
- hypothesis: Stage 3 tune iter6: subsample=0.6.
- observation: pending: interpret fold/runtime signal before next action.
- comparison: pending: compare against previous, family best, and global best.
- significance: pending: apply pooled-std noise rule.
- attribution: one-knob work item; verify no bundled changes before promotion.
- next_hypothesis: pending: one-knob next action or gate decision.

## 20260507-203913-deepen-tier1_strong_solo

- stage: deepen
- feature_lane: tier1_strong_solo
- change_kind: hyperparameter
- hypothesis_unit: colsample_bytree 0.8 -> 0.6
- feature_group: hyperparam
- anchor_run_id: 20260507-202310-deepen-tier1_strong_solo
- status: keep
- cv_mae: 49154.00649740048
- cv_mae_std: 4961.937820802317
- runtime_seconds: 61.79384620001656
- change_from_previous: single_knob=colsample06
- hypothesis: Stage 3 tune iter7: colsample_bytree=0.6.
- observation: pending: interpret fold/runtime signal before next action.
- comparison: pending: compare against previous, family best, and global best.
- significance: pending: apply pooled-std noise rule.
- attribution: one-knob work item; verify no bundled changes before promotion.
- next_hypothesis: pending: one-knob next action or gate decision.

## 20260507-204049-deepen-tier1_strong_solo

- stage: deepen
- feature_lane: tier1_strong_solo
- change_kind: hyperparameter
- hypothesis_unit: colsample_bytree 0.6 -> 1.0
- feature_group: hyperparam
- anchor_run_id: 20260507-203913-deepen-tier1_strong_solo
- status: revert
- cv_mae: 49707.90986689601
- cv_mae_std: 4926.934498321577
- runtime_seconds: 67.36494849997689
- change_from_previous: single_knob=colsample10
- hypothesis: Stage 3 tune iter8: colsample_bytree=1.0; test other direction.
- observation: pending: interpret fold/runtime signal before next action.
- comparison: pending: compare against previous, family best, and global best.
- significance: pending: apply pooled-std noise rule.
- attribution: one-knob work item; verify no bundled changes before promotion.
- next_hypothesis: pending: one-knob next action or gate decision.

## 20260507-204228-deepen-tier1_strong_solo

- stage: deepen
- feature_lane: tier1_strong_solo
- change_kind: hyperparameter
- hypothesis_unit: reg_lambda 1.0 -> 5.0
- feature_group: hyperparam
- anchor_run_id: 20260507-203913-deepen-tier1_strong_solo
- status: revert
- cv_mae: 49308.86793757279
- cv_mae_std: 5002.648635111459
- runtime_seconds: 53.819106000009924
- change_from_previous: single_knob=lambda5
- hypothesis: Stage 3 tune iter9: reg_lambda=5.0; more L2 reg.
- observation: pending: interpret fold/runtime signal before next action.
- comparison: pending: compare against previous, family best, and global best.
- significance: pending: apply pooled-std noise rule.
- attribution: one-knob work item; verify no bundled changes before promotion.
- next_hypothesis: pending: one-knob next action or gate decision.

## 20260507-204354-deepen-tier1_strong_solo

- stage: deepen
- feature_lane: tier1_strong_solo
- change_kind: hyperparameter
- hypothesis_unit: reg_alpha 0 -> 1.0
- feature_group: hyperparam
- anchor_run_id: 20260507-203913-deepen-tier1_strong_solo
- status: revert
- cv_mae: 49390.14426588221
- cv_mae_std: 4911.644713365753
- runtime_seconds: 49.936615499987965
- change_from_previous: single_knob=alpha1
- hypothesis: Stage 3 tune iter10: reg_alpha=1.0; add L1 reg.
- observation: pending: interpret fold/runtime signal before next action.
- comparison: pending: compare against previous, family best, and global best.
- significance: pending: apply pooled-std noise rule.
- attribution: one-knob work item; verify no bundled changes before promotion.
- next_hypothesis: pending: one-knob next action or gate decision.

## 20260507-204541-deepen-tier1_strong_solo

- stage: deepen
- feature_lane: tier1_strong_solo
- change_kind: feature
- hypothesis_unit: ablate: drop commune_first cat
- feature_group: ablate
- anchor_run_id: 20260507-203913-deepen-tier1_strong_solo
- status: ablate
- cv_mae: 51038.3327079749
- cv_mae_std: 4928.899342185866
- runtime_seconds: 49.236804900021525
- change_from_previous: ablate_a1=drop_commune_first
- hypothesis: Ablate a1: LOO remove commune_first from cats; test if it is load-bearing.
- observation: pending: interpret fold/runtime signal before next action.
- comparison: pending: compare against previous, family best, and global best.
- significance: pending: apply pooled-std noise rule.
- attribution: one-knob work item; verify no bundled changes before promotion.
- next_hypothesis: pending: one-knob next action or gate decision.

## 20260507-204702-deepen-tier1_strong_solo

- stage: deepen
- feature_lane: tier1_strong_solo
- change_kind: feature
- hypothesis_unit: ablate: drop cadastral_first cat
- feature_group: ablate
- anchor_run_id: 20260507-203913-deepen-tier1_strong_solo
- status: ablate
- cv_mae: 50523.148703272556
- cv_mae_std: 4729.4113882103375
- runtime_seconds: 46.26349510002183
- change_from_previous: ablate_a2=drop_cadastral_first
- hypothesis: Ablate a2: LOO remove cadastral_first.
- observation: pending: interpret fold/runtime signal before next action.
- comparison: pending: compare against previous, family best, and global best.
- significance: pending: apply pooled-std noise rule.
- attribution: one-knob work item; verify no bundled changes before promotion.
- next_hypothesis: pending: one-knob next action or gate decision.

## 20260507-204822-deepen-tier1_strong_solo

- stage: deepen
- feature_lane: tier1_strong_solo
- change_kind: feature
- hypothesis_unit: ablate: drop land_area+num_lots+num_premises
- feature_group: ablate
- anchor_run_id: 20260507-203913-deepen-tier1_strong_solo
- status: ablate
- cv_mae: 50780.583047824715
- cv_mae_std: 5035.565692916642
- runtime_seconds: 46.261220399988815
- change_from_previous: ablate_a3=drop_land_lots_premises
- hypothesis: Ablate a3: LOO drop the 3 raw count/area cols added in deepen iter4.
- observation: pending: interpret fold/runtime signal before next action.
- comparison: pending: compare against previous, family best, and global best.
- significance: pending: apply pooled-std noise rule.
- attribution: one-knob work item; verify no bundled changes before promotion.
- next_hypothesis: pending: one-knob next action or gate decision.

## 20260507-204944-deepen-tier1_strong_solo

- stage: deepen
- feature_lane: tier1_strong_solo
- change_kind: target
- hypothesis_unit: ablate: revert log1p target
- feature_group: ablate
- anchor_run_id: 20260507-203913-deepen-tier1_strong_solo
- status: ablate
- cv_mae: 49324.444765621534
- cv_mae_std: 4667.493783894466
- runtime_seconds: 48.49904769999557
- change_from_previous: ablate_a4=revert_log1p
- hypothesis: Ablate a4: LOO disable log1p target wrap.
- observation: pending: interpret fold/runtime signal before next action.
- comparison: pending: compare against previous, family best, and global best.
- significance: pending: apply pooled-std noise rule.
- attribution: one-knob work item; verify no bundled changes before promotion.
- next_hypothesis: pending: one-knob next action or gate decision.

## 20260507-205107-deepen-tier1_strong_solo

- stage: deepen
- feature_lane: tier1_strong_solo
- change_kind: feature
- hypothesis_unit: ablate: drop date_ordinal
- feature_group: ablate
- anchor_run_id: 20260507-203913-deepen-tier1_strong_solo
- status: ablate
- cv_mae: 49399.6337505282
- cv_mae_std: 4613.646202421698
- runtime_seconds: 47.93277179999859
- change_from_previous: ablate_a5=drop_date_ordinal
- hypothesis: Ablate a5: LOO drop date_ordinal.
- observation: pending: interpret fold/runtime signal before next action.
- comparison: pending: compare against previous, family best, and global best.
- significance: pending: apply pooled-std noise rule.
- attribution: one-knob work item; verify no bundled changes before promotion.
- next_hypothesis: pending: one-knob next action or gate decision.

## 20260507-205244-deepen-tier1_strong_solo

- stage: deepen
- feature_lane: tier1_strong_solo
- change_kind: feature
- hypothesis_unit: ablate combined: drop log1p + drop date_ordinal
- feature_group: ablate
- anchor_run_id: 20260507-203913-deepen-tier1_strong_solo
- status: ablate
- cv_mae: 50298.59637042021
- cv_mae_std: 4492.976338180789
- runtime_seconds: 49.32562400001916
- change_from_previous: ablate_a6=drop_log1p_and_date
- hypothesis: Ablate a6: combined removal of log1p target wrap AND date_ordinal feature; verify simplified W''.
- observation: pending: interpret fold/runtime signal before next action.
- comparison: pending: compare against previous, family best, and global best.
- significance: pending: apply pooled-std noise rule.
- attribution: one-knob work item; verify no bundled changes before promotion.
- next_hypothesis: pending: one-knob next action or gate decision.

## 20260507-205423-deepen-tier1_strong_solo

- stage: deepen
- feature_lane: tier1_strong_solo
- change_kind: diagnostic
- hypothesis_unit: confirm seed=2026 of W' recipe
- feature_group: confirm
- anchor_run_id: 20260507-203913-deepen-tier1_strong_solo
- status: confirm
- cv_mae: 49247.42680048377
- cv_mae_std: 4450.305768964429
- runtime_seconds: 53.66278740001144
- change_from_previous: confirm_seed2026
- hypothesis: Stage 4 confirm seed=2026 of W' (tune_iter7 colsample=0.6 + all kept knobs).
- observation: pending: interpret fold/runtime signal before next action.
- comparison: pending: compare against previous, family best, and global best.
- significance: pending: apply pooled-std noise rule.
- attribution: one-knob work item; verify no bundled changes before promotion.
- next_hypothesis: pending: one-knob next action or gate decision.
