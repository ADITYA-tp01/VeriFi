"""VeriFi — Evidence-Driven Financial Safety Agent. Run: streamlit run app.py"""
from __future__ import annotations

import uuid
from pathlib import Path

import streamlit as st
from langgraph.types import Command

from agent.graph import app

st.set_page_config(page_title="VeriFi", page_icon="🛡️", layout="wide")

st.markdown(
    """
    <style>
    h1[data-testid="stTitle"] {
        letter-spacing: .5px;
        background: linear-gradient(90deg, #2563eb, #7c3aed);
        -webkit-background-clip: text;
        background-clip: text;
        color: transparent !important;
    }
    [data-testid="stMetricValue"] { font-variant-numeric: tabular-nums; }
    [data-testid="stMetric"] {
        background: rgba(128,128,128,.07);
        border: 1px solid rgba(128,128,128,.18);
        border-radius: 12px;
        padding: 12px 16px;
    }
    .vf-trace {
        border-left: 4px solid #3b82f6;
        background: rgba(128,128,128,.06);
        border-radius: 6px;
        padding: 7px 13px;
        margin: 5px 0;
    }
    .vf-trace b { color: #3b82f6; }
    .vf-decision { color: #dc2626; font-weight: 700; }
    .vf-score-critical { color: #dc2626; font-weight: 800; }
    .vf-score-high { color: #ea580c; font-weight: 800; }
    .vf-score-suspicious { color: #ca8a04; font-weight: 800; }
    .vf-score-clear { color: #16a34a; font-weight: 800; }
    </style>
    """,
    unsafe_allow_html=True,
)

FIX = Path(__file__).resolve().parent / "data" / "fixtures"

LEVEL_COLORS = {
    "CRITICAL": "🔴",
    "HIGH": "🟠",
    "SUSPICIOUS": "🟡",
    "NO_STRONG_INDICATORS": "🟢",
}

SCORE_CSS = {
    "CRITICAL": "vf-score-critical",
    "HIGH": "vf-score-high",
    "SUSPICIOUS": "vf-score-suspicious",
    "NO_STRONG_INDICATORS": "vf-score-clear",
}

BAD_DECISIONS = ("MISMATCH +40", "ERROR")

NODE_ICONS = {
    "router": "🧭", "intent": "🧠", "qr_decode": "📷", "mismatch": "⚡",
    "url_intel": "🔍", "social": "🗣️", "taxonomy": "📚", "language": "🌐",
    "risk_engine": "🧮", "planner": "🤖", "clarify": "❓", "deep_scan": "🔬",
    "explainer": "💬", "incident_interview": "🎙️", "playbook": "📋",
}

if "thread_id" not in st.session_state:
    st.session_state.thread_id = str(uuid.uuid4())
if "waiting_answer" not in st.session_state:
    st.session_state.waiting_answer = None
if "last_result" not in st.session_state:
    st.session_state.last_result = None

st.title("🛡️ VeriFi")
st.caption("Evidence-driven financial safety — deterministic math, agentic loops, LLM only explains.")


def run_graph(payload: dict):
    config = {"configurable": {"thread_id": st.session_state.thread_id}}
    return app.invoke(payload, config)


def resume_graph(answer: str):
    config = {"configurable": {"thread_id": st.session_state.thread_id}}
    return app.invoke(Command(resume=answer), config)


def load_result(result: dict):
    """Store result and pick up any pending interrupt (clarify / interview)."""
    st.session_state.last_result = result
    interrupts = result.get("__interrupt__")
    st.session_state.waiting_answer = interrupts[0].value if interrupts else None


