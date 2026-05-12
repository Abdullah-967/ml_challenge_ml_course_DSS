# Feature Lanes

Use this reference when defining fair smoke tests or deciding how to deepen a promising model family. A feature lane is a named, reproducible feature scope. It keeps model comparisons interpretable and prevents uncontrolled feature sprawl.

Feature lanes are broad context. For Stage 2 deepen and autoresearch, use
`feature_search_space.md` to name the concrete `hypothesis_unit` being tested
inside the lane.

## Table Of Contents

- [Shared Rules](#shared-rules)
- [`baseline_numeric`](#baseline_numeric)
- [`all_numeric`](#all_numeric)
- [`numeric_plus_basic_cats`](#numeric_plus_basic_cats)
- [`geo_signal`](#geo_signal)
- [`derived_ratios`](#derived_ratios)
- [`linear_interactions`](#linear_interactions)
- [Lane Selection By Family](#lane-selection-by-family)

## Shared Rules

- Run the three recommended Stage 1 lanes for the active family before deepening.
- Keep each lane stable across model families when the preprocessing is fair.
- Fit imputers, encoders, scalers, and any label-derived statistics inside CV folds.
- Do not use `dataset/test.json` to choose features.
- Record the lane name and feature count in `results.tsv`.
- For deepen/autoresearch feature work, record the concrete `hypothesis_unit`
  in the work item and reflection log.

## `baseline_numeric`

Purpose: fastest comparable baseline and sanity check.

Typical features:

```python
[
    "built_area",
    "num_lots",
    "land_area",
    "num_commercial",
]
```

Use for:

- all model families;
- quick smoke tests;
- debugging evaluator and artifact paths.

Do not over-interpret failure on this lane; some families need broader signal.

## `all_numeric`

Purpose: broad numeric signal without categorical complexity.

Definition:

- include all numeric and boolean columns available in the training records;
- exclude `property_value`;
- avoid columns that are IDs or target leaks if any appear.

Use for:

- tree ensembles and boosting as an early fair lane;
- linear models after imputation and scaling.

Watch for:

- sparse or mostly-missing numeric fields;
- booleans represented as objects or strings;
- unstable derived counts.

## `numeric_plus_basic_cats`

Purpose: add low-cardinality categorical signal without target encoding.

Candidate categorical features:

- property type or use category;
- date parts derived from construction/update dates;
- low-cardinality administrative labels;
- binary string flags.

Preprocessing:

- one-hot encode low-cardinality categoricals;
- cap or group rare categories if one-hot explosion is likely;
- fit encoders inside each fold through a pipeline.

Use for:

- linear models;
- tree bagging;
- XGBoost or boosting when explicit encoding is stable.

Watch for:

- high-cardinality geography leaking into enormous one-hot matrices;
- unseen categories at prediction time.

## `geo_signal`

Purpose: capture commune/departement/region price structure.

Candidate features:

- commune code or name;
- department/region code;
- latitude/longitude;
- fold-safe group medians or counts by geographic group;
- distance-like transforms only if derived from raw coordinates without test-informed tuning.

Preprocessing:

- non-target geographic fields can be encoded normally;
- target-derived group statistics must be learned inside each fold;
- use global training fallback values for unseen groups.

Use for:

- boosting and tree bagging;
- linear models with one-hot or fold-safe smoothed target encodings;
- possible blends if geography is complementary.

Watch for:

- target leakage from precomputed full-data medians;
- too many one-hot commune categories;
- test-set category inspection influencing feature choice.

## `derived_ratios`

Purpose: add domain-informed numeric structure.

Candidate features:

- built area per apartment;
- lots per section;
- commercial share;
- apartments per commune;
- log or capped versions of heavily skewed counts;
- missingness indicators for important numeric fields.

Rules:

- protect divisions with deterministic training-independent safeguards;
- keep derived features interpretable;
- add a small group at a time so effects can be attributed.

Use for:

- boosting and bagging;
- linear robust models after scaling.

Watch for:

- noisy ratios when denominators are tiny;
- duplicating information already captured by tree splits;
- over-deriving without CV improvement.

## `linear_interactions`

Purpose: let linear-style models capture limited nonlinear relationships.

Candidate transforms:

- `PolynomialFeatures(degree=2, interaction_only=True, include_bias=False)`;
- hand-picked interactions such as `built_area * latitude` only with a clear reason;
- log-transformed numeric variables before interactions if CV supports it.

Use for:

- `Ridge`;
- `Lasso`;
- `ElasticNet`;
- `HuberRegressor` if feature count stays manageable.

Do not use as a general feature lane for tree ensembles. Trees already model interactions through splits.

Watch for:

- feature explosion;
- slow linear solvers;
- unstable coefficients without scaling.

## Lane Selection By Family

Recommended Stage 1 smoke lanes:

```text
linear_robust: baseline_numeric, all_numeric, numeric_plus_basic_cats
tree_bagging: baseline_numeric, all_numeric, derived_ratios
boosting: all_numeric, numeric_plus_basic_cats, geo_signal
xgboost: all_numeric, numeric_plus_basic_cats, geo_signal
median_quantile: baseline_numeric, all_numeric, numeric_plus_basic_cats
```

If a lane is incompatible or too slow, document the reason in
`iteration_log.md` before leaving smoke. Only try `linear_interactions` after a
linear family has a reasonable baseline. Only try target-derived `geo_signal`
after reading `leakage_and_validation.md`.
