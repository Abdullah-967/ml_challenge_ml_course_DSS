# Feature Search Space

Use this reference when planning feature or preprocessing exploration. It is
derived from `dataset/features.json` and the observed training schema. The goal
is to name concrete, attributable hypothesis units without turning the workflow
into one-run-per-column feature selection.

## Principle

`feature_lane` is broad context. `hypothesis_unit` is the actual idea being
tested.

A `hypothesis_unit` may contain multiple columns or transforms only when they
are semantically or mechanically linked and should be kept, dropped, or ablated
together. Unrelated bundles are `multi_change: true` and require ablation before
promotion.

## Structural Numeric

Raw numeric/count/area fields already enter broad numeric lanes:

- `num_lots`, `num_communes`, `num_sections`, `num_parcels`
- `land_area`, `built_area`
- `num_premises`, `num_houses`, `num_apartments`, `num_dependencies`,
  `num_commercial`
- `house_area`, `apartment_area`
- `future_sale`, `year`, `month`

Candidate units:

- `structural_numeric_baseline`: broad numeric sanity scope.
- `presence_flags`: deterministic indicators for important zero/missing-like
  structural fields.
- `log_skewed_numerics`: log/capped transforms for heavily skewed numeric
  fields.
- `linear_interaction_probe`: a bounded degree-2 interaction subset for linear
  families, seeded by train-only diagnostics and evaluated as one grouped unit
  rather than term-by-term cherry-picking.

## Room Layout

Room-count and room-area distribution fields are raw numeric features, but they
can also be tested as a coherent layout signal:

- apartment counts: `num_apt_1_room` through `num_apt_5plus_rooms`
- house counts: `num_house_1_room` through `num_house_5plus_rooms`
- apartment areas: `area_apt_1_room` through `area_apt_5plus_rooms`
- house areas: `area_house_1_room` through `area_house_5plus_rooms`

Candidate units:

- `room_layout_distribution`: all room-count and room-area distribution fields
  as one semantic group.
- `room_area_density_ratios`: average area per apartment/house room bucket,
  protected against zero denominators.
- `drop_sparse_room_layout`: remove sparse room-layout columns if they add noise
  to a stronger anchor.

## Property And Transaction Categories

Low-cardinality categorical features:

- `property_type`: 25 observed values.
- `transaction_type`: 6 observed values.

Candidate units:

- `property_transaction_categories`: `property_type` and `transaction_type`
  together when the model can handle both safely.
- `property_type_category`: property type only.
- `transaction_type_category`: transaction type only.

Fit encoders inside CV folds. For tree boosters with native categorical support,
record category handling in `params_summary`.

## Geography

Geographic and cadastral fields:

- `commune_codes`: about 196 observed values.
- `cadastral_sections`: about 846 observed values.
- `dept_code`, `dept_name`, `region_code`, `region_name`: constant in the
  current training set, so they are not useful decision features.

Candidate units:

- `commune_first_category`: first commune code as a categorical feature.
- `cadastral_first_category`: first cadastral section as a categorical feature.
- `geo_granularity`: replace or compare commune-only, section-only, and
  commune+section encodings.
- `commune_frequency`: fold-safe count/frequency signal from training folds.
- `commune_target_encoding`: fold-safe smoothed target statistics only.

Never derive geography choices from `dataset/test.json`. Target-derived geo
statistics must be learned inside each CV fold with a fallback for unseen groups.

## Date And Time

Date fields:

- `transaction_date`: raw date string with many unique values.
- `year`, `month`: numeric coarse date parts already included in numeric lanes.

Candidate units:

- `date_ordinal`: days since a fixed training-independent epoch.
- `month_cyclical`: sine/cosine month encoding.
- `year_trend`: centered year or transaction age style trend feature.

Do not use future information or test-set date distribution to choose date
transforms.

## Derived Ratios

Domain-derived ratios should be added in coherent groups, not scattered one
column at a time:

- `area_density_ratios`: built area per premise, land per lot, commercial share,
  apartment share, house share.
- `room_area_density_ratios`: average areas per apartment/house room group.
- `parcel_density_ratios`: parcel/section/commune count ratios when denominators
  are stable.

Protect all divisions with deterministic safeguards. If a ratio group is weak
but cheap, it can stay only when reflection labels it a simplicity/signal tie;
otherwise discard or ablate it.

## Identifiers To Avoid

High-cardinality raw identifiers:

- `parcel_ids`: about 18k observed values.
- `transferred_parcel_ids`: about 17k observed values.

Do not use these raw strings as categorical features in normal smoke/deepen
runs. Only use derived, bounded signals such as counts, prefixes, or stable
geographic components when there is a written hypothesis and leakage check.

## Planner Checklist

Before a feature/preprocessing work item is created:

- name exactly one `hypothesis_unit`;
- set `change_kind` to `feature` or `preprocessing`;
- set `feature_group` to one of structural_numeric, room_layout,
  property_transaction, geography, date_time, derived_ratios, or id_derived;
- state the anchor recipe or run if this is not a first smoke run;
- keep unrelated bundles out of the work item unless `multi_change: true` is
  intentional and ablation is planned.
