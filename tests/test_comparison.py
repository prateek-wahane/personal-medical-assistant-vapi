from app.services.comparison import compare_lab_results, summarize_comparison


class DummyResult:
    def __init__(self, marker_key, marker_label, value, unit, low, high, status, raw_range=""):
        self.marker_key = marker_key
        self.marker_label = marker_label
        self.value = value
        self.unit = unit
        self.reference_low = low
        self.reference_high = high
        self.status = status
        self.raw_range = raw_range


def test_compare_improves_when_low_marker_moves_toward_range():
    old = [DummyResult("hemoglobin", "Hemoglobin", 11.0, "g/dL", 13.0, 17.0, "low", "13-17")]
    new = [DummyResult("hemoglobin", "Hemoglobin", 12.4, "g/dL", 13.0, 17.0, "low", "13-17")]

    entries = compare_lab_results(old, new)
    assert entries[0]["trend"] == "improved"
    assert "closer" in entries[0]["interpretation"]


def test_summary_contains_worsened_bucket():
    entries = [{"trend": "worsened", "marker_label": "LDL"}]
    assert "worsened: LDL" == summarize_comparison(entries)


def test_unit_mismatch_is_not_compared_directly():
    old = [DummyResult("glucose", "Glucose", 90.0, "mg/dL", 70.0, 100.0, "normal")]
    new = [DummyResult("glucose", "Glucose", 5.0, "mmol/L", 4.0, 6.0, "normal")]
    entries = compare_lab_results(old, new)
    assert entries[0]["trend"] == "not-comparable-different-unit"
