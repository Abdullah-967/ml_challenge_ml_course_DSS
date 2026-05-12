# Practical Notebooks Reference

Use this reference when choosing a model family, defining fair smoke tests, explaining a modeling move, or writing notebook narrative. It maps course-practical lessons into the `property_value` MAE challenge without copying large notebook outputs.

## Table Of Contents

- [Sources](#sources)
- [General Modeling Discipline](#general-modeling-discipline)
- [Decision Trees And Ensembles](#decision-trees-and-ensembles)
- [Gradient Descent, Scaling, And Robust Loss](#gradient-descent-scaling-and-robust-loss)
- [Gradient Boosted Trees](#gradient-boosted-trees)
- [Small Grid Style](#small-grid-style)
- [Notebook Narrative Style](#notebook-narrative-style)
- [What To Borrow And What Not To Borrow](#what-to-borrow-and-what-not-to-borrow)

## Sources

- `practicals_notebooks/2_decision_trees_ANS.ipynb`: decision-tree complexity, train/development/test discipline, overfitting, bagging, random forests.
- `practicals_notebooks/3_gradient_descent_ANS.ipynb`: MAE/R2 reporting, feature scaling, learning-rate thinking, robust losses such as Huber.
- `practicals_notebooks/4_gradient_boosted_trees_ANS.ipynb`: boosting as staged weak learners, tuning `n_estimators`, `learning_rate`, `loss`, and small-grid model selection.

## General Modeling Discipline

The practicals separate training, development/validation, and final testing. Apply the same discipline here:

- model and feature choices come from CV/validation only;
- final test predictions are generated only after selection;
- evaluation uses the challenge metric, MAE;
- every experiment should answer one modeling question.

Good questions:

- Does a robust linear model become competitive when scaled and encoded correctly?
- Does a bagging family add useful nonlinear signal compared with boosting?
- Does geography help only when handled fold-safely?
- Does MAE-aligned boosting loss beat squared-error loss?

Weak questions:

- What happens if we change ten model and feature settings at once?
- Can we inspect the test distribution to choose encoders?
- Can we run every model family in one session?

## Decision Trees And Ensembles

From the decision-tree practical:

- deep trees can memorize training data;
- shallow trees underfit but are easier to generalize;
- bagging reduces variance by averaging many trees;
- random forests add feature randomness to decorrelate trees.

Challenge translation:

- use `max_depth`, `max_leaf_nodes`, and `min_samples_leaf` as first complexity controls;
- treat fold variance as a warning sign for brittle trees;
- compare bagging families on the same feature lane before tuning;
- prefer runtime-capped forests before very large forests.

Useful first move:

```python
RandomForestRegressor(
    n_estimators=200,
    max_depth=18,
    min_samples_leaf=2,
    max_features="sqrt",
    n_jobs=-1,
    random_state=42,
)
```

## Gradient Descent, Scaling, And Robust Loss

From the gradient-descent practical:

- feature scale matters for optimization;
- MAE and R2 communicate different aspects of model quality;
- learning-rate and loss choices affect convergence and robustness;
- Huber-style loss can reduce outlier sensitivity.

Challenge translation:

- scale numeric features for `Ridge`, `Lasso`, `ElasticNet`, `HuberRegressor`, and other gradient/linear solvers;
- do not scale tree ensembles by default;
- report MAE as the selection metric and R2 only as supporting context in notebooks;
- try robust linear models when extreme property values dominate errors.

Useful first move:

```python
Pipeline([
    ("preprocessor", preprocessor),
    ("model", HuberRegressor(max_iter=1000, alpha=0.0001)),
])
```

If Huber is slow or unstable, step back to `Ridge` or reduce feature width.

## Gradient Boosted Trees

From the gradient-boosting practical:

- boosting improves by fitting sequential learners to remaining errors;
- learning rate and number of estimators trade off;
- loss choice should align with the metric;
- small grids are easier to reason about than broad searches.

Challenge translation:

- because the challenge metric is MAE, try `loss="absolute_error"` early for sklearn HGBR;
- tune paired settings such as learning rate and iteration count together;
- adjust tree complexity with leaves/depth and `min_samples_leaf`;
- use XGBoost as a separate model family, not just a drop-in replacement, because runtime and objectives differ.

Useful first move:

```python
HistGradientBoostingRegressor(
    loss="absolute_error",
    max_iter=300,
    learning_rate=0.05,
    max_leaf_nodes=31,
    min_samples_leaf=20,
    l2_regularization=0.1,
    random_state=42,
    early_stopping=True,
)
```

## Small Grid Style

When a family reaches tuning, use small grids that preserve interpretability:

```python
settings = []
for max_leaf_nodes in [15, 31, 63]:
    model = HistGradientBoostingRegressor(
        loss="absolute_error",
        max_leaf_nodes=max_leaf_nodes,
        learning_rate=0.05,
        max_iter=300,
        random_state=42,
    )
    model.fit(X_train, y_train)
    predictions = model.predict(X_valid)
    settings.append((max_leaf_nodes, mean_absolute_error(y_valid, predictions)))
```

In the model-family workflow, prefer committing the single best setting as the next canonical run. Do not embed a costly search inside every CV fold unless the search itself is the deliberate experiment.

## Notebook Narrative Style

When promoting a family into a notebook, follow the teaching style of the practicals:

- state the modeling question before code;
- explain why preprocessing is fair for the model family;
- explain why the metric/loss matches MAE;
- report holdout metrics and CV metrics once;
- discuss overfitting risk through complexity and fold variance;
- keep code cells small enough that the modeling idea is visible.

## What To Borrow And What Not To Borrow

Borrow:

- model-complexity reasoning;
- train/dev/test discipline;
- MAE-centered reporting;
- scaling for linear/gradient methods;
- ensemble variance intuition;
- small-grid tuning.

Do not borrow blindly:

- classification-only metrics or losses;
- visualization-heavy notebook cells that do not guide this challenge;
- full practical code blocks that do not match the JSON-record challenge interface;
- test-set evaluation patterns that would violate challenge rules.
