# xgboost_v11 Iteration Log

Append-only. One block per canonical CV run. See the bundled `plugins/model-family-mae/references/reflection_protocol.md`.

Required metadata per entry: stage, change_kind, hypothesis_unit, feature_group, anchor_run_id, change_from_previous, hypothesis, observation, comparison, significance, attribution, next_hypothesis.

## 20260510-134221-smoke-velocity_only_4

- stage: smoke
- feature_lane: velocity_only_4
- change_kind: feature
- hypothesis_unit: commune_time_velocity
- feature_group: date_time
- anchor_run_id: n/a
- status: keep
- cv_mae: 91748.76480381211
- cv_mae_std: 5632.440679647487
- runtime_seconds: 32.61316479998641
- change_from_previous: smoke_iter1_velocity_only_4
- hypothesis: Smoke iter1 (signal isolation): XGBoost on 4 fold-safe commune-time velocity features (n_txns_prev_60d/180d, avg_built_area_prev_60d, days_since_last_txn). Tests whether commune-time density predicts in isolation. History built from training fold only; lookup strictly less-than row's own date.
- observation: pending: interpret fold/runtime signal before next action.
- comparison: pending: compare against previous, family best, and global best.
- significance: pending: apply pooled-std noise rule.
- attribution: one-knob work item; verify no bundled changes before promotion.
- next_hypothesis: pending: one-knob next action or gate decision.

## 20260510-134430-smoke-shrunk_v6_anchor_n1000

- stage: smoke
- feature_lane: shrunk_v6_anchor_n1000
- change_kind: feature
- hypothesis_unit: anchor_no_velocity
- feature_group: structural_numeric
- anchor_run_id: n/a
- status: keep
- cv_mae: 48772.080477082185
- cv_mae_std: 4836.538701790976
- runtime_seconds: 150.90576420002617
- change_from_previous: smoke_iter2_shrunk_v6_anchor_n1000
- hypothesis: Smoke iter2: re-establish v6 anchor at n_est=1000 (no velocity features) as v11 family baseline. Lane 3 will add velocity for lift measurement.
- observation: pending: interpret fold/runtime signal before next action.
- comparison: pending: compare against previous, family best, and global best.
- significance: pending: apply pooled-std noise rule.
- attribution: one-knob work item; verify no bundled changes before promotion.
- next_hypothesis: pending: one-knob next action or gate decision.

## 20260510-134805-smoke-shrunk_v6_anchor_n1000_plus_velocity

- stage: smoke
- feature_lane: shrunk_v6_anchor_n1000_plus_velocity
- change_kind: feature
- hypothesis_unit: commune_time_velocity
- feature_group: date_time
- anchor_run_id: 20260510-134430-smoke-shrunk_v6_anchor_n1000
- status: keep
- cv_mae: 49013.46136523989
- cv_mae_std: 4862.856640407438
- runtime_seconds: 176.70384440000635
- change_from_previous: smoke_iter3_shrunk_v6_plus_velocity
- hypothesis: Smoke iter3: same anchor n=1000 + 4 fold-safe velocity features (n_txns_prev_60d/180d, avg_built_area_prev_60d, days_since_last_txn). Single-knob feature addition. Compare to Lane 2 (48772.08) for clean velocity lift.
- observation: pending: interpret fold/runtime signal before next action.
- comparison: pending: compare against previous, family best, and global best.
- significance: pending: apply pooled-std noise rule.
- attribution: one-knob work item; verify no bundled changes before promotion.
- next_hypothesis: pending: one-knob next action or gate decision.
