# 🛡️ VeriFi — Evidence-Driven Financial Safety Agent

**Bharat Agentic 2026 | v3.0** — detect UPI/QR scams with deterministic evidence scoring, three genuine agentic loops, and an LLM that *explains the math but never overrides it*.

---

## The Insight: Intent ≠ Mechanism

UPI fraud is **contextual manipulation — the QR lies.**
"Scan to receive ₹5000 cashback" → the *narrative* says RECEIVE. The QR payload `upi://pay?pa=...` → the *mechanism* actually DEBITS you.

VeriFi extracts both and compares them. A mismatch is **direct evidence of deception**, not a suspicious vibe — so it carries the engine's highest single weight: **+40**.

---

## Architecture

```text
                    ┌──────────────────────────────────────────────┐
                    │              LANGGRAPH STATE                  │
                    │  evidence_vector · intent · mechanism · score │
                    │  trace_log · conversation · missing_slots     │
                    └──────────────────────────────────────────────┘
                                      │
        USER INPUT (Text / QR Image / URL / "I got scammed")
                                      │
                                      ▼
                           [ ROUTER NODE ]
                           ANALYZE vs INCIDENT
                               │        │
               ┌───────────────┘        └────────────────┐
               ▼                                          ▼
    [ PARALLEL EVIDENCE TOOLS ]                [ INCIDENT INTERVIEW ]
     T1 URL Intel · T2 QR Decode                 Multi-turn slot-filling
     T3 Scam Taxonomy KB                         one question per turn
               │                                 (Tier 2, checkpointer)
               ▼                                          │
    [ DETERMINISTIC RISK ENGINE ]                         ▼
     Category-capped scoring                    [ PLAYBOOK GENERATOR ]
               │                                 1930 / bank / cybercrime.gov.in
               ▼
    [ AGENT PLANNER NODE ]  ◄── THE BRAIN
     ├─► Intent ambiguous?   ──► [ CLARIFY NODE ]    ── asks user ──► loop back
     ├─► Score 25–74 + gap?  ──► [ DEEP SCAN NODE ]  ── re-score ──► loop back
     └─► Confident?          ──► [ EXPLAINER NODE ]  ── LLM explains THE MATH
                                          │
                                          ▼
                     Streamlit UI + live Agent Decision Trace
```

### The three loops (what makes it *agentic*, not a wrapper)
1. **Clarify:** intent confidence < 0.7 → the agent *stops and asks* "pay or receive?", then re-plans with the answer.
2. **Deep scan:** borderline score (25–74) + evidence gap → the agent *autonomously* runs deeper tools, re-scores, re-plans.
3. **Incident interview (Tier 2):** victim is interviewed one question at a time; the recovery playbook is personalized from their answers. Memory via LangGraph `MemorySaver`.

---

## Risk Engine v3 — Category-Capped & Defensible

| Category (cap) | Signal | Points |
|---|---|---|
| url (50) | Known malicious domain | +50 |
| url | Brand impersonation | +25 |
| url | Lookalike/punycode domain | +30 |
| url | Domain < 30 days old | +20 |
| upi (55) | **Intent-mechanism mismatch** | **+40** |
| upi | UPI collection request | +15 |
| social (30) | Urgency/threat language | +15 |
| social | Requests OTP/PIN/credentials | +20 |

Thresholds: **≥75 CRITICAL · ≥50 HIGH · ≥25 SUSPICIOUS · else NO_STRONG_INDICATORS** (never "safe"). Max 135.

### Why these weights
> *Weights encode evidentiary strength, not vibes. The Intent-Mechanism Mismatch (40) is weighted highest because it is direct proof of deception — the mechanism contradicts the narrative. Known-malicious domains (50) are ground truth. Social-engineering signals are capped lowest (30) because urgency alone has legitimate uses (banks really do send KYC reminders). Category caps prevent correlated signals — punycode, brand mismatch and domain age often describe one underlying fact — from triple-counting. Thresholds were tuned on our 30-scenario benchmark to maximize recall on scam cases while keeping false positives on legitimate UPI requests at zero.*

---

## Setup

```bash
pip install -r requirements.txt     # opencv-python-headless — NOT pyzbar
cp .env.example .env                # add your Groq key (optional; heuristic fallback exists)
python scripts/make_fixtures.py     # regenerate hermetic fixtures
streamlit run app.py
```

**Tests (hermetic — no network, no LLM):**
```bash
python -m pytest tests/ -q
python tests/run_eval.py            # 30-scenario benchmark -> tests/eval_results.json
```

---

## Evaluation Benchmark

`tests/eval_set.json` — **30 scenarios**: 15 scam (KYC fraud, digital arrest, fake-buyer QR, task scam, OTP theft, customs scam…), 10 legitimate (real UPI pays, bank SMS, friend transfers), 5 edge (Hinglish scam, ambiguous intent → clarify loop, punycode lookalike).

**Measured results** (see `tests/eval_results.json` — we publish only what we measure):

```
Eval: 15/15 scams HIGH/CRITICAL, 0 false positives on legit transfers,
clarify-loop fired on 3/3 expected cases
```

---

## Hermetic Demo Rule

**No demo input ever touches a live network call.** Tools check `data/fixtures/cached_api/` first; live APIs only run behind `LIVE=1`. API failure → `{"status": "UNVERIFIED"}`, logged in trace, app never crashes.

---

## Project Structure

```
agent/            graph.py (nodes + conditional edges), risk_engine.py, state.py,
                  router.py, mismatch.py
tools/            qr_decoder.py, url_intel.py, intent_extractor.py
data/fixtures/    4 fixture packs + cached_api/ (WHOIS & urlscan JSONs)
data/             scam_taxonomy.json (10 patterns -> 20+ in Tier 2)
tests/            test_tier1_gate.py, eval_set.json (30), run_eval.py
scripts/          make_fixtures.py, demo_fixture1.py
Docs/             plan, phases, video script, deck skeleton
```

---

## Directives We Build By

1. Mismatch is Tier 1 — non-negotiable.
2. **The LLM never overrides the score.** It explains, asks, and plans — the engine decides.
3. No live API in a demo fixture.
4. Never say "safe." Say **"no strong indicators detected."**

---

## Future Work
- Taxonomy as a living, community-fed dataset
- WhatsApp bot delivery channel
- Bank API integration for real-time txn verification
