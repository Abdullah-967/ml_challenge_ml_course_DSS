# Leakage And Validation

Use this reference whenever a feature lane uses categoricals, geography, group statistics, target encoding, log targets, blends, or final promotion checks.

## Table Of Contents

- [Canonical Verdict](#canonical-verdict)
- [Test Set Rule](#test-set-rule)
- [Fold-Safe Preprocessing](#fold-safe-preprocessing)
- [Target Encoding And Group Statistics](#target-encoding-and-group-statistics)
- [Log Targets](#log-targets)
- [Clipping](#clipping)
- [Fixed-Fold Overfitting](#fixed-fold-overfitting)
- [Blends](#blends)
- [Runtime Versus Validity](#runtime-versus-validity)

## Canonical Verdict

The decision metric is 5-fold CV MAE from bundled `scripts/eval_family.py`.

Notebook holdout metrics are useful for explanation and MLflow comparison, but they do not override canonical CV.

## Test Set Rule

`dataset/test.json` is for final predictions only.

Do not use test records to:

- choose feature columns;
- inspect category coverage before choosing encoders;
- set clipping bounds;
- tune hyperparameters;
- decide whether a family should be parked or promoted.

It is fine for a final trained pipeline to transform test records using preprocessing learned from the full training data.

## Fold-Safe Preprocessing

Every learned transformation must be fit on the training split inside the fold:

- imputers;
- scalers;
- one-hot encoders;
- ordinal encoders;
- rare-category groupers;
- group medians/counts;
- target encoders;
- clipping bounds derived from target distribution;
- blend weights.

Safe outside the fold:

- deterministic column selection based on schema and domain reasoning;
- arithmetic transforms that do not use target values;
- parsing dates into year/month/age-like features;
- fixed constants known before seeing validation labels.

## Target Encoding And Group Statistics

Target-derived features are high risk and often high value for geography. Implement them as transformers or fold-local helper functions.

Rules:

- compute group statistics from the fold's training records only;
- apply to validation records with a global training fallback;
- smooth small groups toward the global mean/median;
- never precompute medians on the full dataset before CV;
- log the grouping key and smoothing rule in `params_summary`.

Example concept:

```python
group_median = train_frame.groupby("commune")["property_value"].median()
global_median = train_frame["property_value"].median()
valid_frame["commune_target_median"] = (
    valid_frame["commune"].map(group_median).fillna(global_median)
)
```

In actual CV code, wrap this logic so the evaluator only sees fold-trained transformations.

## Log Targets

A log target can help with right-skewed prices, but it changes the error profile.

If using `log1p(property_value)`:

- train on log targets inside each fold;
- transform predictions back with `expm1`;
- clip negative predictions if needed after inverse transform;
- judge only by original-scale MAE;
- watch for underprediction of expensive properties.

Do not assume log targets help; compare with canonical CV.

## Clipping

Prediction clipping can reduce extreme-error damage but can also hide underfitting.

Allowed clipping:

- bounds computed from training targets inside each fold;
- simple quantiles such as 0.5th and 99.5th percentile;
- documented in `params_summary`.

Not allowed:

- bounds inferred from validation errors after repeated probing;
- bounds inferred from `dataset/test.json`.

## Fixed-Fold Overfitting

Repeatedly probing the same 5 folds can overfit the leaderboard even without test leakage.

Mitigations:

- keep run counts budgeted;
- change one idea at a time;
- record discarded attempts;
- do not declare global champion status from a tiny fixed-fold improvement;
- confirm finalists with a second shuffled 5-fold seed or repeated KFold.

Default confirmation:

```python
KFold(n_splits=5, shuffle=True, random_state=2026)
```

Promote if the confirmed score remains competitive within fold noise.

## Blends

Blend validation must be fold-safe:

1. For each fold, train every base model on the fold's training records.
2. Predict the fold's validation records.
3. Combine validation predictions with fixed or fold-trained weights.
4. Score original-scale MAE.

Do not train base models on full data and evaluate blend weights on the same training rows.

## Runtime Versus Validity

For debugging, it is acceptable to run a smaller local check. For any keep, park, tune, promote, or global comparison decision, return to canonical 5-fold CV.

If the canonical run is too slow:

- reduce model complexity;
- reduce feature lane width;
- park the family as too slow;
- ask the user before approving a long run.
