"""VeriFi — Evidence-Driven Financial Safety Agent. Run: streamlit run app.py"""
from __future__ import annotations

import json
import uuid
from pathlib import Path

import streamlit as st
from langgraph.types import Command

from agent.graph import app

st.set_page_config(page_title="VeriFi", page_icon="🛡️", layout="wide")

FIX = Path(__file__).resolve().parent / "data" / "fixtures"

LEVEL_COLORS = {
    "CRITICAL": "🔴",
    "HIGH": "🟠",
    "SUSPICIOUS": "🟡",
    "NO_STRONG_INDICATORS": "🟢",
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


def render_result(result: dict):
    score = result.get("score", 0)
    level = result.get("risk_level", "NO_STRONG_INDICATORS")
    icon = LEVEL_COLORS.get(level, "⚪")

    c1, c2, c3 = st.columns([1, 1, 2])
    c1.metric("Score", f"{score}/135")
    c2.metric("Level", f"{icon} {level}")
    mismatch = (result.get("evidence_vector") or {}).get("intent_mechanism_mismatch")
    c3.metric("Intent-Mechanism Mismatch", "YES — +40 CRITICAL" if mismatch else "No")

    if result.get("explanation"):
        st.subheader("Explanation")
        st.info(result["explanation"])

    triggers = result.get("triggers") or []
    st.subheader("Triggers")
    if triggers:
        for t in triggers:
            st.write(f"- {t}")
    else:
        st.write("- No strong indicators detected.")

    st.subheader("Agent Decision Trace")
    for i, entry in enumerate(result.get("trace_log") or [], 1):
        st.markdown(
            f"**{i}. `{entry['node']}`** → **{entry['decision']}**  \n"
            f"<small>{entry['detail']}</small>",
            unsafe_allow_html=True,
        )


# ── Input form ──
with st.form("analyze_form"):
    text = st.text_area(
        "Message / text to analyze",
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
        result = run_graph(payload)
    st.session_state.last_result = result

    interrupts = result.get("__interrupt__")
    if interrupts:
        st.session_state.waiting_answer = interrupts[0].value
    else:
        st.session_state.waiting_answer = None

# ── Clarify loop: agent asked a question ──
if st.session_state.waiting_answer:
    st.warning(f"🤔 **VeriFi asks:** {st.session_state.waiting_answer}")
    answer = st.text_input("Your answer (e.g. 'pay' or 'receive')", key="answer_box")
    if st.button("Submit answer"):
        with st.spinner("Re-planning..."):
            result = resume_graph(answer)
        st.session_state.last_result = result
        interrupts = result.get("__interrupt__")
        st.session_state.waiting_answer = interrupts[0].value if interrupts else None
        st.rerun()

# ── Render ──
if st.session_state.last_result:
    render_result(st.session_state.last_result)

# ── Fixture shortcuts (hermetic demo) ──
st.divider()
st.caption("Hermetic demo fixtures (no live network):")
cols = st.columns(4)
if cols[0].button("Load Fixture 1: Mismatch"):
    msg = (FIX / "fixture_1_mismatch" / "message.txt").read_text(encoding="utf-8")
    qr = (FIX / "fixture_1_mismatch" / "qr.png").read_bytes()
    st.session_state.thread_id = str(uuid.uuid4())  # fresh thread per fixture
    st.session_state.last_result = run_graph({"user_input": msg, "qr_image": qr})
    st.session_state.waiting_answer = None
    st.rerun()
if cols[1].button("Load Fixture 2: Lookalike"):
    msg = (FIX / "fixture_2_lookalike" / "message.txt").read_text(encoding="utf-8")
    st.session_state.thread_id = str(uuid.uuid4())
    st.session_state.last_result = run_graph({"user_input": msg})
    st.session_state.waiting_answer = None
    st.rerun()