def render_result(result: dict):
    score = result.get("score", 0)
    level = result.get("risk_level", "NO_STRONG_INDICATORS")
    icon = LEVEL_COLORS.get(level, "⚪")

    c1, c2, c3 = st.columns([1, 1, 2])
    c1.metric("Score", f"{score}/135")
    c2.markdown(
        f"<div>Level</div><div class='{SCORE_CSS.get(level, '')}' "
        f"style='font-size:1.4rem'>{icon} {level}</div>",
        unsafe_allow_html=True,
    )
    mismatch = (result.get("evidence_vector") or {}).get("intent_mechanism_mismatch")
    c3.metric("Intent-Mechanism Mismatch", "YES — +40 CRITICAL" if mismatch else "No")

    # Per-category breakdown (caps: url 50, upi 55, social 30)
    bd = result.get("score_breakdown")
    if bd:
        b1, b2, b3 = st.columns(3)
        b1.progress(min(1.0, bd.get("url", 0) / 50), text=f"url {bd.get('url', 0)}/50")
        b2.progress(min(1.0, bd.get("upi", 0) / 55), text=f"upi {bd.get('upi', 0)}/55")
        b3.progress(min(1.0, bd.get("social", 0) / 30), text=f"social {bd.get('social', 0)}/30")

    if result.get("language") == "hinglish":
        st.info("हिंग्लिश/हिंदी detect hua — explanation Hinglish me di gayi hai (see below).")

    if result.get("playbook"):
        st.subheader("🚨 Personalized Recovery Playbook")
        st.markdown(result["playbook"])
    elif result.get("explanation"):
        st.subheader("Explanation")
        st.info(result["explanation"])

    triggers = result.get("triggers") or []
    if not result.get("playbook"):
        st.subheader("Triggers")
        if triggers:
            for t in triggers:
                st.write(f"- {t}")
        else:
            st.write("- No strong indicators detected.")

    trace = result.get("trace_log") or []
    st.subheader("Agent Decision Trace")
    st.caption(f"{len(trace)} nodes executed — plan → act → observe → re-plan")
    for i, entry in enumerate(trace, 1):
        icon = NODE_ICONS.get(entry["node"], "•")
        decision = entry["decision"]
        cls = "vf-decision" if decision in BAD_DECISIONS else ""
        st.markdown(
            f"<div class='vf-trace'>{icon} <b>{i}. {entry['node']}</b> "
            f"&rarr; <span class='{cls}'>{decision}</span><br>"
            f"<small>{entry['detail']}</small></div>",
            unsafe_allow_html=True,
        )

    with st.expander("Evidence vector (raw) — show your work"):
        st.json(result.get("evidence_vector") or {})
        if result.get("score_breakdown"):
            st.caption(f"score_breakdown: {result['score_breakdown']}")


# ── Input form ──
with st.form("analyze_form"):
    text = st.text_area(
        "Message / text to analyze (or describe a scam that already happened)",
        placeholder="Paste the suspicious SMS, WhatsApp message, or UPI request here...",
        height=120,
    )
    qr_file = st.file_uploader("QR image (optional)", type=["png", "jpg", "jpeg", "webp"])
    submitted = st.form_submit_button("Analyze", type="primary")

if submitted and (text or qr_file):
    with st.spinner("Gathering evidence..."):
        payload = {"user_input": text or ""}
        if qr_file is not None:
            payload["qr_image"] = qr_file.getvalue()
        load_result(run_graph(payload))

# ── Pending question: clarify loop OR incident interview turn ──
if st.session_state.waiting_answer:
    result = st.session_state.last_result or {}
    is_incident = result.get("mode") == "INCIDENT"
    if is_incident:
        slots = result.get("incident_slots") or {}
        filled = " · ".join(f"**{k}**: {v}" for k, v in slots.items()) or "_none yet_"
        st.info(f"🎙️ **Incident interview** — answered so far: {filled}")
        label = f"Answer (question {len(slots) + 1}/4 — e.g. TXN7845123690, HDFC, 15000, or 'skip')"
    else:
        st.warning(f"🤔 **VeriFi asks:** {st.session_state.waiting_answer}")
        label = "Your answer (e.g. 'pay' or 'receive')"
    answer = st.text_input(label, key="answer_box")
    if st.button("Submit answer"):
        with st.spinner("Continuing..."):
            load_result(resume_graph(answer))
        st.rerun()

# ── Render (skip while interview question is pending — shown above) ──
if st.session_state.last_result and not st.session_state.waiting_answer:
    render_result(st.session_state.last_result)

# ── Fixture shortcuts (hermetic demo — no live network) ──
st.divider()
st.caption("Hermetic demo fixtures (no live network):")
cols = st.columns(4)

FIXTURES = {
    0: ("Fixture 1: Mismatch", "fixture_1_mismatch", True),
    1: ("Fixture 2: Lookalike", "fixture_2_lookalike", False),
    2: ("Fixture 3: Incident", "fixture_3_incident", False),
    3: ("Fixture 4: Legit", "fixture_4_legit", False),
}
for idx, (label, folder, has_qr) in FIXTURES.items():
    if cols[idx].button(label):
        payload = {"user_input": (FIX / folder / "message.txt").read_text(encoding="utf-8")}
        if has_qr:
            payload["qr_image"] = (FIX / folder / "qr.png").read_bytes()
        st.session_state.thread_id = str(uuid.uuid4())  # fresh thread per fixture
        load_result(run_graph(payload))
        st.rerun()
