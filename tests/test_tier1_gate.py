"""Tier 1 Gate tests — Fixture 1 must run end-to-end with +40 mismatch -> CRITICAL."""
from __future__ import annotations

import json
import uuid
from pathlib import Path

import pytest
from langgraph.types import Command

from agent.graph import app
from agent.risk_engine import calculate_risk_score

ROOT = Path(__file__).resolve().parent.parent
F1 = ROOT / "data" / "fixtures" / "fixture_1_mismatch"


def _config():
    return {"configurable": {"thread_id": str(uuid.uuid4())}}


def test_risk_engine_caps_and_thresholds():
    score, level, triggers = calculate_risk_score({"intent_mechanism_mismatch": True})
    assert score == 40 and level == "SUSPICIOUS"
    assert any("CRITICAL: claims RECEIVE" in t for t in triggers)

    # Category cap: url signals cannot exceed 50
    score, _, _ = calculate_risk_score({
        "is_known_malicious": True,        # +50 url (cap hit)
        "brand_mismatch": True,            # would be +25 but capped
        "is_punycode_or_lookalike": True,  # would be +30 but capped
        "domain_age_days": 3,              # would be +20 but capped
    })
    assert score == 50

    # Max total = 135
    score, level, _ = calculate_risk_score({
        "is_known_malicious": True,
        "intent_mechanism_mismatch": True,
        "is_upi_collection_request": True,
        "has_urgency_threats": True,
        "requests_sensitive_info": True,
    })
    assert score == 135 and level == "CRITICAL"

    # Never "safe"
    _, level, _ = calculate_risk_score({})
    assert level == "NO_STRONG_INDICATORS"


def test_fixture1_end_to_end_gate():
    """THE GATE: Fixture 1 -> +40 mismatch trigger -> CRITICAL."""
    expected = json.loads((F1 / "expected.json").read_text(encoding="utf-8"))
    msg = (F1 / "message.txt").read_text(encoding="utf-8")
    qr = (F1 / "qr.png").read_bytes()

    result = app.invoke({"user_input": msg, "qr_image": qr}, _config())

    assert result.get("intent", {}).get("category") == expected["intent"]
    assert result.get("mechanism", {}).get("action") == expected["mechanism"]
    assert result["evidence_vector"]["intent_mechanism_mismatch"] is True
    assert any(expected["expected_trigger"] in t for t in result["triggers"])
    assert result["risk_level"] == expected["expected_level"]
    assert result["score"] >= expected["min_score"]
    nodes = [e["node"] for e in result["trace_log"]]
    assert "mismatch" in nodes and "risk_engine" in nodes and "explainer" in nodes
    assert result.get("explanation")
    # No clarify interruption on a high-confidence narrative
    assert "__interrupt__" not in result


def test_fixture2_lookalike_cached_whois():
    """Fixture 2 — lookalike domain scored from CACHE only (hermetic)."""
    msg = (ROOT / "data" / "fixtures" / "fixture_2_lookalike" / "message.txt").read_text(
        encoding="utf-8"
    )
    result = app.invoke({"user_input": msg}, _config())
    assert "__interrupt__" not in result  # neutral narrative, no QR -> no clarify
    ev = result["evidence_vector"]
    assert ev["domain_age_days"] == 5             # from cached WHOIS JSON
    assert ev["brand_mismatch"] is True            # text says HDFC, domain isn't official
    assert ev["is_punycode_or_lookalike"] is True  # hdfc embedded in non-official domain
    assert result["score"] >= 25
    assert result["risk_level"] in ("SUSPICIOUS", "HIGH", "CRITICAL")


def test_clarify_loop_fires_on_ambiguous_intent():
    """Loop 1 — ambiguous narrative + QR mechanism -> agent asks, then re-plans."""
    qr = (F1 / "qr.png").read_bytes()
    cfg = _config()
    result = app.invoke(
        {"user_input": "Complete the pending process. Reply to proceed.",
         "qr_image": qr},
        cfg,
    )
    assert "__interrupt__" in result, "clarify loop should have fired"
    question = result["__interrupt__"][0].value
    assert "pay" in question.lower() and "receive" in question.lower()

    # Resume with the user's answer -> graph re-plans and completes
    result = app.invoke(Command(resume="pay"), cfg)
    assert "clarify" in [e["node"] for e in result["trace_log"]]
    assert result["intent"]["category"] == "SEND_MONEY"
    assert result.get("explanation")


def test_deep_scan_loop_on_borderline_score():
    """Loop 2 — borderline score + unverified URL -> escalates, re-scores, explains."""
    msg = (
        "Send Rs.500 now at http://free-recharge-win.com and share OTP "
        "to confirm, or the offer expires within 24 hours."
    )
    result = app.invoke({"user_input": msg}, _config())
    nodes = [e["node"] for e in result["trace_log"]]
    assert "__interrupt__" not in result
    assert "deep_scan" in nodes, "deep-scan loop should have escalated"
    assert result["deep_scan_performed"] is True
    assert result["evidence_vector"]["domain_age_days"] == 15  # escalation assumption
    assert result["score"] >= 50 and result["risk_level"] in ("HIGH", "CRITICAL")
    assert "explainer" in nodes  # loop terminated — no infinite re-scan


def test_incident_router():
    """Router classifies incident reports -> incident interview begins (Tier 2)."""
    result = app.invoke({"user_input": "I got scammed yesterday, money was deducted"}, _config())
    assert result["mode"] == "INCIDENT"
    # Interview starts — first question asks for the transaction ID
    assert "__interrupt__" in result
    assert "transaction id" in result["__interrupt__"][0].value.lower()


def test_explanation_never_says_safe():
    result = app.invoke({"user_input": "hello"}, _config())
    explanation = result.get("explanation", "").lower()
    assert "no strong indicators" in explanation
    assert result["risk_level"] == "NO_STRONG_INDICATORS"
