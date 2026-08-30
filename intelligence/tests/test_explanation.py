"""Tests for intelligence/explanation.py: the I-10 human-readable explanation module."""

from __future__ import annotations

from intelligence import explanation, orchestrator


def _packet(displacement=1.2):
    return {
        "schema_version": "1.0",
        "node_id": "NODE_A",
        "sequence": 1,
        "timestamp": "2026-08-29T16:30:00Z",
        "sensors": {
            "tilt_x_deg": 0.4,
            "tilt_y_deg": 0.2,
            "vibration_g": 0.08,
            "displacement_mm": displacement,
        },
        "health": {"mpu6050_ok": True, "displacement_input_ok": True, "connection_ok": True},
    }


def _decision_and_evidence(displacement=1.2, **kwargs):
    result = orchestrator.orchestrate_decision(_packet(displacement=displacement), **kwargs)
    return result["decision"], result["evidence"]


def test_no_llm_client_configured_uses_template_fallback():
    decision, evidence = _decision_and_evidence()
    result = explanation.generate_explanation(decision, evidence, llm_client=None)
    assert result["source"] == "template_fallback"
    assert decision["node_id"] in result["explanation"]
    assert decision["state"] in result["explanation"]


def test_failing_llm_client_falls_back_and_does_not_raise():
    def broken_llm(decision, evidence):
        raise RuntimeError("simulated LLM outage")

    decision, evidence = _decision_and_evidence(displacement=9.0)
    result = explanation.generate_explanation(decision, evidence, llm_client=broken_llm)
    assert result["source"] == "template_fallback"
    assert result["explanation"]  # still produced a usable explanation


def test_llm_client_returning_empty_string_falls_back():
    decision, evidence = _decision_and_evidence()
    result = explanation.generate_explanation(decision, evidence, llm_client=lambda d, e: "   ")
    assert result["source"] == "template_fallback"


def test_llm_client_returning_none_falls_back():
    decision, evidence = _decision_and_evidence()
    result = explanation.generate_explanation(decision, evidence, llm_client=lambda d, e: None)
    assert result["source"] == "template_fallback"


def test_successful_llm_client_response_is_used_verbatim():
    decision, evidence = _decision_and_evidence()
    result = explanation.generate_explanation(
        decision, evidence, llm_client=lambda d, e: "  A calm reading from Node A.  "
    )
    assert result["source"] == "llm"
    assert result["explanation"] == "A calm reading from Node A."


def test_result_never_carries_risk_confidence_or_state_as_its_own_fields():
    decision, evidence = _decision_and_evidence()
    result = explanation.generate_explanation(decision, evidence)
    assert set(result.keys()) == {"explanation", "source"}


def test_reason_codes_are_reflected_in_template_explanation():
    decision, evidence = _decision_and_evidence(displacement=9.0)  # CRITICAL, DISPLACEMENT_RISING
    result = explanation.generate_explanation(decision, evidence)
    assert "displacement" in result["explanation"].lower()


def test_normal_reading_with_no_reason_codes_still_explains_cleanly():
    decision, evidence = _decision_and_evidence(displacement=1.2)
    assert decision["reason_codes"] == []
    result = explanation.generate_explanation(decision, evidence)
    assert "no elevated evidence" in result["explanation"]


def test_pipeline_continues_normally_end_to_end_when_llm_fails():
    """Full integration: orchestrator + explanation, with a broken LLM, must still
    yield a complete, valid decision AND a usable explanation."""

    def broken_llm(decision, evidence):
        raise ConnectionError("network unreachable")

    result = orchestrator.orchestrate_decision(_packet(displacement=4.5))
    explanation_result = explanation.generate_explanation(
        result["decision"], result["evidence"], llm_client=broken_llm
    )
    assert result["decision"]["state"] == "WARNING"
    assert explanation_result["source"] == "template_fallback"
    assert explanation_result["explanation"]
