from collections.abc import Iterable

from app.models import LabResult


def _lab_to_map(results: Iterable[LabResult]) -> dict[str, LabResult]:
    return {item.marker_key: item for item in results}


def _base_safety() -> dict:
    return {
        "safety_note": (
            "This is educational guidance only. It does not replace a clinician's assessment, "
            "especially before starting supplements or changing treatment."
        )
    }


def recommendation_for_marker(result: LabResult, supporting_results: Iterable[LabResult] = ()) -> dict:
    support_map = _lab_to_map(supporting_results)
    payload = {
        "headline": f"{result.marker_label} is {result.status}.",
        "foods": [],
        "lifestyle": [],
        "supplement_discussion": [],
        "questions_for_doctor": [],
        **_base_safety(),
    }

    if result.marker_key == "hemoglobin" and result.status == "low":
        ferritin = support_map.get("ferritin")
        b12 = support_map.get("vitamin_b12")
        payload.update(
            {
                "why_it_matters": "Low hemoglobin can reflect anemia or reduced oxygen-carrying capacity.",
                "foods": [
                    "Iron-rich foods: lentils, beans, spinach, tofu, eggs, lean meat if you eat it",
                    "Pair iron-rich foods with vitamin C sources like lemon, amla, orange, guava, or capsicum",
                ],
                "lifestyle": [
                    "Avoid tea or coffee close to iron-rich meals",
                    "Review heavy bleeding, fatigue, breathlessness, or frequent blood donation with your doctor",
                ],
                "supplement_discussion": [
                    "Iron supplements are often used only when iron deficiency is confirmed",
                    "Do not self-start high-dose iron if ferritin or iron studies have not been reviewed",
                ],
                "questions_for_doctor": [
                    "Do I need ferritin, serum iron, transferrin saturation, B12, or folate review?",
                    "Could blood loss or another cause explain the low hemoglobin?",
                ],
            }
        )
        if ferritin and ferritin.status == "low":
            payload["pattern_hint"] = "Low hemoglobin with low ferritin may fit iron deficiency."
        if b12 and b12.status == "low":
            payload["pattern_hint"] = "Low hemoglobin with low B12 can suggest mixed or non-iron causes of anemia."
        return payload

    if result.marker_key == "ferritin" and result.status == "low":
        payload.update(
            {
                "why_it_matters": "Ferritin reflects iron stores in the body.",
                "foods": [
                    "Beans, lentils, chickpeas, soy, leafy greens, pumpkin seeds",
                    "Add vitamin C with meals to improve non-heme iron absorption",
                ],
                "lifestyle": [
                    "Space tea or coffee away from meals when trying to improve iron intake",
                    "Review heavy periods, GI symptoms, or endurance overtraining if relevant",
                ],
                "supplement_discussion": [
                    "Discuss dose and duration of iron supplementation with your doctor",
                    "Iron can be harmful if taken unnecessarily or in very high doses",
                ],
                "questions_for_doctor": [
                    "Do I need a full iron study or repeat ferritin after treatment?",
                ],
            }
        )
        return payload

    if result.marker_key == "vitamin_b12" and result.status == "low":
        payload.update(
            {
                "why_it_matters": "Vitamin B12 supports nerve function and red blood cell production.",
                "foods": [
                    "Eggs, dairy, fish, meat if you consume them",
                    "Fortified cereals or fortified plant milks for vegetarian diets",
                ],
                "lifestyle": [
                    "Review vegetarian or vegan intake and long-term acid-suppressing medicines",
                ],
                "supplement_discussion": [
                    "B12 tablets or injections are often chosen based on severity and cause",
                ],
                "questions_for_doctor": [
                    "Should I repeat B12 or review folate and anemia markers together?",
                ],
            }
        )
        return payload

    if result.marker_key == "vitamin_d_25_oh" and result.status == "low":
        payload.update(
            {
                "why_it_matters": "Vitamin D supports bone and muscle health.",
                "foods": [
                    "Fortified dairy or plant milks, egg yolk, fatty fish if you consume them",
                ],
                "lifestyle": [
                    "Discuss safe sunlight exposure based on your skin type and local climate",
                    "Keep up resistance exercise or walking if medically appropriate",
                ],
                "supplement_discussion": [
                    "Vitamin D supplements are common, but dose should be matched to your level and clinician advice",
                ],
                "questions_for_doctor": [
                    "What dose and repeat-test interval is appropriate for my level?",
                ],
            }
        )
        return payload

    if result.marker_key in {"fasting_glucose", "hba1c"} and result.status == "high":
        payload.update(
            {
                "why_it_matters": "Higher glucose markers can suggest impaired glucose control.",
                "foods": [
                    "Focus meals on protein, fiber, pulses, vegetables, and lower refined sugar intake",
                ],
                "lifestyle": [
                    "Aim for regular walking after meals if medically suitable",
                    "Review sleep, stress, and body-weight trends",
                ],
                "supplement_discussion": [
                    "Do not rely on supplements instead of medical diabetes evaluation",
                ],
                "questions_for_doctor": [
                    "Do I need repeat glucose testing or diabetes screening?",
                ],
            }
        )
        return payload

    if result.marker_key in {"ldl", "triglycerides"} and result.status == "high":
        payload.update(
            {
                "why_it_matters": "Higher lipid markers can increase cardiovascular risk over time.",
                "foods": [
                    "Increase soluble fiber: oats, beans, vegetables, seeds",
                    "Reduce excess fried foods, ultra-processed snacks, and sugary drinks",
                ],
                "lifestyle": [
                    "Build consistent exercise and improve sleep routine",
                    "Review alcohol intake if triglycerides are high",
                ],
                "supplement_discussion": [
                    "Do not replace clinician-guided treatment with over-the-counter supplements alone",
                ],
                "questions_for_doctor": [
                    "Should I repeat the lipid profile fasting and review overall risk?",
                ],
            }
        )
        return payload

    payload.update(
        {
            "why_it_matters": f"{result.marker_label} should be interpreted with your symptoms, medical history, and the rest of the panel.",
            "foods": ["Keep diet balanced and aligned with your doctor's advice."],
            "lifestyle": ["Continue periodic monitoring and discuss changes that are clinically meaningful."],
            "supplement_discussion": ["Only add supplements when a deficiency or specific need is confirmed."],
            "questions_for_doctor": ["Do I need any follow-up tests for this marker?"],
        }
    )
    return payload
