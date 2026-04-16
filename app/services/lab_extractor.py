from __future__ import annotations

import math
import re
from dataclasses import dataclass
from typing import Iterable


@dataclass
class ParsedMarker:
    marker_key: str
    marker_label: str
    value: float
    unit: str
    reference_low: float | None
    reference_high: float | None
    raw_range: str
    status: str
    raw_line: str


ALIAS_MAP: dict[str, list[str]] = {
    "hemoglobin": ["hemoglobin", "haemoglobin", "hb"],
    "hematocrit": ["hematocrit", "haematocrit", "pcv", "hct"],
    "rbc": ["rbc count", "rbc", "red blood cell count"],
    "wbc": ["wbc count", "wbc", "total leucocyte count", "total leukocyte count"],
    "platelets": ["platelet count", "platelets", "platelet"],
    "mcv": ["mcv", "mean corpuscular volume"],
    "mch": ["mch", "mean corpuscular hemoglobin"],
    "mchc": ["mchc", "mean corpuscular hemoglobin concentration"],
    "ferritin": ["ferritin", "serum ferritin"],
    "serum_iron": ["serum iron", "iron"],
    "vitamin_b12": ["vitamin b12", "b12", "cobalamin"],
    "folate": ["folate", "folic acid"],
    "vitamin_d_25_oh": ["25-oh vitamin d", "25 hydroxy vitamin d", "25-ohd", "vitamin d"],
    "fasting_glucose": ["fasting glucose", "fasting blood sugar", "glucose fasting", "fbs"],
    "hba1c": ["hba1c", "glycated hemoglobin", "glycosylated hemoglobin"],
    "total_cholesterol": ["total cholesterol", "cholesterol total"],
    "ldl": ["ldl cholesterol", "ldl"],
    "hdl": ["hdl cholesterol", "hdl"],
    "triglycerides": ["triglycerides", "tg"],
    "creatinine": ["serum creatinine", "creatinine"],
    "alt": ["alanine aminotransferase", "sgpt", "alt"],
    "ast": ["aspartate aminotransferase", "sgot", "ast"],
    "tsh": ["thyroid stimulating hormone", "tsh"],
}

PREFERRED_LABELS = {
    "hemoglobin": "Hemoglobin",
    "hematocrit": "Hematocrit",
    "rbc": "RBC",
    "wbc": "WBC",
    "platelets": "Platelets",
    "mcv": "MCV",
    "mch": "MCH",
    "mchc": "MCHC",
    "ferritin": "Ferritin",
    "serum_iron": "Serum Iron",
    "vitamin_b12": "Vitamin B12",
    "folate": "Folate",
    "vitamin_d_25_oh": "Vitamin D",
    "fasting_glucose": "Fasting Glucose",
    "hba1c": "HbA1c",
    "total_cholesterol": "Total Cholesterol",
    "ldl": "LDL",
    "hdl": "HDL",
    "triglycerides": "Triglycerides",
    "creatinine": "Creatinine",
    "alt": "ALT",
    "ast": "AST",
    "tsh": "TSH",
}

RANGE_PATTERNS = [
    re.compile(r"(?P<low>-?\d+(?:\.\d+)?)\s*(?:-|–|to)\s*(?P<high>-?\d+(?:\.\d+)?)", re.IGNORECASE),
    re.compile(r"(?:ref(?:erence)?|range)?\s*(?:<|<=|upto|up to)\s*(?P<high>-?\d+(?:\.\d+)?)", re.IGNORECASE),
    re.compile(r"(?:ref(?:erence)?|range)?\s*(?:>|>=)\s*(?P<low>-?\d+(?:\.\d+)?)", re.IGNORECASE),
]
NUMBER_RE = re.compile(r"[-+]?\d+(?:\.\d+)?")


def _norm(s: str) -> str:
    return re.sub(r"\s+", " ", s.strip().lower())


def _parse_float(token: str) -> float | None:
    token = token.replace(",", "").strip()
    match = NUMBER_RE.search(token)
    if not match:
        return None
    try:
        return float(match.group(0))
    except ValueError:
        return None


