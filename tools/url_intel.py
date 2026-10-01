"""VeriFi URL Intel — cache-first WHOIS/domain/brand checks (Plan Part 4).

Hermetic rule: cached_api/ is checked FIRST. Cache miss → live call ONLY if
LIVE=1. Otherwise returns UNVERIFIED — the app never crashes, never touches
the network during a demo fixture.
"""
from __future__ import annotations

import json
import os
import re
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()

CACHE_DIR = Path(__file__).resolve().parent.parent / "data" / "fixtures" / "cached_api"

# Brand registry seed — tokens for matching + OFFICIAL domains (Qwen expands in Tier 2)
BRAND_TOKENS = {
    "sbi": ["sbi", "state bank"],
    "hdfc": ["hdfc"],
    "icici": ["icici"],
    "axis": ["axis"],
    "paytm": ["paytm"],
    "phonepe": ["phonepe", "phone pay"],
    "gpay": ["gpay", "google pay"],
}

OFFICIAL_DOMAINS = {
    "sbi": ["sbi.co.in", "onlinesbi.com", "yono.co.in"],
    "hdfc": ["hdfcbank.com"],
    "icici": ["icicibank.com"],
    "axis": ["axisbank.com"],
    "paytm": ["paytm.com"],
    "phonepe": ["phonepe.com"],
    "gpay": ["pay.google.com", "googlepay.com"],
}


def _live_enabled() -> bool:
    return os.getenv("LIVE", "0") == "1"


def _extract_domain(url: str) -> str:
    url = url.strip()
    url = re.sub(r"^https?://", "", url, flags=re.I)
    domain = url.split("/")[0].split("?")[0].lower()
    if domain.startswith("www."):
        domain = domain[4:]
    return domain


def _cache_lookup(domain: str) -> dict | None:
    if not CACHE_DIR.exists():
        return None
    for f in CACHE_DIR.glob("*.json"):
        if domain in f.name:
            try:
                return json.loads(f.read_text(encoding="utf-8"))
            except (json.JSONDecodeError, OSError):
                continue
    return None


def _live_whois(domain: str) -> dict:
    """Live WHOIS lookup — only reachable when LIVE=1."""
    try:
        import socket

        creation = socket.getaddrinfo(domain, None)  # existence check only
        del creation
        return {"status": "OK", "domain_age_days": None, "live": True}
    except OSError:
        return {"status": "UNVERIFIED", "reason": f"domain {domain} does not resolve"}


def _is_official(domain: str, brand_key: str) -> bool:
    """True if the domain is the brand's genuine registered domain."""
    official = OFFICIAL_DOMAINS.get(brand_key, [])
    return any(domain == d or domain.endswith("." + d) for d in official)


def _is_punycode_or_lookalike(domain: str, claimed_brand: str | None) -> bool:
    if "xn--" in domain:
        return True
    if not claimed_brand:
        return False
    brand_key = claimed_brand.lower()
    if _is_official(domain, brand_key):
        return False
    # Non-official domain that embeds the brand token = lookalike
    return any(t in domain for t in BRAND_TOKENS.get(brand_key, [brand_key]))


def check_brand_mismatch(url: str, claimed_brand: str | None) -> bool:
    """True if the message claims a brand but the domain isn't the official one."""
    if not claimed_brand:
        return False
    domain = _extract_domain(url)
    return not _is_official(domain, claimed_brand.lower())


def get_url_intel(url: str, claimed_brand: str | None = None) -> dict:
    """Return evidence fields for the risk engine, cache-first."""
    domain = _extract_domain(url)

    cached = _cache_lookup(domain)
    if cached is not None:
        evidence = dict(cached)
        evidence["source"] = f"cache:{domain}"
    elif _live_enabled():
        evidence = _live_whois(domain)
        evidence["source"] = "live"
    else:
        # Graceful degradation — never crash, never hit network in a demo
        evidence = {
            "status": "UNVERIFIED",
            "reason": f"no cache for {domain} and LIVE!=1",
            "source": "none",
            "domain_age_days": 999,
        }

    evidence["domain"] = domain
    evidence.setdefault("domain_age_days", 999)
    evidence["is_known_malicious"] = bool(evidence.get("is_known_malicious", False))
    evidence["brand_mismatch"] = check_brand_mismatch(url, claimed_brand)
    evidence["is_punycode_or_lookalike"] = _is_punycode_or_lookalike(
        domain, claimed_brand
    )
    return evidence
