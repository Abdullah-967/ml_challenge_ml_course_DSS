# xgboost_v10 Iteration Log

Append-only. One block per canonical CV run. See the bundled `plugins/model-family-mae/references/reflection_protocol.md`.

Required metadata per entry: stage, change_kind, hypothesis_unit, feature_group, anchor_run_id, change_from_previous, hypothesis, observation, comparison, significance, attribution, next_hypothesis.

## 20260510-125151-smoke-transfer_only_3

- stage: smoke
- feature_lane: transfer_only_3
- change_kind: feature
- hypothesis_unit: transfer_mode_triplet
- feature_group: id_derived
- anchor_run_id: n/a
- status: keep
- cv_mae: 90419.8077262329
- cv_mae_std: 5300.75173403007
- runtime_seconds: 28.18734140007291
- change_from_previous: smoke_iter1_transfer_only_3
- hypothesis: Smoke iter1 (signal isolation): XGBoost on 3 transfer-mode features (n_transferred, transfer_overlap_ratio, is_no_transfer) derived from parcel_ids vs transferred_parcel_ids set arithmetic. Tests whether the 32% no_transfer / 66% full_match / 1.5% partial split (median 80k vs 118k) predicts in isolation. Baseline-3-style.
- observation: pending: interpret fold/runtime signal before next action.
- comparison: pending: compare against previous, family best, and global best.
- significance: pending: apply pooled-std noise rule.
- attribution: one-knob work item; verify no bundled changes before promotion.
- next_hypothesis: pending: one-knob next action or gate decision.

## 20260510-125333-smoke-shrunk_v6_anchor

- stage: smoke
- feature_lane: shrunk_v6_anchor
- change_kind: feature
- hypothesis_unit: shrunk_v6_anchor_baseline
- feature_group: structural_numeric
- anchor_run_id: n/a
- status: keep
- cv_mae: 48441.68952092821
- cv_mae_std: 4771.498055018735
- runtime_seconds: 429.3990835000295
- change_from_previous: smoke_iter2_shrunk_v6_anchor
- hypothesis: Smoke iter2: re-establish v6 anchor at smoke speed (top5 sub-models, n_est=2000) without transfer features. Sets the baseline for measuring transfer-feature lift in Lane 3.
- observation: pending: interpret fold/runtime signal before next action.
- comparison: pending: compare against previous, family best, and global best.
- significance: pending: apply pooled-std noise rule.
- attribution: one-knob work item; verify no bundled changes before promotion.
- next_hypothesis: pending: one-knob next action or gate decision.

## 20260510-130153-smoke-shrunk_v6_plus_transfer

- stage: smoke
- feature_lane: shrunk_v6_plus_transfer
- change_kind: feature
- hypothesis_unit: transfer_mode_features_added_to_anchor
- feature_group: id_derived
- anchor_run_id: 20260510-125333-smoke-shrunk_v6_anchor
- status: timeout
- cv_mae: None
- cv_mae_std: None
- runtime_seconds: 600.3263701999094
- change_from_previous: smoke_iter3_shrunk_v6_plus_transfer
- hypothesis: Smoke iter3: same shrunk v6 anchor as Lane 2 + 4 transfer-mode features (n_transferred, n_parcels_kept, transfer_overlap_ratio, is_no_transfer). Single-knob feature addition. Compare to Lane 2 (48441.69) for incremental lift.
- observation: pending: interpret fold/runtime signal before next action.
- comparison: pending: compare against previous, family best, and global best.
- significance: pending: apply pooled-std noise rule.
- attribution: one-knob work item; verify no bundled changes before promotion.
- next_hypothesis: pending: one-knob next action or gate decision.

## 20260510-131411-deepen-shrunk_v6_anchor_n1000

- stage: deepen
- feature_lane: shrunk_v6_anchor_n1000
- change_kind: hyperparameter
- hypothesis_unit: anchor_n1000
- feature_group: structural_numeric
- anchor_run_id: n/a
- status: keep
- cv_mae: 48772.080477082185
- cv_mae_std: 4836.538701790976
- runtime_seconds: 205.87313700001687
- change_from_previous: deepen_iter1_anchor_n1000
- hypothesis: Deepen iter1: re-anchor at n_est=1000 (vs Lane 2's 2000) so iter2 with transfer features fits the 10-min budget. Establishes the runtime-safe deepen baseline.
- observation: pending: interpret fold/runtime signal before next action.
- comparison: pending: compare against previous, family best, and global best.
- significance: pending: apply pooled-std noise rule.
- attribution: one-knob work item; verify no bundled changes before promotion.
- next_hypothesis: pending: one-knob next action or gate decision.

## 20260510-131835-deepen-shrunk_v6_anchor_n1000_plus_transfer

- stage: deepen
- feature_lane: shrunk_v6_anchor_n1000_plus_transfer
- change_kind: feature
- hypothesis_unit: transfer_mode_features_added_to_anchor
- feature_group: id_derived
- anchor_run_id: 20260510-131411-deepen-shrunk_v6_anchor_n1000
- status: keep
- cv_mae: 48589.87782870345
- cv_mae_std: 4902.626715200254
- runtime_seconds: 195.77267239999492
- change_from_previous: deepen_iter2_plus_transfer4
- hypothesis: Deepen iter2 (single-knob feature addition): anchor n=1000 + 4 transfer-mode features (n_transferred, n_parcels_kept, transfer_overlap_ratio, is_no_transfer). Compare to iter1 (48772.08) for clean transfer-feature lift.
- observation: pending: interpret fold/runtime signal before next action.
- comparison: pending: compare against previous, family best, and global best.
- significance: pending: apply pooled-std noise rule.
- attribution: one-knob work item; verify no bundled changes before promotion.
- next_hypothesis: pending: one-knob next action or gate decision.
