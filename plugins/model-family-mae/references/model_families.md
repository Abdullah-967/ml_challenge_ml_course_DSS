# Model Families

Use this reference when selecting the active family or defining fair smoke-test defaults. The goal is to compare families under sensible preprocessing, not to tune every estimator.

## Table Of Contents

- [Shared Rules](#shared-rules)
- [Linear Robust](#linear-robust)
- [Tree Bagging](#tree-bagging)
- [Boosting](#boosting)
- [XGBoost](#xgboost)
- [Median And Quantile](#median-and-quantile)
- [Blends](#blends)

## Shared Rules

- Keep the first run simple and fast.
- Use `random_state=42` wherever the estimator supports it.
- Do not use `dataset/test.json` for any decision.
- Match preprocessing to the model family.
- Record enough params in `params_summary` to reproduce the run.
- If a model cannot fit within the runtime budget, reduce complexity before parking.

## Linear Robust

Purpose: fast baseline, interpretable coefficients, and diversity for future blends.

Good first models:

- `LinearRegression`
- `Ridge`
- `Lasso`
- `ElasticNet`
- `HuberRegressor`

Fair preprocessing:

- impute numeric features;
- one-hot encode low-cardinality categoricals when used;
- scale dense numeric features with `StandardScaler`;
- use `PolynomialFeatures` only in the `linear_interactions` feature lane.

Smoke defaults:

```python
Pipeline([
    ("preprocessor", preprocessor),
    ("model", Ridge(alpha=10.0)),
])
```

High-yield tuning:

- `alpha` for `Ridge`, `Lasso`, `ElasticNet`;
- `l1_ratio` for `ElasticNet`;
- `epsilon` and `alpha` for `HuberRegressor`;
- log-target comparison only if evaluated directly with canonical CV.

Failure modes:

- unscaled inputs make optimization unstable;
- high-cardinality one-hot features can be slow or noisy;
- interactions can explode feature count quickly.

## Tree Bagging

Purpose: nonlinear baseline with variance reduction and different bias from boosting.

Good first models:

- `RandomForestRegressor`
- `ExtraTreesRegressor`

Fair preprocessing:

- impute numeric features;
- ordinal or one-hot encode categoricals only if the lane calls for them;
- no scaling needed.

Smoke defaults:

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

High-yield tuning:

- `max_depth`;
- `min_samples_leaf`;
- `max_features`;
- `n_estimators` only after a smaller forest is promising.

Failure modes:

- slow CV when trees are large;
- weak extrapolation on expensive properties;
- categorical encodings can create artificial order if not chosen carefully.

## Boosting

Purpose: strong tabular candidate and current known champion family.

Good first models:

- `HistGradientBoostingRegressor`
- `GradientBoostingRegressor`

Fair preprocessing:

- impute or let HGBR handle numeric missing values where appropriate;
- encode categoricals only if the chosen implementation and feature lane support it safely;
- no scaling needed.

Smoke defaults:

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

High-yield tuning:

- `loss`: prioritize `"absolute_error"` because the challenge metric is MAE;
- `learning_rate` and `max_iter` pairs such as `(0.1, 150)`, `(0.05, 300)`, `(0.02, 500)`;
- `max_leaf_nodes`;
- `min_samples_leaf`;
- `l2_regularization`.

Failure modes:

- fixed-fold overfitting after too many small tweaks;
- early stopping behavior can vary with validation split;
- HGBR is already explored, so only deepen when there is a clear new idea.

## XGBoost

Purpose: strong external gradient-boosted-tree family now that `xgboost` is listed in `requirements.txt`.

Use only after confirming import availability in the environment.

Fair preprocessing:

- impute numeric features or use XGBoost-compatible missing values;
- encode categoricals explicitly unless using a carefully supported categorical mode;
- no scaling needed.

Smoke defaults:

```python
XGBRegressor(
    objective="reg:absoluteerror",
    n_estimators=500,
    learning_rate=0.05,
    max_depth=4,
    min_child_weight=5,
    subsample=0.8,
    colsample_bytree=0.8,
    reg_lambda=1.0,
    tree_method="hist",
    n_jobs=-1,
    random_state=42,
)
```

If `reg:absoluteerror` is unavailable in the installed version, fall back to `objective="reg:squarederror"` and judge by CV MAE.

High-yield tuning:

- `max_depth`;
- `min_child_weight`;
- `subsample`;
- `colsample_bytree`;
- `reg_lambda`;
- `learning_rate` with `n_estimators`.

Failure modes:

- version-specific objective names;
- long CV runtime;
- overfitting if depth and trees grow together.

## Median And Quantile

Purpose: robust alternatives for skewed target distributions.

Candidate models:

- `QuantileRegressor` only on small/simple feature sets;
- `GradientBoostingRegressor(loss="quantile", alpha=0.5)` if runtime is acceptable.

Use strict runtime safeguards. These are not first-choice broad families unless outliers dominate errors.

## Blends

Purpose: combine independently strong and diverse families.

Do not blend until at least two confirmed families exist. A blend must be evaluated fold-safely:

- train each base model inside the fold;
- combine validation predictions inside the fold;
- tune blend weights using training/CV only;
- confirm before promotion.

Start with simple weighted averages. Do not introduce stacking unless there is enough evidence and runtime budget.
