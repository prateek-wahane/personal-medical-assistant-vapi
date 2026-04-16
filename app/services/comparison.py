from __future__ import annotations

from collections import defaultdict
from typing import Iterable

from app.models import LabResult

LOWER_IS_BETTER = {"fasting_glucose", "hba1c", "ldl", "triglycerides", "creatinine", "alt", "ast"}
HIGHER_IS_BETTER = {"hemoglobin", "ferritin", "vitamin_b12", "folate", "vitamin_d_25_oh", "hdl"}


def _severity(value: float, low: float | None, high: float | None) -> float:
    if low is not None and value < low:
        return round((low - value) / max(abs(low), 1.0), 4)
    if high is not None and value > high:
        return round((value - high) / max(abs(high), 1.0), 4)
    return 0.0


def _to_map(results: Iterable[LabResult]) -> dict[str, LabResult]:
    return {result.marker_key: result for result in results}


def _normalize_unit(unit: str) -> str:
    return "".join(unit.lower().split())


def compare_lab_results(old_results: Iterable[LabResult], new_results: Iterable[LabResult]) -> list[dict]:
    old_map = _to_map(old_results)
    new_map = _to_map(new_results)

    all_keys = sorted(set(old_map) | set(new_map))
    entries: list[dict] = []

    for key in all_keys:
        old = old_map.get(key)
        new = new_map.get(key)

        if old and new:
            if old.unit and new.unit and _normalize_unit(old.unit) != _normalize_unit(new.unit):
                entries.append(
                    {
                        "marker_key": key,
                        "marker_label": new.marker_label,
                        "previous_value": old.value,
                        "current_value": new.value,
                        "unit": f"{old.unit} -> {new.unit}",
                        "delta": None,
                        "previous_status": old.status,
                        "current_status": new.status,
                        "trend": "not-comparable-different-unit",
                        "interpretation": (
                            f"{new.marker_label} used different units across reports "
                            f"({old.unit} vs {new.unit}), so direct comparison is unsafe."
                        ),
                    }
                )
                continue

            delta = round(new.value - old.value, 4)
            old_sev = _severity(old.value, old.reference_low, old.reference_high)
            new_sev = _severity(new.value, new.reference_low, new.reference_high)

            if new_sev < old_sev:
                trend = "improved"
                interpretation = f"{new.marker_label} moved closer to the reference range."
            elif new_sev > old_sev:
                trend = "worsened"
                interpretation = f"{new.marker_label} moved farther away from the reference range."
            else:
                if key in LOWER_IS_BETTER:
                    trend = "improved" if delta < 0 else "worsened" if delta > 0 else "stable"
                elif key in HIGHER_IS_BETTER:
                    trend = "improved" if delta > 0 else "worsened" if delta < 0 else "stable"
                else:
                    trend = "stable" if abs(delta) < 0.0001 else "changed"
                interpretation = f"{new.marker_label} changed by {delta:g} {new.unit}".strip()

            if old.raw_range and new.raw_range and old.raw_range != new.raw_range:
                interpretation += f" Reference range changed from {old.raw_range} to {new.raw_range}."

            entries.append(
                {
                    "marker_key": key,
                    "marker_label": new.marker_label,
                    "previous_value": old.value,
                    "current_value": new.value,
                    "unit": new.unit or old.unit,
                    "delta": delta,
                    "previous_status": old.status,
                    "current_status": new.status,
                    "trend": trend,
                    "interpretation": interpretation,
                }
            )
        elif old and not new:
            entries.append(
                {
                    "marker_key": key,
                    "marker_label": old.marker_label,
                    "previous_value": old.value,
                    "current_value": None,
                    "unit": old.unit,
                    "delta": None,
                    "previous_status": old.status,
                    "current_status": None,
                    "trend": "missing-in-new-report",
                    "interpretation": f"{old.marker_label} was present in the older report but not found in the new report.",
                }
            )
        elif new and not old:
            entries.append(
                {
                    "marker_key": key,
                    "marker_label": new.marker_label,
                    "previous_value": None,
                    "current_value": new.value,
                    "unit": new.unit,
                    "delta": None,
                    "previous_status": None,
                    "current_status": new.status,
                    "trend": "new-marker",
                    "interpretation": f"{new.marker_label} was not found in the older report.",
                }
            )

    return entries


def summarize_comparison(entries: list[dict]) -> str:
    buckets: dict[str, list[str]] = defaultdict(list)
    for entry in entries:
        buckets[entry["trend"]].append(entry["marker_label"])

    parts: list[str] = []
    for key in [
        "improved",
        "worsened",
        "stable",
        "changed",
        "not-comparable-different-unit",
        "new-marker",
        "missing-in-new-report",
    ]:
        if buckets.get(key):
            labels = ", ".join(sorted(buckets[key]))
            parts.append(f"{key.replace('-', ' ')}: {labels}")
    return " | ".join(parts) if parts else "No comparable markers were found."
