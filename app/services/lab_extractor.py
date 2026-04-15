import math
import re
from dataclasses import dataclass


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
    "vitamin_d_25_oh": ["vitamin d", "25-oh vitamin d", "25 hydroxy vitamin d", "25-ohd"],
    "fasting_glucose": ["fasting glucose", "fasting blood sugar", "fbs", "glucose fasting"],
    "hba1c": ["hba1c", "glycated hemoglobin", "glycosylated hemoglobin"],
    "total_cholesterol": ["total cholesterol", "cholesterol total"],
    "ldl": ["ldl", "ldl cholesterol"],
    "hdl": ["hdl", "hdl cholesterol"],
    "triglycerides": ["triglycerides", "tg"],
    "creatinine": ["creatinine", "serum creatinine"],
    "alt": ["alt", "sgpt", "alanine aminotransferase"],
    "ast": ["ast", "sgot", "aspartate aminotransferase"],
    "tsh": ["tsh", "thyroid stimulating hormone"],
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


def _norm(s: str) -> str:
    return re.sub(r"\s+", " ", s.strip().lower())


def _parse_float(token: str) -> float | None:
    token = token.replace(",", "").strip()
    try:
        return float(token)
    except ValueError:
        return None


def _extract_reference_range(line: str) -> tuple[float | None, float | None, str]:
    patterns = [
        r"(?P<low>-?\d+(?:\.\d+)?)\s*(?:-|–|to)\s*(?P<high>-?\d+(?:\.\d+)?)",
        r"ref(?:erence)?[:\s]+(?P<low>-?\d+(?:\.\d+)?)\s*(?:-|–|to)\s*(?P<high>-?\d+(?:\.\d+)?)",
    ]
    for pattern in patterns:
        match = re.search(pattern, line, flags=re.IGNORECASE)
        if match:
            low = _parse_float(match.group("low"))
            high = _parse_float(match.group("high"))
            return low, high, f"{match.group('low')}-{match.group('high')}"
    return None, None, ""


def _extract_value_and_unit(line: str) -> tuple[float | None, str]:
    match = re.search(r"(-?\d+(?:\.\d+)?)\s*([%A-Za-zµμ/\^0-9.-]*)", line)
    if not match:
        return None, ""
    value = _parse_float(match.group(1))
    unit = (match.group(2) or "").strip()
    return value, unit


def _status_from_range(value: float, low: float | None, high: float | None) -> str:
    if low is None and high is None:
        return "unknown"
    if low is not None and value < low:
        return "low"
    if high is not None and value > high:
        return "high"
    return "normal"


def extract_lab_markers(raw_text: str) -> tuple[list[ParsedMarker], list[str], float]:
    parsed: list[ParsedMarker] = []
    warnings: list[str] = []

    lines = [line.strip() for line in raw_text.splitlines() if line.strip()]
    consumed: set[str] = set()

    for line in lines:
        norm_line = _norm(line)
        for marker_key, aliases in ALIAS_MAP.items():
            if marker_key in consumed:
                continue

            if not any(alias in norm_line for alias in aliases):
                continue

            value, unit = _extract_value_and_unit(line)
            if value is None or math.isnan(value):
                warnings.append(f"Could not parse value for line: {line[:80]}")
                continue

            low, high, raw_range = _extract_reference_range(line)
            status = _status_from_range(value, low, high)
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
            break

    confidence = round(len(parsed) / max(8, len(ALIAS_MAP)), 2)
    if not parsed:
        warnings.append("No supported lab markers were detected. Review parser rules for this report format.")

    return parsed, warnings, confidence
