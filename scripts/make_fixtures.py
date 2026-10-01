"""Generate hermetic fixture files (Plan Part 4). Run: python scripts/make_fixtures.py"""
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from tools.qr_decoder import generate_qr  # noqa: E402

FIX = ROOT / "data" / "fixtures"
CACHED = FIX / "cached_api"


def write(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def write_json(path: Path, obj: dict) -> None:
    write(path, json.dumps(obj, indent=2, ensure_ascii=False))


# ════════════ Fixture 1: Intent-Mechanism Mismatch (the money-shot) ════════════
f1 = FIX / "fixture_1_mismatch"
generate_qr("upi://pay?pa=scammer@okicici&am=5000&tn=Cashback", str(f1 / "qr.png"))

write(
    f1 / "message.txt",
    "From SBI: Scan this QR to receive Rs.5000 cashback. "
    "Verify immediately at https://sbi-kyc-verify.com or your account "
    "will be blocked within 24 hours.",
)
write_json(
    f1 / "expected.json",
    {
        "intent": "RECEIVE_MONEY",
        "mechanism": "SEND_MONEY",
        "mismatch": True,
        "expected_trigger": "+40 CRITICAL: claims RECEIVE, QR actually DEBITS",
        "expected_level": "CRITICAL",
        "min_score": 75,
        "clarify_fires": False,
    },
)

# ════════════ Fixture 2: Lookalike domain (cached WHOIS — no network) ════════════
f2 = FIX / "fixture_2_lookalike"
write(
    f2 / "message.txt",
    "HDFC Bank: Update your KYC immediately at https://hdfc-kyc-update.in "
    "or account will be suspended today.",
)
write_json(
    f2 / "expected.json",
    {
        "mode": "ANALYZE",
        "expected_level": ["HIGH"],
        "signals": ["brand_mismatch", "is_punycode_or_lookalike"],
        "domain_age_days": 5,
        "clarify_fires": False,
    },
)

# ════════════ Fixture 3: Incident interview (Tier 2 slot-filling) ════════════
f3 = FIX / "fixture_3_incident"
write(
    f3 / "message.txt",
    "I got scammed yesterday - Rs.15000 was deducted from my HDFC account "
    "after a fake bank officer called me.",
)
write_json(
    f3 / "interview_answers.json",
    {
        "txn_id": "TXN7845123690",
        "bank": "HDFC Bank",
        "amount": "15000",
        "time": "2026-09-30 14:32 IST",
        "channel": "UPI (vishing - fake bank officer)",
        "notes": "Victim shared OTP during the call",
    },
)
write_json(
    f3 / "expected.json",
    {
        "mode": "INCIDENT",
        "slots": ["txn_id", "bank", "amount", "time"],
        "playbook_terms": ["1930", "cybercrime.gov.in"],
        "personalized": True,
    },
)

# ════════════ Fixture 4: Legit UPI (zero false positives) ════════════
f4 = FIX / "fixture_4_legit"
write(
    f4 / "message.txt",
    "Payment received! Rahul sent you Rs. 500 for movie tickets. "
    "UPI Ref: 412365897452. Your HDFC Bank a/c XX4821 is updated.",
)
write_json(
    f4 / "expected.json",
    {
        "mode": "ANALYZE",
        "expected_level": "NO_STRONG_INDICATORS",
        "max_score": 24,
        "clarify_fires": False,
        "intent": "RECEIVE_MONEY",
    },
)

# ════════════ Cached API responses (hermetic — checked FIRST, always) ════════════
WHOIS_CACHE = {
    # fixture 1 + eval
    "sbi-kyc-verify.com": {"age": 3, "malicious": False},
    # fixture 2 + eval
    "hdfc-kyc-update.in": {"age": 5, "malicious": False},
    # eval scam domains
    "cyber-cell-release.in": {"age": 2, "malicious": True},
    "verify-upi.in": {"age": 8, "malicious": True},
    "customs-clearance.in": {"age": 4, "malicious": True},
    "loan-approval-app.com": {"age": 6, "malicious": True},
    "sbi-notice-verify.com": {"age": 6, "malicious": False},
    "help-me-return.com": {"age": 9, "malicious": True},
    "hdfc-secure-login.in": {"age": 7, "malicious": False},
    "upi-collect-info.com": {"age": 5, "malicious": True},
    "diwali-fund.org": {"age": 12, "malicious": True},
    "bijli-bill-pay.in": {"age": 3, "malicious": True},
    "sim-reverify.com": {"age": 4, "malicious": True},
    "daily-earn-app.com": {"age": 5, "malicious": True},
    "xn--sbi-verify-9cb.com": {"age": 12, "malicious": False},
    # eval legit domain (official)
    "hdfcbank.com": {"age": 4000, "malicious": False},
}

for domain, meta in WHOIS_CACHE.items():
    write_json(
        CACHED / f"whois_{domain}.json",
        {
            "status": "OK",
            "domain": domain,
            "domain_age_days": meta["age"],
            "is_known_malicious": meta["malicious"],
        },
    )

# urlscan cache (Tier 3 consumes this — cached at pre-flight so demo never hits network)
write_json(
    CACHED / "urlscan_sbi-kyc-verify.com.json",
    {
        "page": {"url": "https://sbi-kyc-verify.com", "status": 200},
        "verdicts": {"overall": {"score": 100, "malicious": True}},
        "lists": {"categories": ["phishing"]},
        "_comment": "cached at pre-flight; live urlscan only behind --live (Tier 3)",
    },
)

print("Fixtures generated:")
for p in sorted(FIX.rglob("*")):
    if p.is_file():
        print("  ", p.relative_to(ROOT))
