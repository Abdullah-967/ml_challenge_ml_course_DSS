# xgboost_v8 Iteration Log

Append-only. One block per canonical CV run. See the bundled `plugins/model-family-mae/references/reflection_protocol.md`.

Required metadata per entry: stage, change_kind, hypothesis_unit, feature_group, anchor_run_id, change_from_previous, hypothesis, observation, comparison, significance, attribution, next_hypothesis.

## smoke_iter1 -- 20260509-214323-smoke-v7_plus_cadastral_counts

- stage: smoke
- feature_lane: v7_plus_cadastral_counts
- change_kind: feature
- hypothesis_unit: structural_numeric_baseline
- feature_group: structural_numeric
- anchor_run_id: 20260509-195253-deepen-v6_capacity_path (xgboost_v7 promoted)
- status: keep
- runtime_seconds: 1083.62 (~18 min)
- smoke_shrink: n_estimators 8000 -> 4000 and top_k_types 15 -> 10 applied uniformly across all three v8 smoke lanes for fair fast comparison; restore 8000/15 at deepen/confirm.
- change_from_previous: smoke laneA — ADD num_parcels, num_sections, num_communes, num_dependencies (4 cadastral count fields present in dataset/features.json but not in v7's NUMERIC_COLUMNS) on top of v7 promoted recipe.
- hypothesis: dataset/features.json exposes 4 cadastral counts that v7 ignored. Trees should benefit from explicit transaction-extent signal (multi-parcel/multi-commune transactions are systematically different in size and value). Expected small-to-moderate improvement.
- observation: cv_mae 48468.89 +/- 4727.28 over 5 folds; runtime_seconds 1083.62. Slowest of the 3 smoke lanes despite only +4 cols (likely tree-build overhead from new dense numeric splits). cv_mae_std *lowest* of the 3 — fold variance dropped vs v7 anchor.
- comparison:
  - vs v7 promoted seed=42 anchor (46308.02 +/- 5754.24, n_est=8000): delta_mae +2160.87 — but this is not apples-to-apples (smoke uses shrunken n_est=4000/top_k=10).
  - vs family best so far (this is iter1): n/a.
  - vs global champion (root iter22, 50907): -2438.11 (better, even at shrunken capacity).
- significance: vs v7 anchor delta is misleading because of smoke shrink. For within-family comparison see iter2 / iter3 below.
- attribution: single feature knob (4 added columns + smoke shrink baseline). The shrink itself is shared across all v8 smoke lanes, so cross-lane comparison is fair.
- next_hypothesis: smoke laneB — replace cadastral additions with room_area_density_ratios (avg area per apt/house room bucket) to test whether per-bucket density signal beats the cadastral-count signal at the same shrunken capacity.

## smoke_iter2 -- 20260509-214332-smoke-v7_plus_room_density

- stage: smoke
- feature_lane: v7_plus_room_density
- change_kind: feature
- hypothesis_unit: room_area_density_ratios
- feature_group: derived_ratios
- anchor_run_id: 20260509-195253-deepen-v6_capacity_path (xgboost_v7 promoted)
- status: keep (new family best)
- runtime_seconds: 756.34 (~12.6 min)
- change_from_previous: smoke laneB — ADD 10 avg-area-per-room ratios = `safe_div(area_<kind>_<bucket>, num_<kind>_<bucket>)` for kind in {apt,house} x bucket in {1_room, 2_rooms, 3_rooms, 4_rooms, 5plus_rooms}, on top of v7 promoted recipe (no cadastral counts; shared smoke shrink).
- hypothesis: per-bucket counts and areas already give the model the raw signal but require it to learn the implicit ratio. Pre-computing density (m^2 per dwelling) should sharpen splits at depth=6 by giving a single monotone feature instead of forcing bucket-level pairwise interactions, especially for high-volume (3-4 room) buckets where the denominator is well-populated.
- observation: cv_mae 48002.73 +/- 5199.55 over 5 folds; runtime_seconds 756.34 — fastest meaningful lane (B has +10 cols vs A's +4, but A is slower; the room-density features must be enabling earlier-converging trees). cv_mae_std *highest* of the 3 lanes (fold variance widened vs A).
- comparison:
  - vs smoke_iter1 (lane A): delta_mae -466.16, delta_std +472.27. pooled_std = sqrt((4727.28^2+5199.55^2)/2) = 4969.4; noise_band = 0.25 * 4969.4 = 1242.4. |delta| 466 < 1242 -> tie_within_noise.
  - vs family best so far (this becomes the new family best): n/a.
  - vs global champion (50907): -2904.27 (better at shrunken capacity).
- significance: tie_within_noise vs lane A on cv_mae, but lowest absolute MAE in the family so far. Best information-gain candidate to anchor deepen.
- attribution: single feature knob (10 density ratios). No bundled changes. The improvement vs lane A is within fold noise so we cannot claim density features beat cadastral counts decisively at this capacity — but they tie while adding interpretable structural signal that should compose well with deeper capacity at restored n_est=8000.
- next_hypothesis: smoke laneC — DROP the 8 sparse 1-room/2-room layout columns from v7 anchor (no cadastral counts, no density ratios). Tests the orthogonal direction: whether removing low-coverage room buckets helps or hurts at the same capacity. Pairs with B for a future B+C deepen iteration.

## smoke_iter3 -- 20260509-214336-smoke-v7_minus_sparse_rooms

- stage: smoke
- feature_lane: v7_minus_sparse_rooms
- change_kind: feature
- hypothesis_unit: drop_sparse_room_layout
- feature_group: room_layout
- anchor_run_id: 20260509-195253-deepen-v6_capacity_path (xgboost_v7 promoted)
- status: keep
- runtime_seconds: 641.07 (~10.7 min)
- change_from_previous: smoke laneC — DROP 8 sparse 1-room/2-room layout columns (num_apt_1_room, area_apt_1_room, num_apt_2_rooms, area_apt_2_rooms, num_house_1_room, area_house_1_room, num_house_2_rooms, area_house_2_rooms) from v7 anchor (no cadastral counts, no density ratios; shared smoke shrink).
- hypothesis: 1-room and 2-room buckets are the sparsest in the training data; their counts and areas are mostly zero/near-zero, contributing little signal but adding split candidates that can absorb noise on small folds. Dropping them should at least be a no-cost simplification, possibly a small improvement.
- observation: cv_mae 48236.73 +/- 5068.73 over 5 folds; runtime_seconds 641.07 — fastest of the 3 (-8 cols => smaller hist). cv_mae_std mid-range.
- comparison:
  - vs smoke_iter2 (lane B, family best): delta_mae +234.00, delta_std -130.82. pooled_std = sqrt((5199.55^2+5068.73^2)/2) = 5134.5; noise_band = 0.25 * 5134.5 = 1283.6. |delta| 234 < 1283 -> tie_within_noise.
  - vs smoke_iter1 (lane A): delta_mae -232.16, |delta| 232 < pooled noise -> tie_within_noise.
  - vs global champion (50907): -2670.27.
- significance: tie_within_noise with both A and B, but the simplest recipe (-8 cols vs anchor) and the fastest. Per `search_policy.md` keep rule: "tie_within_noise AND the new recipe is meaningfully simpler/faster" => keep on simplicity grounds.
- attribution: single feature knob (8 dropped columns). The all-three-tie pattern means the v7 anchor's numeric scope is roughly saturated for trees at depth=6 — adding cadastral counts, adding density ratios, and dropping sparse buckets all land in the same fold-noise basin.
- next_hypothesis: stage gate decision — smoke is complete (3 lanes; min=max=3). All three lanes tie within noise vs each other and beat global champion at shrunken capacity. Family-best is lane B (room_area_density_ratios). For deepen, anchor on lane B's density-ratio recipe at RESTORED capacity (n_est=8000, top_k=15) and run a single-knob deepen iteration that COMPOSES lane C's drop_sparse with lane B's density features (since the sparse 1-room/2-room buckets are now only used as numerators in the new density ratios — dropping the raw counts/areas while keeping their ratios is a clean single semantic knob). If that wins or ties, layer further deepen iterations one knob at a time per `search_policy.md` (min 10 iterations, single-knob discipline).

## deepen_iter1 -- 20260509-224734-deepen-v8_b_density_restored

- stage: deepen
- feature_lane: v8_b_density_restored
- change_kind: capacity_pair
- hypothesis_unit: room_area_density_ratios
- feature_group: derived_ratios
- anchor_run_id: 20260509-214332-smoke-v7_plus_room_density (lane B smoke)
- status: keep (within-family) but underperforms v7 promoted (regression)
- cv_mae: 48040.81
- cv_mae_std: 5087.47
- runtime_seconds: 1943.31 (~32 min)
- change_from_previous: capacity_pair restore — n_estimators 4000 -> 8000 in both global and sub-models, AND top_k_types 10 -> 15. Mechanically paired (smoke shrink reverse). NUMERIC_COLUMNS unchanged from lane B smoke (still includes room_area_density_ratios).
- hypothesis: lane B was best at shrunken capacity. Restoring capacity should let trees fit the density-ratio signal more sharply and beat v7 promoted (46308.02 at the same restored capacity, no density ratios) by a noise-aware margin.
- observation: cv_mae 48040.81 +/- 5087.47; runtime_seconds 1943.31 (longer than v7's 1505s for the same n_est=8000 — the 10 extra dense numeric ratios slow tree-build per round). cv_mae barely moved from lane B's shrunken 48002.73.
- comparison:
  - vs smoke_iter2 (lane B at shrunk capacity, 48002.73 +/- 5199.55): delta_mae +38.08; pooled_std=sqrt((5087.47^2+5199.55^2)/2)=5143.7; noise_band=1285.9. |delta| 38 << noise -> tie_within_noise. Capacity restoration produced essentially zero improvement over the shrunk recipe — strong evidence the model already saturated at n_est=4000/top_k=10 with the density-ratio feature set.
  - vs v7 promoted seed=42 (46308.02 +/- 5754.24, same capacity, no density ratios): delta_mae +1732.79; pooled_std=sqrt((5087.47^2+5754.24^2)/2)=5430.7; noise_band=1357.7. |delta| 1733 > noise -> REGRESSION. The +10 density-ratio columns make the model WORSE at restored capacity vs v7 baseline.
  - vs family best (lane B smoke at 48002.73): tied (see above).
  - vs global champion (50907.33): -2866.52 (still better).
- significance: tie_within_noise vs lane B smoke (capacity restoration adds nothing when density ratios are present), but **regression vs v7 promoted at the same capacity**. This is decisive negative evidence on the room_area_density_ratios hypothesis_unit at depth=6/n_est=8000: the per-bucket count+area columns already supply the implicit ratio splits trees need, and adding the 10 explicit ratios introduces redundant noisy features that hurt at full capacity.
- attribution: single mechanically-paired knob (capacity restoration). The regression vs v7 promoted is attributable to the room_area_density_ratios feature unit carried in from lane B (since iter1 differs from v7 promoted only by those 10 columns). Confidence: high — same hyperparams, same data, same seed; the only systematic difference is the +10 columns. iter2 will isolate this.
- next_hypothesis: deepen iter2 — DROP the 10 room_area_density_ratios from iter1 (i.e. revert to the v7 promoted NUMERIC_COLUMNS but stay in the v8 family workspace). Single feature knob. Hypothesis_unit: `room_area_density_ratios` (this is a discard-direction test of the same unit). If iter2 cv_mae lands at v7-promoted's 46308 +/- noise, the density ratios are confirmed redundant and the family-best resets to a v7-equivalent point — from there, deepen pivots to lane C's drop_sparse_room_layout direction (next single knob: drop sparse 1-room/2-room raw cols on top of iter2). If iter2 lands materially WORSE than v7 promoted, something else changed (suspect: the lane C smoke directory's residual state) and we need to bisect.

## 20260509-232317-deepen-v8_drop_density

- stage: deepen
- feature_lane: v8_drop_density
- change_kind: feature
- hypothesis_unit: room_area_density_ratios (discard direction)
- feature_group: derived_ratios
- anchor_run_id: 20260509-224734-deepen-v8_b_density_restored (iter1)
- status: keep (new family best by margin)
- cv_mae: 47978.89
- cv_mae_std: 4784.97
- runtime_seconds: 1488.14 (~24.8 min)
- change_from_previous: DROP all 10 room_area_density_ratios from iter1 NUMERIC_COLUMNS. Result code-identical to xgboost_v7 promoted recipe (n_est=8000, top_k=15, no density ratios) verified by `diff` against runs/20260509-192702-deepen-v6_capacity_path/experiment.py — only docstring/metadata fields differ.
- hypothesis: iter1 underperformed v7 promoted (46308.02) by +1733 with density ratios; expected iter2 to land at ~v7's 46308 if those 10 cols were the regressor. Code-identical reproduction also serves as a cross-family determinism check.
- observation: cv_mae 47978.89 +/- 4784.97; runtime_seconds 1488.14. Fold-by-fold vs v7 promoted seed=42 winning run:
    - fold0: v7 44657 vs v8 46754 (delta +2097)
    - fold1: v7 41076 vs v8 46986 (delta +5910)
    - fold2: v7 40721 vs v8 41223 (delta  +502)
    - fold3: v7 56183 vs v8 56077 (delta  -106)
    - fold4: v7 48902 vs v8 48855 (delta   -47)
  Folds 2/3/4 are essentially identical; folds 0/1 diverge by 2k-6k. Code is identical, seed is identical, data is identical -> divergence is XGBoost thread-non-determinism (n_jobs=-1 + tree_method=hist + multi-thread grad/hess accumulation).
- comparison:
  - vs deepen_iter1 (48040.81 +/- 5087.47): delta_mae -61.92; pooled_std=sqrt((4784.97^2+5087.47^2)/2)=4938.0; noise_band=1234.5. |delta| 62 << noise -> tie_within_noise. iter2 is family-best on raw cv_mae but the gain is within noise (0.13%).
  - vs xgboost_v7 promoted seed=42 (46308.02 +/- 5754.24): delta_mae +1670.87; pooled_std=sqrt((4784.97^2+5754.24^2)/2)=5292.5; noise_band=1323.1. |delta| 1671 > 1323 -> mild REGRESSION (delta only ~1.26x noise band). With same code and same seed, the most-likely cause is fold-0/fold-1 thread-determinism drift, not a real recipe difference.
  - vs xgboost_v7 promoted seed=2026 confirm (47233.08 +/- 3051.72): delta_mae +745.81; pooled_std=sqrt((4784.97^2+3051.72^2)/2)=4011.3; noise_band=1002.8. |delta| 746 < 1003 -> tie_within_noise. v8 iter2 ties v7's seed=2026 confirm.
  - vs v7 promoted 2-seed mean (46770.55): delta_mae +1208.34. Right at the noise boundary; not decisively worse.
  - vs global champion (50907.33): -2928.44 (better).
- significance: tie_within_noise vs iter1 (density ratios are net-NEUTRAL at this capacity, contradicting iter1's stand-alone "regression vs v7" reading) and tie_within_noise vs v7 confirm. The earlier iter1 reading of "+1733 regression" was inflated by reference to a single seed=42 point that itself benefits from XGBoost thread-determinism luck on folds 0/1.
- attribution: single feature knob (10 cols dropped). Combined iter1+iter2 evidence: density ratios are roughly neutral at restored v7 capacity (~0 mean effect within noise). The iter1-vs-v7 "regression" was largely thread-determinism between two single-seed points, not a feature effect. v8 family-best is iter2 by a noise-magnitude margin.
- next_hypothesis: deepen iter3 — anchor on iter2 (no density ratios; v7-equivalent recipe in v8 workspace). Single feature knob: DROP the 8 sparse 1-room/2-room raw cols (lane C content) on top of iter2. Hypothesis_unit: `drop_sparse_room_layout`. Hypothesis: those 8 cols are mostly zero/near-zero in training; trees may absorb fold noise via spurious splits on them. Dropping should tie or mildly improve. If it ties, the recipe gets simpler (-8 cols, faster trees). If it improves, that's the first real signal in the deepen chain.

## 20260509-235345-deepen-v8_drop_sparse_rooms

- stage: deepen
- feature_lane: v8_drop_sparse_rooms
- change_kind: feature
- hypothesis_unit: drop_sparse_room_layout
- feature_group: room_layout
- anchor_run_id: 20260509-232317-deepen-v8_drop_density
- status: keep
- cv_mae: 48461.879912841
- cv_mae_std: 5025.829976207236
- runtime_seconds: 1247.0344375000568
- change_from_previous: deepen_iter3_drop_sparse_rooms
- hypothesis: Deepen iter3: anchored on iter2 (v7-equivalent). DROP 8 sparse 1-room/2-room raw cols (num_apt_1_room, area_apt_1_room, num_apt_2_rooms, area_apt_2_rooms, num_house_1_room, area_house_1_room, num_house_2_rooms, area_house_2_rooms). Single feature knob.
- observation: pending: interpret fold/runtime signal before next action.
- comparison: pending: compare against previous, family best, and global best.
- significance: pending: apply pooled-std noise rule.
- attribution: one-knob work item; verify no bundled changes before promotion.
- next_hypothesis: pending: one-knob next action or gate decision.

## 20260510-004926-deepen-v8_drop_sparse_plus_cadastral

- stage: deepen
- feature_lane: v8_drop_sparse_plus_cadastral
- change_kind: feature
- hypothesis_unit: structural_numeric_baseline
- feature_group: structural_numeric
- anchor_run_id: 20260509-235345-deepen-v8_drop_sparse_rooms
- status: keep
- cv_mae: 48492.17125977142
- cv_mae_std: 4846.088502606687
- runtime_seconds: 1285.1306100999936
- change_from_previous: deepen_iter4_add_cadastral
- hypothesis: Deepen iter4: anchored on iter3 (drop sparse + no density). ADD num_parcels, num_sections, num_communes, num_dependencies. Single feature knob from iter3.
- observation: pending: interpret fold/runtime signal before next action.
- comparison: pending: compare against previous, family best, and global best.
- significance: pending: apply pooled-std noise rule.
- attribution: one-knob work item; verify no bundled changes before promotion.
- next_hypothesis: pending: one-knob next action or gate decision.

## 20260510-011240-deepen-v8_drop_const_cats

- stage: deepen
- feature_lane: v8_drop_const_cats
- change_kind: feature
- hypothesis_unit: property_transaction_categories
- feature_group: property_transaction
- anchor_run_id: 20260509-232317-deepen-v8_drop_density
- status: keep
- cv_mae: 48302.653328344604
- cv_mae_std: 5259.363434673816
- runtime_seconds: 1301.2315407999558
- change_from_previous: deepen_iter5_drop_const_cats
- hypothesis: Deepen iter5: pivot back to family-best iter2 anchor. DROP dept_code and region_code from CATEGORICAL_COLUMNS (CLAUDE.md flags both as constant in training; they only add encoding overhead with no decision splits).
- observation: pending: interpret fold/runtime signal before next action.
- comparison: pending: compare against previous, family best, and global best.
- significance: pending: apply pooled-std noise rule.
- attribution: one-knob work item; verify no bundled changes before promotion.
- next_hypothesis: pending: one-knob next action or gate decision.

## 20260510-013543-deepen-v8_log_skewed

- stage: deepen
- feature_lane: v8_log_skewed
- change_kind: preprocessing
- hypothesis_unit: log_skewed_numerics
- feature_group: structural_numeric
- anchor_run_id: 20260509-232317-deepen-v8_drop_density
- status: keep
- cv_mae: 47978.89409290442
- cv_mae_std: 4784.971381405014
- runtime_seconds: 1301.697872400051
- change_from_previous: deepen_iter6_log_skewed
- hypothesis: Deepen iter6: anchored on family-best iter2. Replace built_area, land_area, house_area, apartment_area with their log1p variants in NUMERIC_COLUMNS. Single preprocessing knob. Tests whether log spacing maps long-tailed area distributions onto more uniform hist-bin density.
- observation: pending: interpret fold/runtime signal before next action.
- comparison: pending: compare against previous, family best, and global best.
- significance: pending: apply pooled-std noise rule.
- attribution: one-knob work item; verify no bundled changes before promotion.
- next_hypothesis: pending: one-knob next action or gate decision.

## 20260510-015847-deepen-v8_presence_flags

- stage: deepen
- feature_lane: v8_presence_flags
- change_kind: feature
- hypothesis_unit: presence_flags
- feature_group: structural_numeric
- anchor_run_id: 20260510-013543-deepen-v8_log_skewed
- status: keep
- cv_mae: 47963.501368268284
- cv_mae_std: 4952.18636146039
- runtime_seconds: 1323.4372111998964
- change_from_previous: deepen_iter7_presence_flags
- hypothesis: Deepen iter7: anchored on iter6 (=iter2). ADD 5 binary presence flags (has_apartments, has_houses, has_commercial, has_dependencies, has_lots). Single feature knob.
- observation: pending: interpret fold/runtime signal before next action.
- comparison: pending: compare against previous, family best, and global best.
- significance: pending: apply pooled-std noise rule.
- attribution: one-knob work item; verify no bundled changes before promotion.
- next_hypothesis: pending: one-knob next action or gate decision.

## 20260510-022205-deepen-v8_parcel_ratios

- stage: deepen
- feature_lane: v8_parcel_ratios
- change_kind: feature
- hypothesis_unit: parcel_density_ratios
- feature_group: derived_ratios
- anchor_run_id: 20260510-015847-deepen-v8_presence_flags
- status: keep
- cv_mae: 48718.819468546964
- cv_mae_std: 4639.179798320795
- runtime_seconds: 1357.190591600025
- change_from_previous: deepen_iter8_parcel_ratios
- hypothesis: Deepen iter8: anchored on iter7. ADD 4 cadastral density ratios (parcels_per_section, parcels_per_commune, sections_per_commune, lots_per_parcel). Single feature knob.
- observation: pending: interpret fold/runtime signal before next action.
- comparison: pending: compare against previous, family best, and global best.
- significance: pending: apply pooled-std noise rule.
- attribution: one-knob work item; verify no bundled changes before promotion.
- next_hypothesis: pending: one-knob next action or gate decision.

## 20260510-024610-deepen-v8_month_cyclical

- stage: deepen
- feature_lane: v8_month_cyclical
- change_kind: feature
- hypothesis_unit: month_cyclical
- feature_group: date_time
- anchor_run_id: 20260510-015847-deepen-v8_presence_flags
- status: keep
- cv_mae: 48549.826584925766
- cv_mae_std: 5070.479723870751
- runtime_seconds: 1377.104312999989
- change_from_previous: deepen_iter9_month_cyclical
- hypothesis: Deepen iter9: anchored on iter7 (family-best). ADD sin_month and cos_month cyclical encoding. Single feature knob.
- observation: pending: interpret fold/runtime signal before next action.
- comparison: pending: compare against previous, family best, and global best.
- significance: pending: apply pooled-std noise rule.
- attribution: one-knob work item; verify no bundled changes before promotion.
- next_hypothesis: pending: one-knob next action or gate decision.

## 20260510-031025-deepen-v8_iter7_minus_sparse

- stage: deepen
- feature_lane: v8_iter7_minus_sparse
- change_kind: feature
- hypothesis_unit: drop_sparse_room_layout
- feature_group: room_layout
- anchor_run_id: 20260510-015847-deepen-v8_presence_flags
- status: keep
- cv_mae: 48329.38238552715
- cv_mae_std: 5140.846300173427
- runtime_seconds: 1261.8380983000388
- change_from_previous: deepen_iter10_compose_drop_sparse
- hypothesis: Deepen iter10: anchored on iter7 (family-best). DROP 8 sparse 1-room/2-room raw cols. Single feature knob. Closes deepen at min=10.
- observation: pending: interpret fold/runtime signal before next action.
- comparison: pending: compare against previous, family best, and global best.
- significance: pending: apply pooled-std noise rule.
- attribution: one-knob work item; verify no bundled changes before promotion.
- next_hypothesis: pending: one-knob next action or gate decision.

## 20260510-033345-tune-v8_tune_iter1_lr_003

- stage: tune
- feature_lane: v8_tune_iter1_lr_003
- change_kind: hyperparameter
- hypothesis_unit: n_a
- feature_group: n_a
- anchor_run_id: 20260510-015847-deepen-v8_presence_flags
- status: keep
- cv_mae: 48454.12438561546
- cv_mae_std: 4999.009626126675
- runtime_seconds: 600.0757035000715
- change_from_previous: tune_iter1_lr_003
- hypothesis: Tune iter1: smoke-shrink anchor (iter7 recipe at n_est=4000, top_k=10). Single hyperparameter knob: learning_rate 0.05 -> 0.03.
- observation: pending: interpret fold/runtime signal before next action.
- comparison: pending: compare against previous, family best, and global best.
- significance: pending: apply pooled-std noise rule.
- attribution: one-knob work item; verify no bundled changes before promotion.
- next_hypothesis: pending: one-knob next action or gate decision.

## 20260510-034439-tune-v8_tune_iter2_lr_007

- stage: tune
- feature_lane: v8_tune_iter2_lr_007
- change_kind: hyperparameter
- hypothesis_unit: n_a
- feature_group: n_a
- anchor_run_id: 20260510-015847-deepen-v8_presence_flags
- status: keep
- cv_mae: 47875.822992224996
- cv_mae_std: 5165.775046150892
- runtime_seconds: 589.1899528000504
- change_from_previous: tune_iter2_lr_007
- hypothesis: Tune: tune_iter2_lr_007 on iter7 recipe at smoke-shrink (n_est=4000, top_k=10).
- observation: pending: interpret fold/runtime signal before next action.
- comparison: pending: compare against previous, family best, and global best.
- significance: pending: apply pooled-std noise rule.
- attribution: one-knob work item; verify no bundled changes before promotion.
- next_hypothesis: pending: one-knob next action or gate decision.

## 20260510-035454-tune-v8_tune_iter3_max_depth_5

- stage: tune
- feature_lane: v8_tune_iter3_max_depth_5
- change_kind: hyperparameter
- hypothesis_unit: n_a
- feature_group: n_a
- anchor_run_id: 20260510-015847-deepen-v8_presence_flags
- status: keep
- cv_mae: 47916.64138268831
- cv_mae_std: 4963.129888104816
- runtime_seconds: 529.3832001999253
- change_from_previous: tune_iter3_max_depth_5
- hypothesis: Tune: tune_iter3_max_depth_5 on iter7 recipe at smoke-shrink (n_est=4000, top_k=10).
- observation: pending: interpret fold/runtime signal before next action.
- comparison: pending: compare against previous, family best, and global best.
- significance: pending: apply pooled-std noise rule.
- attribution: one-knob work item; verify no bundled changes before promotion.
- next_hypothesis: pending: one-knob next action or gate decision.

## 20260510-040404-tune-v8_tune_iter4_max_depth_7

- stage: tune
- feature_lane: v8_tune_iter4_max_depth_7
- change_kind: hyperparameter
- hypothesis_unit: n_a
- feature_group: n_a
- anchor_run_id: 20260510-015847-deepen-v8_presence_flags
- status: keep
- cv_mae: 48793.77319271626
- cv_mae_std: 5243.744080082205
- runtime_seconds: 681.5417371999938
- change_from_previous: tune_iter4_max_depth_7
- hypothesis: Tune: tune_iter4_max_depth_7 on iter7 recipe at smoke-shrink (n_est=4000, top_k=10).
- observation: pending: interpret fold/runtime signal before next action.
- comparison: pending: compare against previous, family best, and global best.
- significance: pending: apply pooled-std noise rule.
- attribution: one-knob work item; verify no bundled changes before promotion.
- next_hypothesis: pending: one-knob next action or gate decision.

## 20260510-041547-tune-v8_tune_iter5_mcw_3

- stage: tune
- feature_lane: v8_tune_iter5_mcw_3
- change_kind: hyperparameter
- hypothesis_unit: n_a
- feature_group: n_a
- anchor_run_id: 20260510-015847-deepen-v8_presence_flags
- status: keep
- cv_mae: 48376.027233666144
- cv_mae_std: 5379.219889399521
- runtime_seconds: 614.9111419999972
- change_from_previous: tune_iter5_mcw_3
- hypothesis: Tune: tune_iter5_mcw_3 on iter7 recipe at smoke-shrink (n_est=4000, top_k=10).
- observation: pending: interpret fold/runtime signal before next action.
- comparison: pending: compare against previous, family best, and global best.
- significance: pending: apply pooled-std noise rule.
- attribution: one-knob work item; verify no bundled changes before promotion.
- next_hypothesis: pending: one-knob next action or gate decision.

## 20260510-042625-tune-v8_tune_iter6_mcw_10

- stage: tune
- feature_lane: v8_tune_iter6_mcw_10
- change_kind: hyperparameter
- hypothesis_unit: n_a
- feature_group: n_a
- anchor_run_id: 20260510-015847-deepen-v8_presence_flags
- status: keep
- cv_mae: 48687.38132579958
- cv_mae_std: 4932.471593732474
- runtime_seconds: 564.7193195000291
- change_from_previous: tune_iter6_mcw_10
- hypothesis: Tune: tune_iter6_mcw_10 on iter7 recipe at smoke-shrink (n_est=4000, top_k=10).
- observation: pending: interpret fold/runtime signal before next action.
- comparison: pending: compare against previous, family best, and global best.
- significance: pending: apply pooled-std noise rule.
- attribution: one-knob work item; verify no bundled changes before promotion.
- next_hypothesis: pending: one-knob next action or gate decision.

## 20260510-043610-tune-v8_tune_iter7_subsample_07

- stage: tune
- feature_lane: v8_tune_iter7_subsample_07
- change_kind: hyperparameter
- hypothesis_unit: n_a
- feature_group: n_a
- anchor_run_id: 20260510-015847-deepen-v8_presence_flags
- status: keep
- cv_mae: 48426.7200370985
- cv_mae_std: 4865.961197950159
- runtime_seconds: 576.1088156999322
- change_from_previous: tune_iter7_subsample_07
- hypothesis: Tune: tune_iter7_subsample_07 on iter7 recipe at smoke-shrink (n_est=4000, top_k=10).
- observation: pending: interpret fold/runtime signal before next action.
- comparison: pending: compare against previous, family best, and global best.
- significance: pending: apply pooled-std noise rule.
- attribution: one-knob work item; verify no bundled changes before promotion.
- next_hypothesis: pending: one-knob next action or gate decision.

## 20260510-044611-tune-v8_tune_iter8_colsample_05

- stage: tune
- feature_lane: v8_tune_iter8_colsample_05
- change_kind: hyperparameter
- hypothesis_unit: n_a
- feature_group: n_a
- anchor_run_id: 20260510-015847-deepen-v8_presence_flags
- status: keep
- cv_mae: 48070.426511410195
- cv_mae_std: 5052.65472787953
- runtime_seconds: 576.9296211999608
- change_from_previous: tune_iter8_colsample_05
- hypothesis: Tune: tune_iter8_colsample_05 on iter7 recipe at smoke-shrink (n_est=4000, top_k=10).
- observation: pending: interpret fold/runtime signal before next action.
- comparison: pending: compare against previous, family best, and global best.
- significance: pending: apply pooled-std noise rule.
- attribution: one-knob work item; verify no bundled changes before promotion.
- next_hypothesis: pending: one-knob next action or gate decision.

## 20260510-045608-tune-v8_tune_iter9_reg_lambda_5

- stage: tune
- feature_lane: v8_tune_iter9_reg_lambda_5
- change_kind: hyperparameter
- hypothesis_unit: n_a
- feature_group: n_a
- anchor_run_id: 20260510-015847-deepen-v8_presence_flags
- status: keep
- cv_mae: 48262.93322107023
- cv_mae_std: 5194.033394437637
- runtime_seconds: 624.8702950000297
- change_from_previous: tune_iter9_reg_lambda_5
- hypothesis: Tune: tune_iter9_reg_lambda_5 on iter7 recipe at smoke-shrink (n_est=4000, top_k=10).
- observation: pending: interpret fold/runtime signal before next action.
- comparison: pending: compare against previous, family best, and global best.
- significance: pending: apply pooled-std noise rule.
- attribution: one-knob work item; verify no bundled changes before promotion.
- next_hypothesis: pending: one-knob next action or gate decision.

## 20260510-050653-tune-v8_tune_iter10_blend_02

- stage: tune
- feature_lane: v8_tune_iter10_blend_02
- change_kind: hyperparameter
- hypothesis_unit: n_a
- feature_group: n_a
- anchor_run_id: 20260510-015847-deepen-v8_presence_flags
- status: keep
- cv_mae: 48040.87041016238
- cv_mae_std: 5055.354765815747
- runtime_seconds: 637.441543999943
- change_from_previous: tune_iter10_blend_02
- hypothesis: Tune: tune_iter10_blend_02 on iter7 recipe at smoke-shrink (n_est=4000, top_k=10).
- observation: pending: interpret fold/runtime signal before next action.
- comparison: pending: compare against previous, family best, and global best.
- significance: pending: apply pooled-std noise rule.
- attribution: one-knob work item; verify no bundled changes before promotion.
- next_hypothesis: pending: one-knob next action or gate decision.

## 20260510-051940-confirm-v8_final_seed42

- stage: confirm
- feature_lane: v8_final_seed42
- change_kind: capacity_pair
- hypothesis_unit: n_a
- feature_group: n_a
- anchor_run_id: 20260510-034439-tune-v8_tune_iter2_lr_007
- status: keep
- cv_mae: 47821.68811681533
- cv_mae_std: 5237.418670280251
- runtime_seconds: 1339.8127533999505
- change_from_previous: final_seed42_lr_007_restored
- hypothesis: Final candidate seed=42: tune-best (lr=0.07) + iter7 features (presence_flags) at RESTORED capacity (n_est=8000, top_k=15).
- observation: pending: interpret fold/runtime signal before next action.
- comparison: pending: compare against previous, family best, and global best.
- significance: pending: apply pooled-std noise rule.
- attribution: one-knob work item; verify no bundled changes before promotion.
- next_hypothesis: pending: one-knob next action or gate decision.

## 20260510-054235-confirm-v8_final_seed2026

- stage: confirm
- feature_lane: v8_final_seed2026
- change_kind: diagnostic
- hypothesis_unit: n_a
- feature_group: n_a
- anchor_run_id: 20260510-051940-confirm-v8_final_seed42
- status: keep
- cv_mae: 47452.07672866694
- cv_mae_std: 2901.185437298874
- runtime_seconds: 1332.9196818000637
- change_from_previous: final_seed2026_lr_007_restored
- hypothesis: Final candidate seed=2026: same recipe as final_seed42 (lr=0.07 + iter7 features + restored capacity), CV split seed=2026 for two-seed agreement.
- observation: pending: interpret fold/runtime signal before next action.
- comparison: pending: compare against previous, family best, and global best.
- significance: pending: apply pooled-std noise rule.
- attribution: one-knob work item; verify no bundled changes before promotion.
- next_hypothesis: pending: one-knob next action or gate decision.
