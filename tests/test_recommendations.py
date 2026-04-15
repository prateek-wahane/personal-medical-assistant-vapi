from app.services.recommendations import recommendation_for_marker


class DummyLab:
    def __init__(self, marker_key, marker_label, value, unit, status):
        self.marker_key = marker_key
        self.marker_label = marker_label
        self.value = value
        self.unit = unit
        self.status = status


def test_low_hemoglobin_includes_iron_guidance():
    hb = DummyLab("hemoglobin", "Hemoglobin", 11.2, "g/dL", "low")
    payload = recommendation_for_marker(hb, [])
    assert "Iron" in " ".join(payload["foods"])
    assert "safety_note" in payload


def test_high_hba1c_mentions_glucose_control():
    a1c = DummyLab("hba1c", "HbA1c", 6.2, "%", "high")
    payload = recommendation_for_marker(a1c, [])
    assert "glucose control" in payload["why_it_matters"].lower()
