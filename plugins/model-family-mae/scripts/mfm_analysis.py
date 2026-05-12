"""Train-only advisory feature diagnostics for the model-family MAE plugin."""

from __future__ import annotations

import json
import math
from pathlib import Path
from typing import Any


TARGET_KEY = "property_value"
SUPPORTED_METHODS = {"corr-lite", "poly-prune-lite", "hybrid"}
LINEAR_FAMILIES = {"linear", "ridge", "linear_robust", "lasso", "elasticnet", "huber"}
AREA_COUNT_FEATURES = {
    "built_area",
    "house_area",
    "apartment_area",
    "land_area",
    "num_lots",
    "num_premises",
    "num_houses",
    "num_apartments",
    "num_commercial",
    "num_dependencies",
}


def analyze_features(
    root: Path,
    family: str | None = None,
    method: str = "hybrid",
    top_pairs: int = 12,
    top_target: int = 8,
    min_abs_corr: float = 0.85,
    poly_base_feature_limit: int = 6,
    poly_min_features: int = 3,
    poly_degree: int = 2,
    poly_interaction_only: bool = False,
) -> dict[str, Any]:
    if method not in SUPPORTED_METHODS:
        raise SystemExit(f"Unsupported analysis method: {method}")
    if top_pairs < 1 or top_target < 1:
        raise SystemExit("top_pairs and top_target must be positive integers")
    if not 0.0 <= min_abs_corr <= 1.0:
        raise SystemExit("min_abs_corr must be between 0.0 and 1.0")
    if poly_base_feature_limit < 2:
        raise SystemExit("poly_base_feature_limit must be at least 2")
    if poly_min_features < 1:
        raise SystemExit("poly_min_features must be at least 1")
    if poly_degree < 2:
        raise SystemExit("poly_degree must be at least 2")

    dataset_path = root / "dataset" / "train.json"
    if not dataset_path.exists():
        raise SystemExit(f"Training dataset not found: {dataset_path}")

    records = json.loads(dataset_path.read_text(encoding="utf-8"))
    if not records:
        raise SystemExit("Training dataset is empty")

    feature_keys = numeric_feature_keys(records[0])
    if not feature_keys:
        raise SystemExit("No numeric training features found for corr-lite analysis")

    stats = correlation_stats(records, feature_keys)
    pair_rows = pair_correlations(feature_keys, stats["pair_sums"], stats["rows_used"], stats["col_sums"], stats["col_sumsq"])
    target_rows = target_correlations(
        feature_keys,
        stats["rows_used"],
        stats["col_sums"],
        stats["col_sumsq"],
        stats["target_sum"],
        stats["target_sumsq"],
        stats["target_cross"],
    )
    redundancy = redundancy_groups(pair_rows, min_abs_corr)

    pair_rows.sort(key=lambda item: (item["abs_correlation"], item["left"], item["right"]), reverse=True)
    target_rows.sort(key=lambda item: (item["abs_correlation"], item["feature"]), reverse=True)

    suggestions = build_suggestions(family, redundancy, target_rows)
    notes = [
        "Train-only advisory diagnostic. Do not use this output as a promotion gate.",
        "Correlation is most actionable for numeric redundancy and linear-family collinearity, not as a substitute for CV MAE.",
        "Any feature selector or learned pruning rule inspired by this report must still be fit inside each CV fold.",
    ]
    payload = {
        "analysis": "feature_diagnostic",
        "diagnostic_only": True,
        "family": family,
        "method": method,
        "dataset": "dataset/train.json",
        "rows_total": len(records),
        "rows_used": stats["rows_used"],
        "skipped_rows": stats["skipped_rows"],
        "numeric_feature_count": len(feature_keys),
        "numeric_features": feature_keys,
        "high_correlation_pairs": pair_rows[:top_pairs],
        "top_target_correlations": target_rows[:top_target],
        "redundancy_groups": redundancy,
        "suggested_work_items": suggestions,
    }
    if method in {"poly-prune-lite", "hybrid"}:
        poly_section = build_poly_prune_section(
            records,
            family,
            target_rows,
            records[0],
            base_feature_limit=poly_base_feature_limit,
            min_poly_features=poly_min_features,
            poly_degree=poly_degree,
            interaction_only=poly_interaction_only,
        )
        payload["poly_prune_lite"] = poly_section
        payload["suggested_work_items"] = merge_suggestions(payload["suggested_work_items"], poly_section.get("suggested_work_items", []))
        notes.extend(poly_section.get("top_level_notes", []))
    if method == "poly-prune-lite":
        notes.append("corr-lite target correlations are still used to bound the candidate numeric anchor set before polynomial pruning.")
    payload["notes"] = dedupe_text(notes)
    return payload


