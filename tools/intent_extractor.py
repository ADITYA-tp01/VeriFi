"""VeriFi Intent Extractor — narrative intent from text, with confidence (Plan Part 2).

LLM (Groq) is primary. If no API key / call fails, falls back to a deterministic
heuristic so the hermetic demo never dies. Returns {category, confidence}.
"""
from __future__ import annotations

import json
import os
import re

from dotenv import load_dotenv

load_dotenv()

RECEIVE_WORDS = [
    "receive", "receiv", "get", "getting", "cashback", "refund", "prize",
    "winner", "won", "credit", "credited", "paid to you", "money back",
    "refund mil", "paisa milega", "cashback milega",
]
SEND_WORDS = [
    "pay", "payment", "send", "debit", "scan to pay", "scan karo",
    "transfer", "recharge", "upgrade", "fee", "verify account",
    "pay now", "jaldi pay",
]

SYSTEM_PROMPT = """You classify the NARRATIVE INTENT of a message in an Indian UPI context.
Categories: RECEIVE_MONEY (message claims the user will GET money), SEND_MONEY (message asks the user to PAY), NEUTRAL.
Reply with ONLY a JSON object: {"category": "...", "confidence": 0.0-1.0}
Confidence = how sure you are of the narrative intent (not whether it's a scam)."""


def _heuristic_intent(text: str) -> dict:
    low = (text or "").lower()
    recv = sum(1 for w in RECEIVE_WORDS if w in low)
    send = sum(1 for w in SEND_WORDS if w in low)

    if recv > send:
        category, hits = "RECEIVE_MONEY", recv
    elif send > recv:
        category, hits = "SEND_MONEY", send
    else:
        category, hits = "NEUTRAL", 0

    if hits == 0:
        confidence = 0.4
    elif abs(recv - send) >= 2:
        confidence = 0.92
    elif recv == send and recv > 0:
        category, confidence = "NEUTRAL", 0.35  # conflicting cues -> low confidence
    else:
        confidence = 0.75
    return {"category": category, "confidence": round(confidence, 2), "source": "heuristic"}


def _llm_intent(text: str) -> dict | None:
    api_key = os.getenv("GROQ_API_KEY") or os.getenv("GROQ_API_KEY_BACKUP")
    if not api_key:
        return None
    try:
        from groq import Groq

        client = Groq(api_key=api_key)
        resp = client.chat.completions.create(
            model=os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile"),
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": text[:2000]},
            ],
            temperature=0,
            response_format={"type": "json_object"},
        )
        raw = resp.choices[0].message.content
        data = json.loads(raw)
        return {
            "category": str(data.get("category", "NEUTRAL")),
            "confidence": max(0.0, min(1.0, float(data.get("confidence", 0.5)))),
            "source": "llm",
        }
    except Exception:
        return None  # degrade to heuristic — never crash the demo


def extract_intent(text: str) -> dict:
    """Narrative intent + confidence. LLM first, heuristic fallback."""
    return _llm_intent(text) or _heuristic_intent(text)
