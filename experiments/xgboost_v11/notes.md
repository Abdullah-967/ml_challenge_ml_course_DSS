# xgboost_v11 Notes

## Premise

Hypothesis-driven feature exploration to break the v6/v7 ~47200 plateau.
Tested axis B (commune-time market velocity) after v10 ruled out axis A
(transferred_parcel_ids).

## Status

Smoke triad complete. PARKED -- velocity features do not break the plateau.

## Result

| Iter | Recipe | cv_mae +/- std | Note |
|---|---|---|---|
| Smoke 1 | velocity-4 only | 91748.76 +/- 5632.44 | signal too thin alone |
| Smoke 2 | shrunk v6 (n=1000) no velocity | 48772.08 +/- 4836.54 | family best (anchor) |
| Smoke 3 | shrunk v6 (n=1000) + velocity | 49013.46 +/- 4862.86 | **+241 MAE** (tie, slight regression) |

Lift: **+241 MAE**, pooled_std ~4850, noise_band ~1212. Tie within noise but
in the wrong direction.

## Verdict

Velocity features (n_txns_prev_60d/180d, avg_built_area_prev_60d,
days_since_last_txn) do NOT break the plateau. The 76k active-vs-quiet
commune price differential we measured during inspection is real but
already absorbed by the v6 architecture (commune_first native categorical
+ per-type submodels). Adding redundant features only adds noise.

## Decision

**Park.** Axis B ruled out. Combined with v10's null on axis A, two
consecutive within-noise results suggest the v6 feature space is
thoroughly mined. The plateau is robust.