def numeric_feature_keys(sample: dict[str, Any]) -> list[str]:
    keys = []
    for key, value in sample.items():
        if key == TARGET_KEY:
            continue
        if isinstance(value, (int, float, bool)):
            keys.append(key)
    return keys


def correlation_stats(records: list[dict[str, Any]], feature_keys: list[str]) -> dict[str, Any]:
    feature_count = len(feature_keys)
    pair_indices = [(left, right) for left in range(feature_count - 1) for right in range(left + 1, feature_count)]
    col_sums = [0.0] * feature_count
    col_sumsq = [0.0] * feature_count
    target_cross = [0.0] * feature_count
    pair_sums = [0.0] * len(pair_indices)
    rows_used = 0
    skipped_rows = 0
    target_sum = 0.0
    target_sumsq = 0.0

    for record in records:
        target = coerce_numeric(record.get(TARGET_KEY))
        if target is None:
            skipped_rows += 1
            continue

        values = []
        valid = True
        for key in feature_keys:
            value = coerce_numeric(record.get(key))
            if value is None:
                valid = False
                break
            values.append(value)
        if not valid:
            skipped_rows += 1
            continue

        rows_used += 1
        target_sum += target
        target_sumsq += target * target

        for idx, value in enumerate(values):
            col_sums[idx] += value
            col_sumsq[idx] += value * value
            target_cross[idx] += value * target

        pair_idx = 0
        for left in range(feature_count - 1):
            left_value = values[left]
            for right in range(left + 1, feature_count):
                pair_sums[pair_idx] += left_value * values[right]
                pair_idx += 1

    if rows_used < 3:
        raise SystemExit("corr-lite requires at least three complete training rows")
    return {
        "rows_used": rows_used,
        "skipped_rows": skipped_rows,
        "col_sums": col_sums,
        "col_sumsq": col_sumsq,
        "target_sum": target_sum,
        "target_sumsq": target_sumsq,
        "target_cross": target_cross,
        "pair_sums": pair_sums,
    }


def coerce_numeric(value: Any) -> float | None:
    if value is None or isinstance(value, str):
        return None
    try:
        number = float(value)
    except (TypeError, ValueError):
        return None
    if math.isnan(number) or math.isinf(number):
        return None
    return number


def target_correlations(
    feature_keys: list[str],
    rows_used: int,
    col_sums: list[float],
    col_sumsq: list[float],
    target_sum: float,
    target_sumsq: float,
    target_cross: list[float],
) -> list[dict[str, Any]]:
    rows = []
    for idx, feature in enumerate(feature_keys):
        correlation = pearson_from_sums(
            rows_used,
            col_sums[idx],
            target_sum,
            col_sumsq[idx],
            target_sumsq,
            target_cross[idx],
        )
        if correlation is None:
            continue
        rows.append(
            {
                "feature": feature,
                "correlation": round(correlation, 6),
                "abs_correlation": round(abs(correlation), 6),
            }
        )
    return rows


