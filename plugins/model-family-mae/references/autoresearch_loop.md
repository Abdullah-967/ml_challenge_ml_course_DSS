# Autoresearch Loop

Use this reference once a model family has shown real potential and you are ready to extract the most out of it before moving on. The loop is inspired by Karpathy's `autoresearch` operating model: a fixed per-experiment budget, a single decision metric, isolated run copies, and many disciplined iterations against a clear anchor.

The previous skill version moved on after one or two tuning runs. That left signal on the table. This loop replaces "two attempts and out" with a budgeted, anchored, single-knob exploration that runs for **at least 10 iterations** before any plateau or diminishing-returns stop can fire, and continues up to the iteration cap if signal is still present.

## Table Of Contents

- [When To Enter The Loop](#when-to-enter-the-loop)
- [Borrowed Principles](#borrowed-principles)
- [Loop Inputs](#loop-inputs)
- [Loop Procedure](#loop-procedure)
- [Candidate Generation](#candidate-generation)
- [Anchor And Stop Conditions](#anchor-and-stop-conditions)
- [Recording](#recording)
- [Worked Example](#worked-example)
- [What This Loop Is Not](#what-this-loop-is-not)

## When To Enter The Loop

Enter once both are true:

1. The active family has completed Stage 1 smoke (all configured lanes) and Stage 2 deepen minimums (see `search_policy.md`), with at least one recipe `A` that meets either:
   - `A.cv_mae` is within roughly 10 percent of the global champion's `cv_mae`, **or**
   - `A.cv_mae` beats the simple baseline (Ridge / HGB defaults) by at least one full `cv_mae_std`.
2. The user has not asked to stop or to switch families.

If only one of those holds, do **not** enter the loop. Park or keep deepening with the regular Stage 2 / Stage 3 budgets.

If both hold and the user has said "explore this family thoroughly", "use autoresearch", "go deep", or similar, the loop becomes the default mode for the rest of the session.

## Borrowed Principles

From Karpathy's `autoresearch`:

- **Fixed per-iteration budget.** One canonical 5-fold CV run per iteration, target under 5 minutes, hard cap 10 minutes. If a candidate would exceed the cap, shrink it (fewer trees, smaller depth) before running, or skip it.
- **Single decision metric.** `cv_mae` from `scripts/eval_family.py`. Holdout, R^2, fold spread, and runtime are diagnostic, not decisive.
- **Isolated file to modify.** Prepare `experiments/<model_family>/runs/<run_id>/experiment.py` for each work item. Do not edit `current_experiment.py` or `best_experiment.py` directly.
- **Anchor on the best.** Every iteration is a one-knob delta from the current anchor recipe. The anchor only updates when a kept iteration produces an `improvement` per `reflection_protocol.md`.
- **Bounded autonomy via a written program.** This file is the program. Read it before each iteration; do not invent rules.

What does **not** carry over from `autoresearch`: latitude to change "everything is fair game" in one step. Our domain is small-data tabular regression where attribution matters more than wall-clock throughput, so we keep the **one-knob-per-iteration** rule from the ablation protocol.

## Loop Inputs

Before entering, write out the loop's state explicitly in `iteration_log.md` under a header `## autoresearch_start`:

```markdown
## autoresearch_start -- <run_id>

- **anchor_recipe:** <recipe id and short params summary>
- **anchor_cv_mae:** <value> +/- <std>
- **global_champion_cv_mae:** <value> +/- <std>
- **per_iteration_budget_seconds:** <e.g. 300>
- **min_iterations:** 10  # MANDATORY FLOOR -- plateau / diminishing stops cannot fire below this
- **plateau_patience:** <integer N, default 4>
- **max_iterations:** <integer M, default 20>
- **candidate_queue:** <ordered list of single-knob candidates, at least 12 entries; see below>
```

If you cannot fill all seven fields, or you cannot generate a candidate queue with at least 12 plausible single-knob entries for the active family, you are not ready for the loop. Go back to Stage 2 deepen.

## Loop Procedure

Repeat until a stop condition fires:

1. **Pop** the highest-priority candidate from `candidate_queue`. If the queue is empty and no stop condition has fired, regenerate per [Candidate Generation](#candidate-generation).
2. **Plan** a work item with `mfm_cli.py plan --write`, naming the single candidate in `description`, `params_summary`, and, for feature/preprocessing work, `hypothesis_unit`.
3. **Edit** only `runs/<run_id>/experiment.py` if the candidate requires code. The CLI preserves that prepared run copy.
4. **Run** `mfm_cli.py run "experiments/<model_family>/work_items/<run_id>.json"`.
5. **Reflect** with `mfm_cli.py reflect "experiments/<model_family>/runs/<run_id>/result.json"` and append an entry per `reflection_protocol.md`. `change_from_previous` must be exactly one knob.
6. **Decide** based on `significance`:
   - `improvement`: update the anchor to this recipe. Reset the no-improvement counter to zero. Regenerate or reorder the candidate_queue around the new anchor (e.g., extend the winning direction).
   - `tie_within_noise`: keep the simpler of the two recipes as anchor and increment the no-improvement counter.
   - `regression`: keep the anchor unchanged and increment the no-improvement counter.
7. **Check stop conditions** (see below). If any fires, exit the loop and proceed to ablation_protocol against the final anchor.

You may not skip step 4. A run without a reflection entry is not a data point and cannot move the anchor.

## Candidate Generation

Generate the queue from the anchor's family. Keep candidates **single-knob**, **independent**, and **runtime-respecting**. For feature/preprocessing candidates, name the concrete `hypothesis_unit` from `feature_search_space.md` or documented dataset inspection. Reasonable starter queues:

### XGBoost

```text
1. max_depth +1
2. max_depth +2
3. min_child_weight +5
4. min_child_weight x2
5. subsample 0.7 (down from 0.8)
6. colsample_bytree 0.7
7. reg_lambda x2
8. learning_rate 0.5x paired with n_estimators 2x (mechanical pair)
9. objective squared_error sanity check (only if absoluteerror is current)
10. enable_categorical with explicit cat list (if currently disabled)
```

### HistGradientBoosting

```text
1. max_leaf_nodes 2x
2. min_samples_leaf 0.5x
3. l2_regularization 10x
4. max_iter 2x paired with learning_rate 0.5x
5. categorical_features=auto vs explicit list
6. monotonic_cst on a single high-signal feature
7. loss absolute_error vs squared_error sanity check (if not already chosen)
```

### Linear Robust

```text
1. alpha sweep (one alpha at a time, e.g. {1, 10, 100, 1000})
2. switch Ridge -> Huber, alpha matched
3. switch Ridge -> ElasticNet, l1_ratio in {0.1, 0.5}
4. add log1p target (preprocessing-only knob)
5. drop linear_interactions if currently enabled, or add if currently disabled
```

### Tree Bagging

```text
1. max_depth +/- 4
2. min_samples_leaf 0.5x and 2x
3. max_features sqrt vs log2
4. n_estimators 2x (only after smaller forest is promising)
5. ExtraTrees vs RandomForest swap
```

Rules for queue construction:

- Order by **expected information gain per minute**, not by alphabetical.
- Prefer knobs with theoretical reason to help on this dataset (e.g., `max_depth` when the data has many strong interactions).
- Defer expensive knobs (large `n_estimators`, doubled `max_iter`) until cheaper ones plateau.
- A single knob may appear at multiple magnitudes (e.g., `max_depth +1` and `max_depth +2`) but only as separate queue entries.
- Feature candidates must name one attributable `hypothesis_unit`, such as `room_layout_distribution`, `date_ordinal`, or `property_transaction_categories`; avoid broad lane-only labels.

## Anchor And Stop Conditions

Stop the loop when the **first** of these fires, **subject to the minimum-iteration floor**:

- **Minimum-iteration floor (mandatory):** `iterations_run < min_iterations` (default 10) blocks Plateau and Diminishing-returns stops. The loop must run at least `min_iterations` canonical CV runs even if the no-improvement counter would otherwise fire. This exists because a 4-iteration plateau on a 6-iteration loop is just bad luck on candidate ordering, not real diminishing returns.
- **Plateau** (only after `iterations_run >= min_iterations`): `no_improvement_counter >= plateau_patience` consecutive iterations.
- **Budget**: `iterations_run >= max_iterations`. This is the only hard upper bound.
- **Wall clock**: cumulative loop runtime exceeds the user's session-level time budget if one was given.
- **Diminishing returns** (only after `iterations_run >= min_iterations`): the last `improvement` was smaller than `0.5 * noise_band` and the queue has no theoretically-stronger candidates left.
- **External**: user interrupts or asks to stop. This bypasses the floor.

If the queue empties before `min_iterations` is met, regenerate per [Candidate Generation](#candidate-generation) -- the floor is non-negotiable while there are plausible single-knob candidates to test. Each regenerated candidate must still be informed by accumulated evidence in `iteration_log.md` so the loop stays incremental rather than turning into a grid search.

When the loop exits, write an `## autoresearch_end` block to `iteration_log.md`:

```markdown
## autoresearch_end -- <run_id>

- **iterations_run:** <int> -- must be >= min_iterations unless stop_reason is wall_clock or external
- **improvements_kept:** <int>
- **stop_reason:** <plateau | budget | wall_clock | diminishing | external>
- **final_anchor_recipe:** <id and short params summary>
- **final_anchor_cv_mae:** <value> +/- <std>
- **delta_vs_anchor_at_start:** <delta_mae>
- **delta_vs_global_champion:** <delta_mae>
- **next_action:** ablate | confirm | promote | park | switch_family
```

After exit, the **default next action is the ablation suite** from `ablation_protocol.md` against the final anchor, especially if the loop accumulated several knob changes from the entry anchor. Then confirm seed stability per `leakage_and_validation.md` Section "Fixed-Fold Overfitting", then decide promote / park.

## Recording

Per iteration:

- one row in `experiments/<model_family>/results.tsv` with `stage=autoresearch` and `status` in `{keep, discard, anchor}`.
- one entry in `iteration_log.md` per `reflection_protocol.md`.

Use `status=anchor` for the row that re-establishes the current anchor (when an iteration produced an `improvement` and you adopted it). Use `status=keep` for ties you are keeping for simplicity. Use `status=discard` for regressions.

Do not write notebooks during the loop. Promotion artifacts are post-loop.

## Worked Example

Anchor at loop start: XGB depth=4, mcw=5, n=500, lr=0.05, lane=numeric_plus_basic_cats, target=raw, cv_mae 51,814 +/- 4,615. min_iterations=10, plateau_patience=4, max_iterations=20.

Queue (initial 12 candidates, ordered by expected information gain per minute):

1. max_depth +1 (-> 5)
2. max_depth +2 (-> 6)
3. min_child_weight +5 (-> 10)
4. learning_rate 0.5x paired with n_estimators 2x (-> 0.025, 1000)
5. add `built_per_room` ratio feature
6. add log1p target
7. subsample 0.7
8. colsample_bytree 0.7
9. reg_lambda x2
10. max_depth +3 (-> 7)
11. add `apartments_per_commune` ratio
12. min_child_weight x2 (-> 10) -- only if (3) was a regression so this tests the opposite direction

A plausible run:

- iter1: candidate 1, depth=5, cv_mae 51,290, `improvement` (-524 vs 51,814, noise_band ~ 1,150 -> just over half a band; flag as marginal). Anchor moves to depth=5.
- iter2: candidate 2, depth=6, cv_mae 50,930, `improvement`. Anchor moves to depth=6. Counter reset.
- iter3: candidate 4, lr=0.025 paired with n=1000, cv_mae 50,710, `improvement`. Anchor updates.
- iter4: candidate 5, ratios, cv_mae 50,690, `tie_within_noise`. Discard ratios for simplicity, increment counter to 1.
- iter5: candidate 6, log1p, cv_mae 50,720, `tie_within_noise`. Discard, counter 2.
- iter6: candidate 3, mcw=10, cv_mae 50,820, `regression`. Counter 3.
- iter7: candidate 7, subsample 0.7, cv_mae 50,750, `tie_within_noise`. Counter 4. **Plateau would fire here in the old policy, but `iterations_run = 7 < min_iterations = 10`, so the loop continues.**
- iter8: candidate 8, colsample_bytree 0.7, cv_mae 50,720, `tie_within_noise`. Counter 5 (plateau still suppressed by the floor).
- iter9: candidate 9, reg_lambda x2, cv_mae 50,790, `regression`. Counter 6.
- iter10: candidate 10, depth=7, cv_mae 50,520, `improvement` (-190 vs anchor 50,710, just over noise_band of ~1,165 -> marginal but the floor revealed it). Anchor moves to depth=7. Counter resets to 0. Floor satisfied.
- iter11: candidate 11, `apartments_per_commune` ratio, cv_mae 50,490, `tie_within_noise`. Counter 1.
- iter12: derived from iter10 (max_depth=8 to test direction), cv_mae 50,560, `regression` (depth=7 was the sweet spot). Counter 2.
- iter13: derived from iter10 (`min_child_weight`=3 to compensate for the deeper trees), cv_mae 50,470, `improvement`. Counter resets.
- iter14: subsample 0.6, `tie_within_noise`. Counter 1.
- iter15: re-test ratios on top of the new anchor (depth=7, mcw=3), `tie_within_noise`. Counter 2.
- iter16: queue regenerated; nothing remaining is theoretically stronger; `tie_within_noise`. Counter 3.
- iter17: `tie_within_noise`. Counter 4 -> plateau stop. Loop ends with `iterations_run=17`, well above the floor.

Final anchor: XGB depth=7, mcw=3, n=1000, lr=0.025, lane=numeric_plus_basic_cats, target=raw, cv_mae 50,470. Note that without the min-10 floor, the loop would have stopped at iter7 with cv_mae 50,710 and missed the depth=7 + mcw=3 region entirely. The floor is the difference between "early plateau because the cheap candidates ran out first" and actual diminishing returns.

After exit: run leave-one-out ablation on the kept changes vs the loop's entry anchor (depth, lr+n pair, mcw), then second-seed confirm, then promote.

## What This Loop Is Not

- It is **not** a license to bundle changes for speed. One knob per iteration, always.
- It is **not** a license to skip the reflection entry. No entry, no anchor update.
- It is **not** a hyperparameter grid search; the queue is ordered, prioritized, and pruned as it runs.
- It is **not** a substitute for ablation. After the loop, ablate the final delta vs the entry anchor.
- It is **not** for unproven families. Park weak families before considering this loop.

## TL;DR

When a family proves it has potential, enter a Karpathy-style autoresearch loop: fixed per-iteration budget, single CV MAE metric, one knob per iteration, anchored on the current best. **Floor: at least 10 iterations** before plateau / diminishing-returns can stop the loop; ceiling: `max_iterations` (default 20). Each iteration's candidate is informed by accumulated evidence in `iteration_log.md`. Reflect after every run. Ablate after the loop. Promote only what survives both.
