from app.services.lab_extractor import extract_lab_markers


def test_parser_uses_b12_result_not_label_number():
    markers, warnings, _ = extract_lab_markers("Vitamin B12 260 pg/mL 200 - 900")
    assert not warnings
    assert markers[0].marker_key == "vitamin_b12"
    assert markers[0].value == 260


def test_parser_handles_25_oh_vitamin_d():
    markers, warnings, _ = extract_lab_markers("25-OH Vitamin D 22 ng/mL 30 - 100")
    assert not warnings
    assert markers[0].marker_key == "vitamin_d_25_oh"
    assert markers[0].value == 22
    assert markers[0].status == "low"