def pair_correlations(
    feature_keys: list[str],
    pair_sums: list[float],
    rows_used: int,
    col_sums: list[float],
    col_sumsq: list[float],
) -> list[dict[str, Any]]:
    rows = []
    pair_idx = 0
    for left in range(len(feature_keys) - 1):
        for right in range(left + 1, len(feature_keys)):
            correlation = pearson_from_sums(
                rows_used,
                col_sums[left],
                col_sums[right],
                col_sumsq[left],
                col_sumsq[right],
                pair_sums[pair_idx],
            )
            pair_idx += 1
            if correlation is None:
                continue
            rows.append(
                {
                    "left": feature_keys[left],
                    "right": feature_keys[right],
                    "correlation": round(correlation, 6),
                    "abs_correlation": round(abs(correlation), 6),
                }
            )
    return rows


def pearson_from_sums(
    count: int,
    sum_x: float,
    sum_y: float,
    sum_x2: float,
    sum_y2: float,
    sum_xy: float,
) -> float | None:
    numerator = count * sum_xy - sum_x * sum_y
    left = count * sum_x2 - sum_x * sum_x
    right = count * sum_y2 - sum_y * sum_y
    if left <= 0 or right <= 0:
        return None
    return numerator / math.sqrt(left * right)


def redundancy_groups(pair_rows: list[dict[str, Any]], min_abs_corr: float) -> list[dict[str, Any]]:
    adjacency: dict[str, set[str]] = {}
    for row in pair_rows:
        if row["abs_correlation"] < min_abs_corr:
            continue
        adjacency.setdefault(row["left"], set()).add(row["right"])
        adjacency.setdefault(row["right"], set()).add(row["left"])

    visited: set[str] = set()
    groups = []
    for feature in sorted(adjacency):
        if feature in visited:
            continue
        stack = [feature]
        component = []
        max_corr = 0.0
        while stack:
            current = stack.pop()
            if current in visited:
                continue
            visited.add(current)
            component.append(current)
            for neighbor in adjacency.get(current, set()):
                max_corr = max(max_corr, edge_abs_corr(pair_rows, current, neighbor))
                if neighbor not in visited:
                    stack.append(neighbor)
        if len(component) > 1:
            groups.append(
                {
                    "features": sorted(component),
                    "size": len(component),
                    "max_abs_correlation": round(max_corr, 6),
                }
            )
    groups.sort(key=lambda item: (item["size"], item["max_abs_correlation"], item["features"]), reverse=True)
    return groups


def edge_abs_corr(pair_rows: list[dict[str, Any]], left: str, right: str) -> float:
    want = {left, right}
    for row in pair_rows:
        if {row["left"], row["right"]} == want:
            return float(row["abs_correlation"])
    return 0.0


