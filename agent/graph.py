"""VeriFi LangGraph — the edges that make it an agent (Plan Part 1).

Three loops:
  1. Clarify      — intent confidence < 0.7 -> agent ASKS the user, then re-plans
  2. Deep scan    — score 25-74 + evidence gap -> agent escalates tools, re-scores
  3. (Tier 2) Incident interview — multi-turn slot filling with checkpointer memory
"""
from __future__ import annotations

import json
import os
import re
from pathlib import Path

from dotenv import load_dotenv
from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import END, START, StateGraph
from langgraph.types import Command, interrupt

from agent.incident import INCIDENT_QUESTIONS, build_playbook, next_open_slot, normalize_answer
from agent.mismatch import detect_mismatch
from agent.risk_engine import calculate_detailed
from agent.router import router_node
from agent.state import AgentState
from tools.intent_extractor import detect_hinglish, extract_intent
from tools.qr_decoder import decode_qr, extract_mechanism
from tools.url_intel import get_url_intel

load_dotenv()

TAXONOMY_PATH = Path(__file__).resolve().parent.parent / "data" / "scam_taxonomy.json"

URGENCY_WORDS = [
    "immediately", "urgent", "within 24", "last warning", "block", "blocked",
    "suspend", "terminated", "warna", "turant", "jaldi", "arrest", "warrant",
    "expire", "expiry", "final notice",
]
SENSITIVE_WORDS = ["otp", "pin", "cvv", "password", "secret key", "upi pin"]
BRAND_WORDS = ["sbi", "hdfc", "icici", "axis", "paytm", "phonepe", "google pay", "gpay"]
URL_RE = re.compile(r"(https?://[^\s]+|www\.[^\s]+|[a-z0-9-]+\.(?:com|in|net|org|co)(?:/[^\s]*)?)", re.I)


