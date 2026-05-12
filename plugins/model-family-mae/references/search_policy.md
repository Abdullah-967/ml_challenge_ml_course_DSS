# Search Policy

Use this reference after the initial inventory and before choosing or advancing a model family.

## Table Of Contents

- [Inventory Inputs](#inventory-inputs)
- [Family Queue](#family-queue)
- [Selecting The Active Family](#selecting-the-active-family)
- [Stage Budgets](#stage-budgets)
- [Feature Hypothesis Units](#feature-hypothesis-units)
- [Advancement Rules](#advancement-rules)
- [Keep And Discard](#keep-and-discard)
- [Anti-Overload Rules](#anti-overload-rules)
- [Reporting Template](#reporting-template)

## Inventory Inputs

Read only enough to decide the next scoped action:

- root `results.tsv`: global best `cv_mae`, current champion recipe, slow or failed attempts;
- `experiments/*/`: which model families already have notebooks, artifacts, or per-family logs;
- current `experiment.py`: useful context for the champion, not the workspace for every family;
- `requirements.txt`: confirm whether optional families such as XGBoost are available.

Do not load every notebook end-to-end unless a specific family needs inspection. Summaries and filenames usually suffice for queue construction.

## Family Queue

Build a small queue, but execute only one active family:

```text
family	status	best_cv_mae	next_action	reason
hist_gradient_boosting	explored	52355.6899	park_or_promote	current champion already deepened
random_forest	queued	NA	smoke_test	unexplored bagging family
linear_robust	queued	NA	smoke_test	fast baseline and blend diversity
xgboost	queued	NA	smoke_test	installed, strong tabular candidate
```

Statuses:

- `queued`: worth testing later.
- `active`: current session's family.
- `deepening`: passed smoke tests and is exploring features.
- `tuning`: strong enough to tune.
- `parked`: stop for now; record why.
- `promoted`: human-accepted winner with notebook/artifacts.

## Selecting The Active Family

Pick the family with the best expected information gain under the runtime budget.

Prefer:

- underexplored families over already deepened HGB variants;
- fast families before expensive families when uncertainty is high;
- families that may add diversity for blending;
- families the user explicitly asks for;
- families with clear fair preprocessing.

Avoid:

- running the whole queue automatically;
- deepening two families in the same session;
- changing model family and feature strategy in a way that makes attribution impossible.

## Stage Budgets

Defaults are stated as **minimum, maximum** so the skill cannot exit a stage on a single positive observation. Both bounds are mandatory.

- Stage 1 smoke test: **min 3, max 3** runs per family on the lanes recommended in `feature_lanes.md` for that family. Run all three before any deepen decision. Skipping a recommended lane requires a written justification in `iteration_log.md`.
- Stage 2 feature deepening: **min 10, max 15** focused single-knob attempts after fair smoke scouting. Each feature/preprocessing attempt must name exactly one `hypothesis_unit` from `feature_search_space.md` or from documented dataset inspection. Each attempt's `next_hypothesis` MUST be informed by the prior iteration's observed evidence -- residuals, fold variance, runtime, or a visible dataset property -- not by a pre-baked grid.
- Stage 3 tuning: **min 10, max 15** focused single-knob hyperparameter attempts before park/promote decision. Mechanically-paired knobs (e.g. `learning_rate` and `n_estimators` paired to keep the step budget constant) count as one knob -- document the pairing. Same incremental-evidence rule as Stage 2.
- Stage 4 confirm: **min 2 seeds** (the canonical seed and at least one alternate shuffled 5-fold seed) before any promotion or "champion" wording.
- Normal eval target: under 5 minutes.
- Hard stop: kill or park runs over 10 minutes unless the user approves a long run.

If the family meets the autoresearch trigger (see [Autoresearch Trigger](#autoresearch-trigger) below), Stage 3 is replaced by the autoresearch loop, which has its own budget rules in `autoresearch_loop.md`.

If a run is slow but promising, reduce feature lanes, model size, or folds for local debugging, then return to canonical 5-fold CV for decisions.

## Feature Hypothesis Units

`feature_lane` is broad context, not the actual feature decision. During deepen
and autoresearch, every feature/preprocessing work item must name one
`hypothesis_unit` in the work item and reflection log. A unit may contain
multiple columns or transforms only when they are semantically or mechanically
linked and should be kept, dropped, or ablated together.

Examples:

- `property_transaction_categories`
- `room_layout_distribution`
- `area_density_ratios`
- `date_ordinal`
- `geo_granularity`
- `commune_frequency`

Do not advance with a vague label such as "deepen geo_signal" unless the exact
unit inside that lane is named. Use `references/feature_search_space.md` to
avoid overlooking available feature groups from `dataset/features.json`.

## Advancement Rules

A stage **cannot** advance until its minimum iteration count is met **and** every iteration has a corresponding entry in `experiments/<family>/iteration_log.md` per `reflection_protocol.md`.

### Smoke -> Deepen

After completing all three smoke runs, deepen if one of these is true:

- best family score beats the Ridge baseline clearly;
- best family score is within roughly 10-15% of the global champion and the family is underexplored;
- score is worse but the model is highly diverse and cheap enough for future blending;
- diagnostics suggest a missing fair preprocessing step rather than model weakness.

Two positive smoke runs are not enough. The third smoke run is part of the evidence base, not optional.

### Deepen -> Tune (or Autoresearch)

Advance from deepen to tune (or autoresearch) only after **at least 10** single-knob deepen iterations. The deepen iterations must each test a **distinct feature/preprocessing change**, not ten runs of the same idea, and each must be motivated by the previous iteration's observed evidence per `reflection_protocol.md`. The 10-iteration floor exists so the family's feature space is meaningfully explored before the tuning regime starts.

If the family hits the [Autoresearch Trigger](#autoresearch-trigger), enter that loop instead of Stage 3.

### Tune -> Confirm

Tune only if:

- the family completed deepen minimums;
- the family is already competitive after smoke/deepen;
- each tuning attempt has a clear purpose stated as a one-sentence hypothesis in `iteration_log.md`;
- the expected runtime is acceptable.

Advance to confirm only after **at least 10** single-knob tuning iterations and a written summary of what was learned. As with deepen, each iteration's choice must be motivated by the prior iteration's observation, not by a pre-baked grid.

### Confirm -> Promote

Park if:

- all fair smoke tests are clearly weak;
- runtime exceeds budget without a strong score;
- repeated crashes indicate brittle preprocessing;
- the family duplicates the current champion's behavior without improvement.

Promote only if **all** of:

- the family beats the global best by a **noise-aware margin** (`delta_mae <= -noise_band` per `reflection_protocol.md`), or is a confirmed diverse blend candidate explicitly approved by the user;
- the recipe has been confirmed with at least one second shuffled 5-fold seed or repeated KFold;
- if the recipe differs from the previous family best by more than one knob, the `ablation_summary` block from `ablation_protocol.md` exists in `iteration_log.md`;
- preprocessing is fold-safe and reproducible;
- the notebook/artifact layout can be written cleanly.

A within-noise tie versus the global champion is **not** grounds for promotion to global champion. It can still justify keeping the family as a confirmed contender for blending or as a faster runner-up, but the wording must be honest: "ties within fold noise", not "beats" or "champion".

## Autoresearch Trigger

When the active family completes smoke and deepen minimums and the best recipe satisfies either:

- `family_best.cv_mae` is within roughly 10 percent of the global champion, OR
- `family_best.cv_mae` beats the Ridge / HGB-default baseline by at least one full `cv_mae_std`,

the next stage is the **autoresearch loop** specified in `autoresearch_loop.md`, not regular Stage 3 tuning. The autoresearch loop replaces Stage 3 with a budgeted, anchored, single-knob exploration that runs until improvement plateaus or the iteration cap is hit.

If the user has explicitly asked the skill to "go deep", "explore thoroughly", "use autoresearch", or similar, treat the trigger as met as soon as smoke and deepen minimums are complete, regardless of the relative score.

After the autoresearch loop exits, run the ablation suite per `ablation_protocol.md` against the loop's entry anchor, then confirm seed stability, then decide promote / park.

## Keep And Discard

Significance uses pooled std (see `reflection_protocol.md` -> Significance Rules):

- `pooled_std = sqrt((std_A^2 + std_B^2) / 2)`
- `noise_band = 0.25 * pooled_std`

Within a family:

- **keep** if `delta_mae <= -noise_band` (clear improvement) **or** the result is `tie_within_noise` AND the new recipe is meaningfully simpler/faster.
- **discard** if it regresses (`delta_mae >= +noise_band`), crashes, or is `tie_within_noise` while adding complexity.
- **park** if the family has consumed its stage budgets without crossing a stage threshold.

For global champion status, be stricter: require confirmation **and** ablation (if multi-change) **and** a noise-aware win, before replacing the global best in narrative or promoted artifacts. A tie within noise is a tie -- never described as a "contender" without the user's explicit framing.

## Anti-Overload Rules

- Keep queue rows concise; do not paste full code or notebook output into notes.
- Store detailed run history in each family `results.tsv` and narrative reflection in `iteration_log.md`.
- Summarize only the best row per family when comparing globally.
- Prefer references over long prompt instructions.
- Stop and report when the next action would exceed the current stage budget, when the autoresearch loop hits a stop condition, or when an ablation suite is required.

## Isolation And Attribution Rules

These prevent the most common evidence failure: changing several knobs at once and producing an unattributed "win".

- **One knob per iteration.** A feature lane edit, a single hyperparameter, a preprocessing change, or a target transform. Not two.
- **Mechanically-paired knobs** (e.g. `learning_rate` halved with `n_estimators` doubled to keep total step budget constant) count as one knob. Document the pairing in `change_from_previous`.
- **No bundling capacity tuning with feature changes.** That mistake masked attribution in the May 5 xgboost run.
- **No mixing target transforms with anything else.** A log target change is its own iteration.
- If the user pushes back and asks for a multi-change run, do it -- but flag it `multi_change: true` in `iteration_log.md` and trigger `ablation_protocol.md` before any promotion or "champion" wording.

## Reporting Template

```text
Active family: <family>
Stage: <smoke|deepen|tune|confirm|promote|park>
Feature lane: <lane>
Best family CV MAE: <value> +/- <std>
Global best CV MAE: <value> +/- <std>
Decision: <keep|discard|park|deepen|tune|promote>
Reason: <one sentence>
Next action: <one scoped action>
```
