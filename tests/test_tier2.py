"""Tier 2 tests — incident interview, playbook, Hinglish, taxonomy, breakdown."""
from __future__ import annotations

import json
from pathlib import Path

from langgraph.types import Command

from agent.graph import app
from agent.incident import build_playbook, normalize_answer
from tools.intent_extractor import detect_hinglish

ROOT = Path(__file__).resolve().parent.parent
F3 = ROOT / "data" / "fixtures" / "fixture_3_incident"
F4 = ROOT / "data" / "fixtures" / "fixture_4_legit"


def _config():
    from uuid import uuid4

    return {"configurable": {"thread_id": str(uuid4())}}


def test_fixture3_full_interview_and_personalized_playbook():
    """Deliverable: fixture 3 runs end-to-end — 4 turns -> personalized playbook."""
    expected = json.loads((F3 / "expected.json").read_text(encoding="utf-8"))
    answers = json.loads((F3 / "interview_answers.json").read_text(encoding="utf-8"))
    msg = (F3 / "message.txt").read_text(encoding="utf-8")

    cfg = _config()
    result = app.invoke({"user_input": msg}, cfg)
    assert result["mode"] == expected["mode"] == "INCIDENT"

    # ONE question per turn — order: txn ID -> bank -> amount -> time
    order = ["transaction id", "bank", "how much", "when"]
    turn = 0
    while "__interrupt__" in result:
        question = result["__interrupt__"][0].value.lower()
        assert order[turn] in question, f"turn {turn + 1} asked out of order: {question}"
        key = expected["slots"][turn]
        result = app.invoke(Command(resume=answers[key]), cfg)
        turn += 1
    assert turn == 4, "interview must ask exactly one question per slot"

    # All slots captured
    assert set(result["incident_slots"].keys()) == set(expected["slots"])

    # Playbook is personalized from THEIR answers
    playbook = result["playbook"]
    assert answers["txn_id"] in playbook
    assert answers["bank"] in playbook
    assert answers["amount"] in playbook
    assert answers["time"] in playbook
    for term in expected["playbook_terms"]:
        assert term in playbook

    # Trace shows the interview turns + playbook generation
    nodes = [e["node"] for e in result["trace_log"]]
    assert nodes.count("incident_interview") == 4
    assert "playbook" in nodes


def test_fixture4_legit_zero_false_positive():
    """Deliverable: fixture 4 (legit UPI) -> NO_STRONG_INDICATORS, no clarify."""
    expected = json.loads((F4 / "expected.json").read_text(encoding="utf-8"))
    msg = (F4 / "message.txt").read_text(encoding="utf-8")

    result = app.invoke({"user_input": msg}, _config())
    assert result["mode"] == expected["mode"]
    assert "__interrupt__" not in result
    assert result["risk_level"] == expected["expected_level"]
    assert result["score"] <= expected["max_score"]


def test_all_four_fixtures_have_complete_traces():
    """Deliverable: all 4 fixtures run with complete agent traces."""
    f1 = ROOT / "data" / "fixtures" / "fixture_1_mismatch"
    runs = []

    r = app.invoke(
        {"user_input": (f1 / "message.txt").read_text(encoding="utf-8"),
         "qr_image": (f1 / "qr.png").read_bytes()},
        _config(),
    )
    assert "__interrupt__" not in r and r["risk_level"] == "CRITICAL"
    runs.append(r)

    f2 = ROOT / "data" / "fixtures" / "fixture_2_lookalike"
    r = app.invoke({"user_input": (f2 / "message.txt").read_text(encoding="utf-8")}, _config())
    assert r["risk_level"] in ("SUSPICIOUS", "HIGH", "CRITICAL")
    runs.append(r)

    cfg = _config()
    r = app.invoke(
        {"user_input": (F3 / "message.txt").read_text(encoding="utf-8")}, cfg
    )
    answers = ["TXN1", "SBI", "5000", "yesterday"]
    for a in answers:
        assert "__interrupt__" in r
        r = app.invoke(Command(resume=a), cfg)
    assert r.get("playbook") and "1930" in r["playbook"]
    runs.append(r)

    r = app.invoke({"user_input": (F4 / "message.txt").read_text(encoding="utf-8")}, _config())
    assert r["risk_level"] == "NO_STRONG_INDICATORS"
    runs.append(r)

    for r in runs:
        assert len(r.get("trace_log") or []) >= 3, "every fixture must produce a visible trace"


def test_interview_skip_marks_unknown_and_still_completes():
    """Skip answers don't block the interview; playbook handles unknown slots."""
    cfg = _config()
    r = app.invoke({"user_input": "I got scammed, money was deducted"}, cfg)
    for answer in ["skip", "HDFC", "10000", "today morning"]:
        assert "__interrupt__" in r
        r = app.invoke(Command(resume=answer), cfg)
    assert r["incident_slots"]["txn_id"] == "unknown"
    assert "could not be provided" in r["playbook"]
    assert "1930" in r["playbook"]


def test_normalize_answer():
    assert normalize_answer("  ") == "unknown"
    assert normalize_answer("don't know") == "unknown"
    assert normalize_answer("TXN123") == "TXN123"


def test_hinglish_detection():
    hinglish = "Kya aapko cashback chahiye? Is QR ko scan karo aur paisa receive karo - turant!"
    english = "Payment received! Rahul sent you Rs. 500 for movie tickets."
    devanagari = "यूपीआई भुगतान प्राप्त हुआ"
    assert detect_hinglish(hinglish) == "hinglish"
    assert detect_hinglish(english) == "en"
    assert detect_hinglish(devanagari) == "hinglish"


def test_hinglish_routes_explainer():
    """Hinglish input -> language flagged + Hinglish explanation (fallback path)."""
    hinglish = "Turant ye QR scan karo aur cashback milega, warna offer band ho jayegi!"
    result = app.invoke({"user_input": hinglish}, _config())
    assert result["language"] == "hinglish"
    assert "score diya" in result["explanation"]          # Hinglish fallback template
    assert "VeriFi scored this" not in result["explanation"]  # NOT the English template
    assert "1930" in result["explanation"]                # action plan present
    assert "safe" not in result["explanation"].lower()    # never say "safe"
    # trace records the routing decision
    assert "language" in [e["node"] for e in result["trace_log"]]


def test_english_routes_english_explainer():
    result = app.invoke(
        {"user_input": "Your account will be blocked. Update KYC at https://sbi-kyc-verify.com"},
        _config(),
    )
    assert result["language"] == "en"
    assert "VeriFi scored this" in result["explanation"]


def test_taxonomy_20_plus_patterns():
    tax = json.loads(
        (ROOT / "data" / "scam_taxonomy.json").read_text(encoding="utf-8")
    )
    assert len(tax["patterns"]) >= 20


def test_score_breakdown_in_state():
    """Judge-facing per-category breakdown: url/upi/social with caps visible."""
    f1 = ROOT / "data" / "fixtures" / "fixture_1_mismatch"
    result = app.invoke(
        {"user_input": (f1 / "message.txt").read_text(encoding="utf-8"),
         "qr_image": (f1 / "qr.png").read_bytes()},
        _config(),
    )
    bd = result["score_breakdown"]
    assert set(bd.keys()) == {"url", "upi", "social"}
    assert bd["url"] <= 50 and bd["upi"] <= 55 and bd["social"] <= 30
    assert sum(bd.values()) == result["score"]


def test_build_playbook_deterministic():
    p = build_playbook({"txn_id": "T1", "bank": "SBI", "amount": "500", "time": "today"})
    assert all(x in p for x in ("T1", "SBI", "500", "today", "1930", "cybercrime.gov.in"))
