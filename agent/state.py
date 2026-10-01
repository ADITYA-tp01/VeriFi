"""VeriFi agent state — the shared LangGraph state (Plan Part 1)."""
from __future__ import annotations

from typing import Annotated, Any, TypedDict
from operator import add


class AgentState(TypedDict, total=False):
    # ── Input ──
    user_input: str                       # raw text from the user
    qr_image: Any                         # QR image path/bytes if uploaded
    mode: str                             # "ANALYZE" | "INCIDENT"

    # ── Evidence ──
    evidence_vector: dict                 # signals for the risk engine
    intent: dict                          # {category, confidence} from LLM
    mechanism: dict                       # {action, payload} from QR decode
    intent_mechanism_mismatch: bool       # the killer signal

    # ── Scoring ──
    score: int
    risk_level: str                       # CRITICAL | HIGH | SUSPICIOUS | NO_STRONG_INDICATORS
    triggers: list                        # human-readable trigger log

    # ── Agentic loop bookkeeping ──
    clarify_needed: bool                  # planner: intent ambiguous?
    clarify_question: str                 # question to ask the user
    clarify_answer: str                   # user's answer (fed back in)
    deep_scan_needed: bool                # planner: borderline + evidence gap
    deep_scan_performed: bool             # prevent infinite deep-scan loop
    missing_slots: list                   # evidence gaps the planner sees

    # ── Conversation / trace ──
    conversation: Annotated[list, add]    # full turn history
    trace_log: Annotated[list, add]       # agent decision trace (UI shows this)
    explanation: str                      # LLM's explanation of the math
    incident_slots: dict                  # txn_id, bank, amount, time (incident mode)
    playbook: str                         # personalized recovery steps


def append_trace(trace: list, node: str, decision: str, detail: str) -> list:
    """Helper: build a trace entry. Call as state update: {"trace_log": [...]}."""
    return trace + [{"node": node, "decision": decision, "detail": detail}]
