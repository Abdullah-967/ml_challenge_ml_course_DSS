# Reflection Protocol

Every canonical CV run must be followed by a written reflection entry **before** the next decision is made. This is the gate that turns "tool-call -> tool-call" into "observe -> hypothesize -> test -> reflect".

Read this reference at the start of every session and re-read it any time you are tempted to advance a stage on the strength of a single observation.

## Table Of Contents

- [Why This Exists](#why-this-exists)
- [Where Reflections Live](#where-reflections-live)
- [Required Entry Format](#required-entry-format)
- [Significance Rules](#significance-rules)
- [Attribution Rules](#attribution-rules)
- [Anti-Patterns](#anti-patterns)
- [Worked Examples](#worked-examples)

## Why This Exists

A previous run advanced from smoke -> deepen -> tune in three iterations, each time on a single observation, with multi-knob changes that made attribution impossible. The skill produced a verdict without producing evidence. This protocol forces the evidence step.

Operating principle: **a CV run that is not reflected on is not a data point.**

## Where Reflections Live

One markdown file per active family:

```text
experiments/<model_family>/iteration_log.md
```

Append one block per run, in chronological order. Never overwrite earlier entries. The header at the top of the file must be:

```markdown
# <model_family> Iteration Log

Append-only. One block per canonical CV run. See the bundled
`plugins/model-family-mae/references/reflection_protocol.md`.
```

`iteration_log.md` is human-readable narrative. `results.tsv` remains the structured run history. Both must agree on `run_id`, `cv_mae`, `cv_mae_std`, `runtime_seconds`, and `status`.

## Required Entry Format

Every entry should include these fields. Empty fields are not allowed; if a field does not apply, write `n/a` and explain why.

```markdown
## iter<N> -- <run_id>

- **stage:** smoke | deepen | tune | confirm | ablate | autoresearch
- **change_kind:** feature | preprocessing | target | hyperparameter |
  capacity_pair | diagnostic | n/a
- **hypothesis_unit:** the concrete attributable idea for feature/preprocessing
  runs, or `n/a` otherwise. A unit may contain multiple columns/transforms only
  when they are semantically or mechanically linked.
- **feature_group:** structural_numeric | room_layout | property_transaction |
  geography | date_time | derived_ratios | id_derived | n/a
- **anchor_run_id:** the run id this candidate is based on, or `n/a` for a
  first smoke/baseline run.
- **change_from_previous:** one sentence naming the SINGLE knob/feature/preprocessing
  change vs the immediate previous run, or "baseline" for iter1.
  If you changed more than one thing, list each on its own bullet and flag this entry
  as `multi_change: true` -- the ablation_protocol then becomes mandatory.
- **hypothesis:** what you expected to happen and why, in one or two sentences.
  Must be written BEFORE looking at the result.
- **observation:** cv_mae, cv_mae_std, runtime_seconds, fold-by-fold spread if notable.
- **comparison:**
  - vs immediate previous run: delta_mae, delta_std (use pooled std, see below).
  - vs family best so far: delta_mae.
  - vs global champion: delta_mae.
- **significance:** one of `improvement`, `tie_within_noise`, `regression`,
  with the threshold computed (see Significance Rules below).
- **attribution:** which change is responsible for the delta and how confident you are.
  If `multi_change: true`, you MUST write `unattributed -- ablation required` here.
- **next_hypothesis:** one scoped change to test next, named as a single knob.
  No "and"s. No "let's also...". One thing.
  Justification must come from evidence visible at write time, sourced from one of:
  (a) a property of THIS family's most recent run -- fold variance, residual
      pattern, runtime, observed under/overfit signal -- or
  (b) a property of the dataset itself visible by inspection -- cardinality,
      missingness rate, skewness, dtype.
  Cross-family priors, prior-run wins on the same dataset, and "we already
  know X works" are not valid justifications. They are author-list bias and
  must be rejected. If no within-family or within-dataset justification
  exists yet, the family is not ready to leave smoke -- run more smoke, do
  not invent a knob.
```

After writing the entry, decide the next action. Do not write the entry retroactively to justify a decision you have already taken.

## Significance Rules

The skill's old "0.25 * std" rule was applied loosely. Pin it down:

- **pooled_std** between runs A and B is `sqrt((std_A^2 + std_B^2) / 2)`.
- **noise_band** = `0.25 * pooled_std`.
- A delta is an `improvement` only if `delta_mae <= -noise_band`.
- A delta is a `regression` only if `delta_mae >= +noise_band`.
- Otherwise it is `tie_within_noise`.

Never call a `tie_within_noise` result a "contender", a "win", or "global best". A tie is a tie. The correct verbal labels are:

- `improvement`: keep, deepen further along this direction.
- `tie_within_noise`: discard if the change adds complexity; keep if it adds simplicity, speed, or diversity. Either way, do **not** advance to the next stage on a tie.
- `regression`: discard, and update next_hypothesis to back off the change.

For comparing a family best against the global champion, the same rule applies. A "confirmed contender" requires `delta_mae <= -noise_band` against the global champion **after** a second-seed confirmation, not before.

## Attribution Rules

You may only mark a result as `kept and attributed` if exactly one knob changed since the previous run. Definitions:

- **one knob**: one attributable `hypothesis_unit`, OR one model hyperparameter, OR one preprocessing change, OR one target transform. Not two unrelated ideas.
- **hypothesis unit**: a semantically or mechanically linked feature group such as `room_layout_distribution`, `area_density_ratios`, or `property_transaction_categories`.
- **adding ratios + switching to log1p target** = two knobs. Bundle is forbidden.
- **bumping max_depth and min_child_weight together** = two knobs. Bundle is forbidden.
- **changing model family + feature lane** = two knobs and not even comparable. Always forbidden.

Exceptions where bundling is allowed:

1. The two changes are mechanically linked (e.g. `learning_rate` and `n_estimators` paired so total step budget stays constant). Document the link in `change_from_previous`.
2. The user explicitly asks for a multi-change run. Still write `multi_change: true` and trigger the ablation_protocol before any promotion.

When `multi_change: true`, the next required action is the ablation suite from `ablation_protocol.md`, not the next stage.

## Anti-Patterns

These all happened in the May 5 xgboost run. None are allowed under this protocol:

- "Lane 2 came back better, lane 3 unnecessary, advancing to deepen." -> violates the smoke-stage minimum (see search_policy.md).
- "Added ratios and log1p together, result tied, must be depth too small." -> attribution invented from a multi-knob run.
- "Bumped depth, mcw, lr, and n_estimators, got the family best." -> unattributed gain, must be ablated before any promotion or champion claim.
- "Beats global champion by 182 with std 4800, calling it a contender." -> within noise, must be labelled `tie_within_noise` and treated as a tie until proven otherwise.

## Worked Examples

### Good entry

```markdown
## iter3 -- 20260506-153054

- **stage:** deepen
- **change_kind:** feature
- **hypothesis_unit:** area_density_ratios
- **feature_group:** derived_ratios
- **anchor_run_id:** iter2
- **change_from_previous:** added `built_per_room` ratio feature only;
  log1p target deferred to a separate iter.
- **hypothesis:** structural ratio should help XGB carve out high-density
  apartment markets that pure built_area cannot represent. Expect
  delta_mae roughly -300 to -800.
- **observation:** cv_mae 51,510, cv_mae_std 4,690, runtime 32 s.
- **comparison:**
  - vs iter2 (cats): delta_mae -304, pooled_std 4,653, noise_band 1,163.
  - vs family best: delta_mae -304.
  - vs global champion HGB iter21 50,934: delta_mae +576.
- **significance:** tie_within_noise (|delta| 304 < noise_band 1,163).
- **attribution:** ratio feature alone did not move the needle; consistent
  with HGB experience that ratios help only after capacity is sized up.
- **next_hypothesis:** keep the ratio (free, simple), and as a SEPARATE iter
  test log1p target on top. Do not bundle.
```

### Bad entry (do not write entries like this)

```markdown
## iter4

Bumped depth=6, n=1500, lr=0.02, mcw=10, added log1p target. Got 50,752,
beats champion. Calling it a contender, moving to confirm.
```

This entry violates: single-knob rule, hypothesis-before-result rule, significance computation, attribution rule, and the contender-vs-tie distinction.

## TL;DR

After every canonical CV run, append a structured entry to `iteration_log.md` with hypothesis, observation, pooled-std-aware significance, and explicit attribution. One knob per run. A tie within noise is a tie, never a contender. No entry, no next decision.
