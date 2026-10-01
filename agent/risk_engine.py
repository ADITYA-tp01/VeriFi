"""VeriFi Risk Engine v3 — deterministic, category-capped scoring (Plan Part 3).

The LLM NEVER overrides this score. It explains, asks, and plans — this engine decides.
"""
from __future__ import annotations

CAPS = {"url": 50, "upi": 55, "social": 30}  # per-category ceilings


def calculate_risk_score(ev: dict) -> tuple[int, str, list]:
    """Score an evidence vector.

    Returns (score, level, triggers) where triggers is a human-readable log
    of applied points, tagging capped applications with [capped].
    """
    cat = {"url": 0, "upi": 0, "social": 0}
    triggers = []

    def add(category: str, points: int, reason: str) -> None:
        before = cat[category]
        cat[category] = min(CAPS[category], cat[category] + points)
        applied = cat[category] - before
        if applied > 0:
            triggers.append(
                f"+{applied} {reason}" + (" [capped]" if applied < points else "")
            )

    # ── URL signals (cap 50) ──
    if ev.get("is_known_malicious"):
        add("url", 50, "Known malicious domain")
    if ev.get("brand_mismatch"):
        add("url", 25, "Brand impersonation (text says 'SBI', domain isn't)")
    if ev.get("is_punycode_or_lookalike"):
        add("url", 30, "Lookalike/punycode domain")
    domain_age = ev.get("domain_age_days", 999)
    if domain_age is not None and domain_age < 30:
        add("url", 20, f"Domain {domain_age}d old")

    # ── UPI / QR signals (cap 55) ──
    if ev.get("intent_mechanism_mismatch"):
        add("upi", 40, "CRITICAL: claims RECEIVE, QR actually DEBITS")
    if ev.get("is_upi_collection_request"):
        add("upi", 15, "UPI collection request")

    # ── Social engineering (cap 30) ──
    if ev.get("has_urgency_threats"):
        add("social", 15, "Urgency/threat language")
    if ev.get("requests_sensitive_info"):
        add("social", 20, "Requests OTP/PIN/credentials")

    score = sum(cat.values())  # max 135
    if score >= 75:
        level = "CRITICAL"
    elif score >= 50:
        level = "HIGH"
    elif score >= 25:
        level = "SUSPICIOUS"
    else:
        level = "NO_STRONG_INDICATORS"  # NEVER "safe"
    return score, level, triggers