def _find_best_match(norm_line: str, consumed: set[str]) -> tuple[str, str, tuple[int, int]] | None:
    candidates: list[tuple[int, int, str, str, tuple[int, int]]] = []
    for marker_key, aliases in ALIAS_MAP.items():
        if marker_key in consumed:
            continue
        for alias in aliases:
            pattern = re.compile(rf"(?<![a-z0-9]){re.escape(alias)}(?![a-z0-9])")
            match = pattern.search(norm_line)
            if match:
                span = match.span()
                candidates.append((span[0], -len(alias), marker_key, alias, span))
    if not candidates:
        return None
    _, _, marker_key, alias, span = sorted(candidates)[0]
    return marker_key, alias, span


def _extract_reference_range(text: str) -> tuple[float | None, float | None, str]:
    for pattern in RANGE_PATTERNS:
        match = pattern.search(text)
        if not match:
            continue
        low = _parse_float(match.groupdict().get("low") or "")
        high = _parse_float(match.groupdict().get("high") or "")
        raw = match.group(0).replace("reference", "").replace("ref", "").strip(" :-")
        return low, high, raw
    return None, None, ""


def _extract_status_flag(text: str) -> str | None:
    tokens = [token.upper() for token in re.findall(r"\b[A-Za-z]+\b", text)]
    if "LOW" in tokens or "L" in tokens:
        return "low"
    if "HIGH" in tokens or "H" in tokens:
        return "high"
    if "NORMAL" in tokens or "N" in tokens:
        return "normal"
    return None


def _extract_value_and_unit(text: str) -> tuple[float | None, str]:
    tokens = re.findall(r"[^\s]+", text)
    for index, token in enumerate(tokens):
        value = _parse_float(token)
        if value is None or math.isnan(value):
            continue

        unit_parts: list[str] = []
        for next_token in tokens[index + 1:]:
            upper = next_token.upper().strip()
            if NUMBER_RE.search(next_token):
                break
            if upper in {"L", "H", "LOW", "HIGH", "NORMAL", "REF", "REFERENCE", "RANGE"}:
                break
            unit_parts.append(next_token)
        unit = " ".join(unit_parts).strip("()[]")
        return value, unit
    return None, ""


def _status_from_range(value: float, low: float | None, high: float | None, explicit_flag: str | None) -> str:
    if low is None and high is None:
        return explicit_flag or "unknown"
    if low is not None and value < low:
        return "low"
    if high is not None and value > high:
        return "high"
    return explicit_flag or "normal"


def extract_lab_markers(raw_text: str) -> tuple[list[ParsedMarker], list[str], float]:
    parsed: list[ParsedMarker] = []
    warnings: list[str] = []

    lines = [line.strip() for line in raw_text.splitlines() if line.strip()]
    consumed: set[str] = set()

    for line in lines:
        norm_line = _norm(line)
        match_info = _find_best_match(norm_line, consumed)
        if not match_info:
            continue

        marker_key, _alias, span = match_info
        value_region = line[span[1]:].strip(" :-	")
        value, unit = _extract_value_and_unit(value_region)
        if value is None or math.isnan(value):
            warnings.append(f"Could not parse value for line: {line[:120]}")
            continue

        low, high, raw_range = _extract_reference_range(value_region)
        explicit_flag = _extract_status_flag(value_region)
        status = _status_from_range(value, low, high, explicit_flag)

        parsed.append(
            ParsedMarker(
                marker_key=marker_key,
                marker_label=PREFERRED_LABELS.get(marker_key, marker_key.replace("_", " ").title()),
                value=value,
                unit=unit,
                reference_low=low,
                reference_high=high,
                raw_range=raw_range,
                status=status,
                raw_line=line,
            )
        )
        consumed.add(marker_key)

    confidence = round(len(parsed) / max(8, len(ALIAS_MAP)), 2)
    if not parsed:
        warnings.append("No supported lab markers were detected. Review parser rules for this report format.")

    return parsed, warnings, confidence