def build_suggestions(
    family: str | None,
    redundancy: list[dict[str, Any]],
    target_rows: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    suggestions = []
    top_target_features = [row["feature"] for row in target_rows[:8]]

    room_group, room_features = first_group_with_matches(redundancy, lambda feature: is_room_layout_feature(feature), min_matches=3)
    if room_group:
        suggestions.append(
            suggestion_row(
                "feature",
                "room_layout_distribution",
                "room_layout",
                "all_numeric",
                room_layout_reason(family, room_features, room_group["max_abs_correlation"]),
            )
        )
        if is_linear_family(family):
            suggestions.append(
                suggestion_row(
                    "feature",
                    "drop_sparse_room_layout",
                    "room_layout",
                    "all_numeric",
                    "Room-layout columns form a tight correlated block; for linear families, compare the full block against a pared-down sparse-tail version rather than keeping every room bucket by default.",
                )
            )

    if sum(feature in AREA_COUNT_FEATURES for feature in top_target_features) >= 2:
        suggestions.append(
            suggestion_row(
                "feature",
                "area_density_ratios",
                "derived_ratios",
                "derived_ratios",
                "Top target-marginal signal is concentrated in raw area/count fields, so deterministic density/share ratios are a natural next single-knob feature group to test.",
            )
        )
        suggestions.append(
            suggestion_row(
                "feature",
                "structural_numeric_baseline",
                "structural_numeric",
                "all_numeric",
                "Raw structural numerics appear to carry the strongest marginal signal; keep them as an explicit anchor group when comparing any pruning or ratio experiment.",
            )
        )

    if not suggestions:
        suggestions.append(
            suggestion_row(
                "diagnostic",
                "no_clear_corr_candidate",
                "structural_numeric",
                "all_numeric",
                "No numeric redundancy pattern crossed the advisory threshold cleanly. Use CV evidence, residuals, or runtime pressure to choose the next hypothesis unit.",
            )
        )

    return dedupe_suggestions(suggestions)


def build_poly_prune_section(
    records: list[dict[str, Any]],
    family: str | None,
    target_rows: list[dict[str, Any]],
    sample_record: dict[str, Any],
    base_feature_limit: int,
    min_poly_features: int,
    poly_degree: int,
    interaction_only: bool,
) -> dict[str, Any]:
    try:
        import numpy as np
        from sklearn.linear_model import LinearRegression
        from sklearn.metrics import mean_absolute_error
        from sklearn.model_selection import KFold
        from sklearn.preprocessing import PolynomialFeatures, StandardScaler
    except ModuleNotFoundError as exc:
        return {
            "status": "unavailable",
            "reason": f"Optional dependency unavailable: {exc.name}",
            "top_level_notes": [
                "The baked-in polynomial pruning diagnostic is available only when sklearn and its numeric stack are installed.",
            ],
            "notes": [
                "The correlation diagnostic still ran normally.",
                "If you want the polynomial pruning path, run the plugin in the same environment that has the evaluator dependencies installed.",
            ],
            "suggested_work_items": [],
        }

    base_features = polynomial_base_features(sample_record, target_rows, base_feature_limit)
    rows, targets, skipped_rows = matrix_from_records(records, base_features)
    if len(rows) < 3:
        return {
            "status": "unavailable",
            "reason": "Not enough complete rows for polynomial pruning",
            "top_level_notes": [],
            "notes": [
                "The polynomial pruning diagnostic needs at least three complete train rows for its bounded base feature set.",
            ],
            "suggested_work_items": [],
        }

    row_count = len(rows)
    n_splits = 5 if row_count >= 5 else row_count
    if n_splits < 3:
        return {
            "status": "unavailable",
            "reason": "Need at least three complete rows for bounded CV pruning",
            "top_level_notes": [],
            "notes": [
                "Fallback to fewer than three CV folds is not supported for the polynomial pruning diagnostic.",
            ],
            "suggested_work_items": [],
        }

    x_rows = np.asarray(rows, dtype=float)
    y_rows = np.asarray(targets, dtype=float)
    poly = PolynomialFeatures(degree=poly_degree, include_bias=False, interaction_only=interaction_only)
    x_poly = poly.fit_transform(x_rows)
    term_names = list(poly.get_feature_names_out(base_features))
    minimum_terms = max(1, min(min_poly_features, x_poly.shape[1]))
    selected = list(range(x_poly.shape[1]))
    best_selected = selected[:]
    best_cv_mae = float("inf")
    best_cv_std = float("inf")
    path = []

    while len(selected) >= minimum_terms:
        cv_mae, cv_std = cv_mae_for_selected_terms(
            x_poly,
            y_rows,
            selected,
            KFold,
            StandardScaler,
            LinearRegression,
            mean_absolute_error,
            n_splits=n_splits,
        )
        next_removed_term = None
        if len(selected) > minimum_terms:
            next_removed_idx = least_important_term(x_poly, y_rows, selected, StandardScaler, LinearRegression)
            next_removed_term = term_names[next_removed_idx]
        path.append(
            {
                "features_left": len(selected),
                "cv_mae": round(cv_mae, 6),
                "cv_mae_std": round(cv_std, 6),
                "next_removed_term": next_removed_term,
            }
        )
        if cv_mae < best_cv_mae:
            best_cv_mae = cv_mae
            best_cv_std = cv_std
            best_selected = selected[:]
        if next_removed_term is None:
            break
        selected.remove(next_removed_idx)

    best_terms = [term_names[idx] for idx in best_selected]
    interaction_terms = [term for term in best_terms if " " in term]
    squared_terms = [term for term in best_terms if "^2" in term]
    suggestions = build_poly_suggestions(family, base_features, interaction_terms, interaction_only)
    top_level_notes = []
    if not is_linear_family(family):
        top_level_notes.append("The baked-in polynomial pruning diagnostic is most relevant for linear families; treat it as low-priority context for tree ensembles.")
    return {
        "status": "available",
        "family_relevance": "high" if is_linear_family(family) else "low",
        "rows_used": row_count,
        "skipped_rows": skipped_rows,
        "n_splits": n_splits,
        "metric": "cv_mae",
        "degree": poly_degree,
        "interaction_only": interaction_only,
        "base_features": base_features,
        "poly_feature_count": int(x_poly.shape[1]),
        "best_subset_size": len(best_selected),
        "best_cv_mae": round(best_cv_mae, 6),
        "best_cv_mae_std": round(best_cv_std, 6),
        "best_terms": best_terms,
        "interaction_terms": interaction_terms,
        "squared_terms": squared_terms,
        "path": path,
        "top_level_notes": top_level_notes,
        "notes": [
            "This is a train-only advisory path. It replaces holdout MSE with bounded KFold CV MAE on the training set.",
            "Each pruning step ranks polynomial terms by standardized absolute coefficient magnitude on the full training matrix, then uses CV MAE to choose the best subset size.",
            "If you turn any retained term set into a real experiment, rebuild it inside a fold-safe pipeline for canonical evaluation.",
        ],
        "suggested_work_items": suggestions,
    }


def polynomial_base_features(
    sample_record: dict[str, Any],
    target_rows: list[dict[str, Any]],
    limit: int,
) -> list[str]:
    ranked = [row["feature"] for row in target_rows if not isinstance(sample_record.get(row["feature"]), bool)]
    if len(ranked) < limit:
        ranked = [row["feature"] for row in target_rows]
    return ranked[:limit]


def matrix_from_records(records: list[dict[str, Any]], feature_names: list[str]) -> tuple[list[list[float]], list[float], int]:
    rows = []
    targets = []
    skipped_rows = 0
    for record in records:
        target = coerce_numeric(record.get(TARGET_KEY))
        if target is None:
            skipped_rows += 1
            continue
        values = []
        valid = True
        for feature in feature_names:
            value = coerce_numeric(record.get(feature))
            if value is None:
                valid = False
                break
            values.append(value)
        if not valid:
            skipped_rows += 1
            continue
        rows.append(values)
        targets.append(target)
    return rows, targets, skipped_rows


def cv_mae_for_selected_terms(
    x_poly,
    y_rows,
    selected: list[int],
    KFold,
    StandardScaler,
    LinearRegression,
    mean_absolute_error,
    n_splits: int,
) -> tuple[float, float]:
    splitter = KFold(n_splits=n_splits, shuffle=True, random_state=42)
    fold_maes = []
    selected_array = x_poly[:, selected]
    for train_index, valid_index in splitter.split(selected_array):
        scaler = StandardScaler()
        x_train = scaler.fit_transform(selected_array[train_index])
        x_valid = scaler.transform(selected_array[valid_index])
        model = LinearRegression()
        model.fit(x_train, y_rows[train_index])
        predictions = model.predict(x_valid)
        fold_maes.append(float(mean_absolute_error(y_rows[valid_index], predictions)))
    return mean_and_std(fold_maes)


def least_important_term(
    x_poly,
    y_rows,
    selected: list[int],
    StandardScaler,
    LinearRegression,
) -> int:
    scaler = StandardScaler()
    x_scaled = scaler.fit_transform(x_poly[:, selected])
    model = LinearRegression()
    model.fit(x_scaled, y_rows)
    magnitudes = [abs(float(value)) for value in model.coef_]
    least_position = min(range(len(magnitudes)), key=lambda idx: magnitudes[idx])
    return selected[least_position]


def mean_and_std(values: list[float]) -> tuple[float, float]:
    mean = sum(values) / len(values)
    variance = sum((value - mean) ** 2 for value in values) / len(values)
    return mean, math.sqrt(variance)


def build_poly_suggestions(
    family: str | None,
    base_features: list[str],
    interaction_terms: list[str],
    interaction_only: bool,
) -> list[dict[str, Any]]:
    if not is_linear_family(family):
        return []
    if not interaction_terms:
        return []
    interaction_style = "interaction-only" if interaction_only else "degree-2 polynomial"
    return [
        suggestion_row(
            "feature",
            "linear_interaction_probe",
            "structural_numeric",
            "linear_interactions",
            (
                f"A bounded train-only CV pruning pass kept {len(interaction_terms)} {interaction_style} terms from base numerics "
                f"{', '.join(base_features)}. Test those interactions as one grouped linear-family hypothesis rather than keeping the full expansion."
            ),
        )
    ]


def merge_suggestions(primary: list[dict[str, Any]], secondary: list[dict[str, Any]]) -> list[dict[str, Any]]:
    return dedupe_suggestions(primary + secondary)


def dedupe_suggestions(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    deduped = []
    seen = set()
    for row in rows:
        key = (row["change_kind"], row["hypothesis_unit"])
        if key in seen:
            continue
        seen.add(key)
        deduped.append(row)
    return deduped


def dedupe_text(lines: list[str]) -> list[str]:
    deduped = []
    seen = set()
    for line in lines:
        if line in seen:
            continue
        seen.add(line)
        deduped.append(line)
    return deduped


def first_group_with_matches(
    redundancy: list[dict[str, Any]],
    predicate,
    min_matches: int,
) -> tuple[dict[str, Any] | None, list[str]]:
    for group in redundancy:
        matches = [feature for feature in group["features"] if predicate(feature)]
        if len(matches) >= min_matches:
            return group, matches
    return None, []


def is_room_layout_feature(feature: str) -> bool:
    return feature.startswith(("num_apt_", "num_house_", "area_apt_", "area_house_"))


def is_linear_family(family: str | None) -> bool:
    if not family:
        return False
    return family.lower() in LINEAR_FAMILIES


def room_layout_reason(family: str | None, features: list[str], max_abs_corr: float) -> str:
    if is_linear_family(family):
        return (
            f"Room-layout features form a highly correlated numeric block (max |r|={max_abs_corr:.3f}). "
            "That is a direct collinearity diagnostic for linear-style families, so test the whole semantic unit rather than promoting single columns."
        )
    return (
        f"Room-layout features form a tight semantic block (max |r|={max_abs_corr:.3f}). "
        "Treat them as one attributable hypothesis unit, then let CV decide whether the full block or a reduced variant is worth keeping."
    )


def suggestion_row(
    change_kind: str,
    hypothesis_unit: str,
    feature_group: str,
    feature_lane: str,
    reason: str,
) -> dict[str, Any]:
    return {
        "change_kind": change_kind,
        "hypothesis_unit": hypothesis_unit,
        "feature_group": feature_group,
        "suggested_feature_lane": feature_lane,
        "reason": reason,
        "plan_hint": (
            f'--feature-lane "{feature_lane}" --change-kind "{change_kind}" '
            f'--hypothesis-unit "{hypothesis_unit}" --feature-group "{feature_group}"'
        ),
    }
