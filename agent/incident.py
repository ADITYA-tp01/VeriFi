"""VeriFi Incident Interview + Playbook Generator (Plan Part 1, Loop 3).

Multi-turn slot-filling — ONE question per turn, memory across turns via the
LangGraph MemorySaver checkpointer. The playbook is personalized from the
victim's answers — never a static dump.
"""
from __future__ import annotations

# Order per plan: txn ID -> bank -> amount -> time
INCIDENT_QUESTIONS: list[tuple[str, str]] = [
    (
        "txn_id",
        "First — what is the transaction ID or UPI reference number of the "
        "fraudulent payment? (reply **skip** if you don't know it)",
    ),
    (
        "bank",
        "Which bank account was the money debited from? (e.g. HDFC, SBI, ICICI)",
    ),
    (
        "amount",
        "How much money was lost? (in rupees, e.g. 15000)",
    ),
    (
        "time",
        "When did this happen? (date and rough time, e.g. '30 Sep, 2:30 PM')",
    ),
]

SKIP_TOKENS = {"skip", "don't know", "dont know", "do not know", "unknown", "no", "na", "-"}


def normalize_answer(raw) -> str:
    """Store the answer, or 'unknown' if skipped/empty."""
    text = str(raw or "").strip()
    if not text or text.lower() in SKIP_TOKENS:
        return "unknown"
    return text


def next_open_slot(slots: dict) -> tuple[str, str] | None:
    """Return (key, question) for the first unfilled slot, or None if done."""
    for key, question in INCIDENT_QUESTIONS:
        if key not in slots:
            return key, question
    return None


def build_playbook(slots: dict) -> str:
    """Personalized recovery playbook from the victim's own answers (Plan Part 1)."""
    txn = slots.get("txn_id", "unknown")
    bank = slots.get("bank", "your bank")
    amount = slots.get("amount", "the lost amount")
    when = slots.get("time", "the time of the transaction")

    amount_str = f"Rs.{amount}" if amount != "unknown" else "the amount you remember"
    when_str = when if when != "unknown" else "the time you remember"
    lines = [
        f"### Recovery Playbook — {bank}",
        "",
        "**1. Call 1930 RIGHT NOW** (Government cyber-fraud helpline, 24x7). "
        f"Tell them: txn ID `{txn}`, {amount_str} debited from **{bank}**, around {when_str}. "
        "Ask them to flag it for recall — the first hours matter most.",
        "",
        "**2. File a complaint at cybercrime.gov.in** — Log in → Report Suspicious Activity → "
        f"Financial Fraud. Use the same details (`{txn}`, {bank}, {amount_str}, {when_str}) "
        "and upload any screenshots. Save the complaint token number.",
        "",
        f"**3. Call {bank}'s official fraud desk** (find the number in your bank's app or "
        f"on the back of your card — never from the scam message). Request a chargeback / "
        f"recall for transaction `{txn}`. Banks must respond to such reports promptly; "
        "escalate to the branch manager if the first agent doesn't act.",
        "",
        "**4. Secure your account NOW:** change your UPI PIN and net-banking password "
        "from the official app, and block/reissue your card if card details were shared.",
        "",
        "**5. Preserve evidence:** do NOT delete the message, QR image, call recording, "
        "or SMS. Screenshots strengthen your cybercrime.gov.in complaint.",
        "",
        "**6. Ignore 'recovery agents':** anyone who calls promising to return your money "
        "for a fee is running a follow-up scam. Official channels never charge for recovery.",
    ]

    unknown_slots = [k for k, v in slots.items() if v == "unknown"]
    if unknown_slots:
        lines.insert(
            2,
            f"_Note: {', '.join(unknown_slots)} could not be provided — "
            "share whatever you remember; 1930 can look up the transaction by your "
            "phone number and time window._\n",
        )
    return "\n".join(lines)
