"""VeriFi Intent-Mechanism Mismatch Engine — THE KILLER FEATURE (Plan Part 2, Tier 1).

Narrative intent (LLM) vs mechanism (deterministic QR payload).
RECEIVE != SEND -> +40 (direct evidence of deception — the mechanism contradicts the narrative).
If intent confidence < 0.7 -> the agent must ask the user (clarify loop), never guess.
"""
from __future__ import annotations

# Map mechanism actions onto the intent vocabulary so we can compare like-for-like
MECHANISM_TO_INTENT = {
    "SEND_MONEY": "SEND_MONEY",       # scanning this QR debits the scanner
    "REQUEST_MONEY": "RECEIVE_MONEY",  # a collect request wants to receive from us
}

CLARIFY_THRESHOLD = 0.7


def detect_mismatch(intent: dict, mechanism: dict) -> dict:
    """Compare narrative intent against what the QR actually does.

    Returns {
      "mismatch": bool,
      "clarify_needed": bool,
      "clarify_question": str,
      "detail": str,
    }
    """
    intent_cat = (intent or {}).get("category", "NEUTRAL")
    confidence = float((intent or {}).get("confidence", 0.0))
    mech_action = (mechanism or {}).get("action", "UNKNOWN")
    has_mechanism = bool((mechanism or {}).get("payload"))

    # Clarify fires when the narrative is uncertain AND something is at stake:
    # either the LLM produced a category it's unsure about, or there is a QR
    # mechanism whose verdict depends on knowing the narrative. (Plan Part 2.)
    clarify_needed = confidence < CLARIFY_THRESHOLD and (
        intent_cat != "NEUTRAL" or has_mechanism
    )
    clarify_question = (
        "Is this message asking you to **pay** money or **receive** money?"
    )

    # Can't compare NEUTRAL/UNKNOWN — no mismatch claim possible
    if intent_cat == "NEUTRAL" or mech_action in ("UNKNOWN", "LINK"):
        return {
            "mismatch": False,
            "clarify_needed": clarify_needed,
            "clarify_question": clarify_question if clarify_needed else "",
            "detail": (
                f"intent={intent_cat} (conf {confidence:.2f}), "
                f"mechanism={mech_action} — no comparison possible"
            ),
        }

    mech_as_intent = MECHANISM_TO_INTENT.get(mech_action, mech_action)
    mismatch = mech_as_intent != intent_cat

    detail = (
        f"intent={intent_cat} (conf {confidence:.2f}) vs "
        f"mechanism={mech_action}"
        + (" — MISMATCH (+40)" if mismatch else " — consistent")
    )
    if mismatch:
        clarify_question = (
            "This QR appears to ask you to PAY, but the message says you will "
            "RECEIVE money. Can you confirm — are you being asked to pay or receive?"
        )

    return {
        "mismatch": mismatch,
        "clarify_needed": clarify_needed,
        "clarify_question": clarify_question if clarify_needed else "",
        "detail": detail,
    }
