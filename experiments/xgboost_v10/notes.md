# xgboost_v10 Notes

## Premise

Hypothesis-driven feature exploration to break the v6/v7 ~47200 plateau.
Tested axis: `transferred_parcel_ids` set arithmetic (signal isolation +
incremental lift on the v6 anchor).

## Status

Smoke triad complete (Lane 3 timed out at n_est=2000; retried as deepen
iter2 at n_est=1000 for budget). Two deepen iters give a clean apples-to-
apples lift measurement.

## Result

| Iter | Recipe | cv_mae +/- std | Note |
|---|---|---|---|
| Smoke 1 | transfer-3 only | 90419.81 +/- 5300.75 | signal too thin alone |
| Smoke 2 | shrunk v6 (n=2000) no transfer | 48441.69 +/- 4771.50 | family best (anchor) |
| Smoke 3 | shrunk v6 (n=2000) + transfer | timeout | budget exceeded |
| Deepen 1 | shrunk v6 (n=1000) no transfer | 48772.08 +/- 4836.54 | runtime-safe baseline |
| Deepen 2 | shrunk v6 (n=1000) + transfer | 48589.88 +/- 4902.63 | **+transfer = -182 MAE** |

Lift measurement (deepen iter2 vs iter1): **-182 MAE**, pooled_std ~4870,
noise_band ~1217. |delta| << noise -> **tie within noise**.

## Verdict

Transfer-mode features (n_transferred, n_parcels_kept, transfer_overlap_ratio,
is_no_transfer) do **not** break the plateau. The 32% no_transfer subgroup
price differential is real but already captured indirectly by `num_parcels`
(equal to n_transferred for the 66% full_match rows) and other size/area
patterns the per-type submodels already exploit. transfer_overlap_ratio is
novel but too sparse (1.5% of rows have non-trivial overlap).

## Decision

**Park.** Axis A ruled out as a plateau-breaker. Best v10 result (smoke iter2
at 48441.69) does not beat the v6/v7 family-best confirms (~47200). No
seed=2026 confirm; no global champion update.

## Next Action

User-directed. Next-best brainstorm axis is **B (commune-time market
velocity)** -- adds a genuinely missing temporal dimension. Other candidates
remain C (robust commune statistics), D (multi-territoriality interaction),
E (commune x type Z-score).
