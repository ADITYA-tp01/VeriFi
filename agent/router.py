"""VeriFi Router Node — classifies input mode: ANALYZE vs INCIDENT (Plan Part 1)."""
from __future__ import annotations

import re

INCIDENT_PATTERNS = [
    r"\bi got scammed\b",
    r"\bgot cheated\b",
    r"\bmoney (was )?(deducted|stolen|debited)\b",
    r"\bfraud happened\b",
    r"\bscammed me\b",
    r"\bi (was )?(duped|tricked)\b",
    r"\blost (₹|rs\.?|rupees?)",
    r"\bunauthorized (transaction|debit|payment)\b",
    r"\bcyber (crime|fraud)\b",
    r"\bhow do i (recover|get my money back)\b",
    r"\brefund my money\b",
]


def classify_mode(user_input: str) -> str:
    """Return "INCIDENT" if the user reports a past scam, else "ANALYZE"."""
    text = (user_input or "").lower()
    for pattern in INCIDENT_PATTERNS:
        if re.search(pattern, text):
            return "INCIDENT"
    return "ANALYZE"


def router_node(state: dict) -> dict:
    """LangGraph node: set mode from user input."""
    mode = classify_mode(state.get("user_input", ""))
    return {
        "mode": mode,
        "trace_log": [
            {
                "node": "router",
                "decision": mode,
                "detail": f"Input classified as {mode} mode",
            }
        ],
    }