def _load_taxonomy() -> dict:
    try:
        return json.loads(TAXONOMY_PATH.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {"patterns": []}


def _match_taxonomy(text: str) -> list:
    low = text.lower()
    hits = []
    for pat in _load_taxonomy().get("patterns", []):
        for signal in pat.get("signals", []):
            if signal.lower() in low:
                hits.append(pat["id"])
                break
    return hits


# ─────────────────────────── NODES ───────────────────────────

def evidence_tools(state: AgentState) -> dict:
    """T1 URL Intel + T2 QR Decode + T3 Taxonomy + intent + MISMATCH (Tier 1 core)."""
    text = state.get("user_input", "")
    trace = []
    ev: dict = dict(state.get("evidence_vector") or {})

    # ── Intent extraction (narrative) ──
    intent = extract_intent(text)

    # User answered the clarify question -> trust the user over the LLM
    clarify_answer = (state.get("clarify_answer") or "").strip()
    if clarify_answer:
        ans = clarify_answer.lower()
        if "pay" in ans or "send" in ans:
            intent = {"category": "SEND_MONEY", "confidence": 0.95, "source": "user"}
        elif "receiv" in ans or "get" in ans or "receive" in ans:
            intent = {"category": "RECEIVE_MONEY", "confidence": 0.95, "source": "user"}
        trace.append({
            "node": "intent",
            "decision": intent["category"],
            "detail": f"Clarify answer '{clarify_answer}' -> {intent['category']} (conf {intent['confidence']})",
        })
    else:
        trace.append({
            "node": "intent",
            "decision": intent["category"],
            "detail": f"Narrative intent {intent['category']} (conf {intent['confidence']}, {intent.get('source')})",
        })

    # ── QR decode (mechanism) ──
    mechanism = {"action": "UNKNOWN", "payload": ""}
    qr_image = state.get("qr_image")
    if qr_image:
        decoded = decode_qr(qr_image)
        if decoded.get("status") == "OK":
            mechanism = extract_mechanism(decoded["payload"])
            trace.append({
                "node": "qr_decode",
                "decision": mechanism["action"],
                "detail": f"QR payload -> {mechanism['action']}: {mechanism['payload'][:80]}",
            })
        else:
            trace.append({
                "node": "qr_decode",
                "decision": "ERROR",
                "detail": f"QR decode failed: {decoded.get('reason')}",
            })

    # ── Mismatch engine (THE KILLER FEATURE) ──
    mm = detect_mismatch(intent, mechanism)
    ev["intent_mechanism_mismatch"] = mm["mismatch"]
    trace.append({
        "node": "mismatch",
        "decision": "MISMATCH +40" if mm["mismatch"] else "no mismatch",
        "detail": mm["detail"],
    })

    # ── URL intel (cache-first) ──
    urls = URL_RE.findall(text)
    claimed_brand = next((b for b in BRAND_WORDS if b in text.lower()), None)
    if urls:
        url_ev = get_url_intel(urls[0], claimed_brand)
        for key in ("domain", "is_known_malicious", "brand_mismatch",
                    "is_punycode_or_lookalike", "domain_age_days", "status",
                    "urlscan_source", "urlscan_category"):
            if key in url_ev:
                ev[key] = url_ev[key]
        detail = (
            f"{urls[0]} source={url_ev.get('source')} age={url_ev.get('domain_age_days')}d "
            f"malicious={url_ev.get('is_known_malicious')} brand_mismatch={url_ev.get('brand_mismatch')}"
        )
        if url_ev.get("urlscan_source"):
            detail += (
                f" | urlscan={url_ev['urlscan_source']}"
                f"{' (' + url_ev['urlscan_category'] + ')' if url_ev.get('urlscan_category') else ''}"
            )
        trace.append({
            "node": "url_intel",
            "decision": url_ev.get("status", "OK"),
            "detail": detail,
        })

    # ── Social engineering signals (deterministic keywords) ──
    low = text.lower()
    ev["has_urgency_threats"] = any(w in low for w in URGENCY_WORDS)
    ev["requests_sensitive_info"] = any(w in low for w in SENSITIVE_WORDS)
    ev["is_upi_collection_request"] = mechanism.get("action") == "REQUEST_MONEY"
    if ev["has_urgency_threats"]:
        trace.append({"node": "social", "decision": "urgency", "detail": "Urgency/threat language detected"})
    if ev["requests_sensitive_info"]:
        trace.append({"node": "social", "decision": "sensitive", "detail": "Requests OTP/PIN/credentials"})

    # ── Taxonomy KB match ──
    tax_hits = _match_taxonomy(text)
    if tax_hits:
        trace.append({
            "node": "taxonomy",
            "decision": ",".join(tax_hits),
            "detail": f"Matched {len(tax_hits)} pattern(s) in scam_taxonomy.json",
        })

    # ── Language routing (Hinglish detection -> explainer switches language) ──
    language = detect_hinglish(text)
    if language == "hinglish":
        trace.append({
            "node": "language",
            "decision": "hinglish",
            "detail": "Hinglish/Hindi detected — explanation will be routed in Hinglish",
        })

    # ── Evidence gaps the planner can see (a deeper tool could fill these) ──
    missing = []
    low_text = text.lower()
    mentions_qr = ("qr" in low_text or "scan" in low_text)
    if mentions_qr and not mechanism.get("payload"):
        missing.append("qr_payload")
    if urls and ev.get("status") == "UNVERIFIED":
        missing.append("url_unverified")

    return {
        "intent": intent,
        "mechanism": mechanism,
        "evidence_vector": ev,
        "clarify_needed": mm["clarify_needed"] and not clarify_answer,
        "clarify_question": mm["clarify_question"],
        "missing_slots": missing,
        "language": language,
        "trace_log": trace,
    }


def risk_engine_node(state: AgentState) -> dict:
    """Deterministic category-capped scoring — the engine decides, always."""
    score, level, triggers, breakdown = calculate_detailed(state.get("evidence_vector") or {})
    return {
        "score": score,
        "risk_level": level,
        "triggers": triggers,
        "score_breakdown": breakdown,
        "trace_log": [{
            "node": "risk_engine",
            "decision": f"{score} -> {level}",
            "detail": ("; ".join(triggers) if triggers else "no signals fired")
                      + f" [url={breakdown['url']}/50 upi={breakdown['upi']}/55 social={breakdown['social']}/30]",
        }],
    }


def planner(state: AgentState) -> dict:
    """THE BRAIN — reads score + evidence gaps, decides what to do next."""
    return {"trace_log": [{
        "node": "planner",
        "decision": "evaluating",
        "detail": f"score={state.get('score')} clarify={state.get('clarify_needed')} "
                  f"missing={state.get('missing_slots')} deep_scanned={state.get('deep_scan_performed')}",
    }]}


def planner_decision(state: AgentState) -> str:
    """Conditional edge: clarify | deep_scan | explain (Plan Part 1)."""
    if state.get("clarify_needed"):
        return "clarify"
    score = state.get("score", 0)
    has_gap = bool(state.get("missing_slots"))
    if 25 <= score <= 74 and has_gap and not state.get("deep_scan_performed"):
        return "deep_scan"
    return "explain"


def clarify_node(state: AgentState) -> dict:
    """Loop 1 — the agent STOPS and asks the user. Resumes via Command(resume=...)."""
    question = state.get("clarify_question") or (
        "Is this message asking you to pay money or receive money?"
    )
    answer = interrupt(question)
    return {
        "clarify_answer": str(answer),
        "clarify_needed": False,
        "trace_log": [{
            "node": "clarify",
            "decision": "asked user",
            "detail": f"Q: {question} | A: {answer}",
        }],
    }


def deep_scan_node(state: AgentState) -> dict:
    """Loop 2 — escalating verification: deeper tools, then re-score."""
    ev = dict(state.get("evidence_vector") or {})
    trace = [{
        "node": "deep_scan",
        "decision": "escalate",
        "detail": f"Borderline score {state.get('score')} with gaps {state.get('missing_slots')} — running deeper checks",
    }]

    # Deep check 1: fuzzy brand match on domain against claimed brand
    domain = str(ev.get("domain", ""))
    if domain:
        import difflib
        brand = next((b for b in BRAND_WORDS if b in (state.get("user_input", "")).lower()), None)
        if brand and not difflib.get_close_matches(brand, [domain], n=1, cutoff=0.6):
            if not ev.get("brand_mismatch"):
                ev["brand_mismatch"] = True
                trace.append({
                    "node": "deep_scan",
                    "decision": "brand mismatch confirmed",
                    "detail": f"Fuzzy match: '{brand}' vs domain '{domain}' — no similarity",
                })

    # Deep check 2: unverified URL on a borderline score -> treat age as unknown-suspicious
    if ev.get("status") == "UNVERIFIED" and ev.get("domain_age_days", 999) == 999:
        ev["domain_age_days"] = 15  # cannot verify age -> assume recent (documented assumption)
        trace.append({
            "node": "deep_scan",
            "decision": "age unverified",
            "detail": "WHOIS unavailable offline; treating as recent domain (documented)",
        })

    missing = [m for m in (state.get("missing_slots") or []) if m != "url_unverified"]
    return {
        "evidence_vector": ev,
        "deep_scan_performed": True,
        "missing_slots": missing,
        "trace_log": trace,
    }


def explainer_node(state: AgentState) -> dict:
    """LLM explains THE MATH — never overrides it. Deterministic fallback.
    Hinglish input -> explanation routed in Hinglish (Plan Part 1)."""
    score = state.get("score", 0)
    level = state.get("risk_level", "NO_STRONG_INDICATORS")
    triggers = state.get("triggers") or []
    intent = state.get("intent") or {}
    mechanism = state.get("mechanism") or {}
    hinglish = state.get("language") == "hinglish"

    prompt = f"""You are VeriFi's explainer. Explain this risk assessment to an Indian UPI user.
Score: {score}/135. Level: {level} (thresholds: 75+ CRITICAL, 50+ HIGH, 25+ SUSPICIOUS).
Triggers: {chr(10).join('- ' + t for t in triggers) or 'none'}.
Narrative intent: {intent.get('category')} (confidence {intent.get('confidence')}).
QR mechanism: {mechanism.get('action')}.
Rules: explain WHY each point was awarded; NEVER change the score; NEVER say 'safe' —
if level is NO_STRONG_INDICATORS say 'no strong indicators detected'. Keep under 120 words.
End with a short action plan."""
    if hinglish:
        prompt += "\nThe user's message was in Hinglish — reply in Hinglish (Roman script, Hindi-English mix)."

    api_key = os.getenv("GROQ_API_KEY") or os.getenv("GROQ_API_KEY_BACKUP")
    explanation = None
    if api_key:
        try:
            from groq import Groq

            client = Groq(api_key=api_key)
            resp = client.chat.completions.create(
                model=os.getenv("GROQ_MODEL", "openai/gpt-oss-120b"),
                messages=[{"role": "user", "content": prompt}],
                temperature=0.3,
                max_tokens=800,
            )
            explanation = resp.choices[0].message.content
        except Exception:
            explanation = None

    if not explanation:
        # Deterministic fallback — the math explained without an LLM
        if hinglish:
            lines = [
                f"VeriFi ne is message ko evidence ke basis par {score}/135 score diya "
                f"-> {level} (CRITICAL>=75, HIGH>=50, SUSPICIOUS>=25).",
            ]
            if triggers:
                lines.append("Reasons: " + "; ".join(triggers) + ".")
            else:
                lines.append("Is evidence me koi strong indicator nahi mila — par "
                             "dhyan rakhiye: ye proof nahi hai ki sab kuch theek hai.")
            if state.get("intent_mechanism_mismatch"):
                lines.append(
                    "Sabse bada saboot: message kaha hai ki aap RECEIV karoge, par QR "
                    "aapko DEBIT karega — ye seedha dhokha hai."
                )
            lines.append(
                "Action: koi QR scan mat kariye, koi payment mat kariye, aur doubt ho to "
                "1930 par call kariye ya cybercrime.gov.in par report kariye."
            )
            explanation = " ".join(lines)
        else:
            lines = [
                f"VeriFi scored this {score}/135 -> {level} "
                f"(thresholds: CRITICAL>=75, HIGH>=50, SUSPICIOUS>=25).",
            ]
            if triggers:
                lines.append("Why: " + "; ".join(triggers) + ".")
            else:
                lines.append("Why: no strong indicators detected in the evidence.")
            if state.get("intent_mechanism_mismatch"):
                lines.append(
                    "Key finding: the message claims you will RECEIVE money, but the QR "
                    "actually DEBITS you — direct evidence of deception."
                )
            lines.append(
                "Action plan: do not scan/pay; verify with the official bank app or call 1930."
            )
            explanation = " ".join(lines)

    return {
        "explanation": explanation,
        "trace_log": [{
            "node": "explainer",
            "decision": "explained (hinglish)" if hinglish else "explained",
            "detail": "LLM explains the engine's math — score unchanged (never overridden)",
        }],
    }


def incident_interview_node(state: AgentState) -> dict:
    """Loop 3 — interview the victim ONE question at a time (checkpointer memory).

    Each invoke with Command(resume=...) fills exactly one slot, then the
    conditional edge loops back here until all slots are filled.
    """
    slots = dict(state.get("incident_slots") or {})
    open_slot = next_open_slot(slots)
    if open_slot is None:
        return {"incident_slots": slots}  # defensive: all filled -> playbook

    key, question = open_slot
    answer = interrupt(question)
    slots[key] = normalize_answer(answer)
    return {
        "incident_slots": slots,
        "trace_log": [{
            "node": "incident_interview",
            "decision": f"{key} = {slots[key]}",
            "detail": f"Q{len(INCIDENT_QUESTIONS) - sum(1 for k, _ in INCIDENT_QUESTIONS if k in slots) + 1}"
                      f"/{len(INCIDENT_QUESTIONS)}: {question} | A: {answer}",
        }],
    }


def incident_decision(state: AgentState) -> str:
    """All slots filled -> playbook; otherwise ask the next question."""
    slots = state.get("incident_slots") or {}
    if next_open_slot(slots) is None:
        return "playbook"
    return "interview"


def playbook_node(state: AgentState) -> dict:
    """Personalized recovery playbook built from the victim's own answers."""
    slots = state.get("incident_slots") or {}
    playbook = build_playbook(slots)
    return {
        "playbook": playbook,
        "explanation": "Interview complete — your personalized recovery playbook is ready below.",
        "trace_log": [{
            "node": "playbook",
            "decision": "personalized",
            "detail": f"Playbook generated from slots: {slots}",
        }],
    }


# ─────────────────────────── GRAPH ───────────────────────────

def build_graph():
    g = StateGraph(AgentState)
    g.add_node("router", router_node)
    g.add_node("evidence_tools", evidence_tools)
    g.add_node("risk_engine", risk_engine_node)
    g.add_node("planner", planner)
    g.add_node("clarify_node", clarify_node)
    g.add_node("deep_scan_node", deep_scan_node)
    g.add_node("explainer_node", explainer_node)
    g.add_node("incident_interview", incident_interview_node)
    g.add_node("playbook_node", playbook_node)

    g.add_edge(START, "router")
    g.add_conditional_edges(
        "router",
        lambda s: "incident" if s.get("mode") == "INCIDENT" else "analyze",
        {"analyze": "evidence_tools", "incident": "incident_interview"},
    )
    g.add_edge("evidence_tools", "risk_engine")
    g.add_edge("risk_engine", "planner")
    g.add_conditional_edges(
        "planner",
        planner_decision,
        {
            "clarify": "clarify_node",
            "deep_scan": "deep_scan_node",
            "explain": "explainer_node",
        },
    )
    g.add_edge("clarify_node", "evidence_tools")   # re-plan with new info
    g.add_edge("deep_scan_node", "risk_engine")    # re-score with new evidence
    g.add_edge("explainer_node", END)
    # Incident branch: interview loops until all slots filled -> playbook
    g.add_conditional_edges(
        "incident_interview",
        incident_decision,
        {"interview": "incident_interview", "playbook": "playbook_node"},
    )
    g.add_edge("playbook_node", END)

    return g.compile(checkpointer=MemorySaver())


app = build_graph()
