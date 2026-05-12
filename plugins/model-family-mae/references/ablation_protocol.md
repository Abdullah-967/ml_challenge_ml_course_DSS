# Ablation Protocol

Use this reference whenever a run with `multi_change: true` produced an apparent improvement, or whenever you are about to promote a recipe that bundles more than one change vs the previous family best. The protocol turns an unattributed gain into an attributed one.

## Table Of Contents

- [When This Triggers](#when-this-triggers)
- [Ablation Suite Layout](#ablation-suite-layout)
- [Decision Rules](#decision-rules)
- [Recording](#recording)
- [Worked Example](#worked-example)
- [Anti-Patterns](#anti-patterns)

## When This Triggers

Ablations are mandatory if either condition holds:

1. The most recent kept run has `multi_change: true` in `iteration_log.md` and was labelled `improvement` or close to it.
2. The recipe being considered for promotion differs from the previous family best by more than one knob (feature, hyperparameter, preprocessing, target transform).

Ablations are optional but recommended after any tuning sequence, to certify which knobs are load-bearing in the final recipe.

## Ablation Suite Layout

Define the multi-change winner as recipe `W`, and the prior family best as recipe `B`. Let the changes from `B` to `W` be `c1, c2, ..., ck` (each is one knob). Build a leave-one-out (LOO) suite:

```text
W                   = B + c1 + c2 + ... + ck      # the winner, already evaluated
W_minus_c1          = B +      c2 + ... + ck      # winner without c1
W_minus_c2          = B + c1 +      ... + ck      # winner without c2
...
W_minus_ck          = B + c1 + c2 + ...           # winner without ck
```

If `k` exceeds 4, prune the suite by dropping pairs that are mechanically linked (e.g. paired `learning_rate` and `n_estimators`) and ablating the pair as one unit. Document the pairing in `iteration_log.md`.

Each LOO run is a canonical 5-fold CV run via `scripts/eval_family.py`, with `--stage ablate` and `--description "ablate c<i>: drop <name>"`. Append the resulting row to the family `results.tsv` with `status=ablate`.

Do not run ablations as a separate notebook or with a separate evaluator; canonical CV is mandatory for them too.

## Decision Rules

For each LOO run, compute pooled-std significance vs `W` (the winner being challenged), using the rules in `reflection_protocol.md`:

- **drop hurts (`W_minus_ci` regresses vs `W` by at least `noise_band`)**: `c_i` is load-bearing. Keep it in the final recipe.
- **drop is a tie (`tie_within_noise`)**: `c_i` is **not** load-bearing. Prefer the simpler recipe; remove `c_i` from the promoted recipe unless it adds runtime safety, robustness, or interpretability you specifically want.
- **drop helps (`W_minus_ci` improves vs `W`)**: `c_i` was actively harmful in combination. Remove it and re-anchor `W` on `W_minus_ci`. Restart the suite from the new anchor.

After the suite, the **promoted recipe is the simplest variant within the noise band of the best LOO score**, not necessarily `W` itself.

## Recording

For every LOO run, append both:

1. A row to `experiments/<model_family>/results.tsv` with `status=ablate`.
2. An entry in `iteration_log.md` using the standard reflection format. `change_from_previous` for each LOO entry should reference the winner `W`, not `B`, since each LOO is a one-knob delta from `W`.

When the suite finishes, append a summary block to `iteration_log.md`:

```markdown
## ablation_summary -- after iter<N>

- **winner W:** <recipe id>, cv_mae <value>
- **load-bearing changes:** <list of c_i where drop hurt>
- **redundant changes:** <list of c_i where drop tied>
- **harmful changes:** <list of c_i where drop helped>
- **promoted recipe:** <simplified recipe id, possibly = W>
- **decision:** keep / promote / discard / re-anchor
```

A multi-change winner without an `ablation_summary` block is **not promotable**. Block any accepted-winner notebook/artifact generation and any "global contender" or "champion" wording until the summary exists.

## Worked Example

Suppose the family best `B` is XGB depth=4, n=500, lr=0.05, lane=numeric_plus_basic_cats, plain target. The candidate winner `W` adds:

- `c1`: `derived_ratios` lane (added 4 ratio features)
- `c2`: target = `log1p(property_value)`
- `c3_paired`: `max_depth=6` paired with `min_child_weight=10` (bundled as one knob because both control tree complexity)
- `c4_paired`: `n_estimators=1500` paired with `learning_rate=0.02` (bundled as one knob; total step budget is the linked quantity)

Suite (4 LOO runs):

```text
W_minus_c1: drop ratios (keep log1p, big trees, slow boost)
W_minus_c2: drop log1p (keep ratios, big trees, slow boost)
W_minus_c3: revert depth=4, mcw=5 (keep ratios, log1p, n=1500, lr=0.02)
W_minus_c4: revert n=500, lr=0.05 (keep ratios, log1p, big trees)
```

Possible outcomes and decisions:

- `W_minus_c4` regresses by 700, others tie within noise -> `c4_paired` (capacity tuning) is the only load-bearing change. Promoted recipe: `B + c4_paired` (drop the redundant ratios and log1p).
- `W_minus_c1` and `W_minus_c2` tie, `W_minus_c3` and `W_minus_c4` regress -> capacity tuning carries the gain. Same conclusion as above.
- `W_minus_c1` improves by 300 -> ratios were harmful in combination. Re-anchor and restart.

In all of these, the promoted recipe is shaped by data, not by the order in which knobs were stacked.

## Anti-Patterns

- **"It works, ship it."** Promoting a multi-change winner without ablation. Forbidden.
- **"Ablation is just for the notebook."** Running LOO with a different evaluator or smaller sample. Use canonical 5-fold CV.
- **"All four changes are obviously good."** Confirmation bias. The May 5 run "knew" capacity tuning, ratios, and log1p all helped, and got it wrong: capacity carried the gain on its own.
- **"Skip ablation if confirm passes."** Confirm only checks seed stability, not attribution. They are independent gates.

## TL;DR

A multi-change winner is unattributed until you run leave-one-out ablations on canonical CV and write an `ablation_summary` block. Promote the **simplest** recipe within the noise band of the winner -- often that means dropping bundled changes that turned out to be redundant.
