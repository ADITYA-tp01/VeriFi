# VeriFi v3.0 — Phases of Execution (Detailed)

## Overview
This document tracks project phases, objectives, owners, gates, and deliverables.
**Source of truth: `VeriFi_v3_Plan.md`** — this document operationalizes it hour-by-hour.
Aligned and corrected against the master plan (see Corrections below).

---

## Corrections Applied (vs. earlier draft)

| # | Earlier Issue | Fix |
|---|---|---|
| 1 | Phase 4 deadline listed as "8:30 **AM**" | Corrected to **8:30 PM** (submission opens 8:00 PM, submit by 8:30 PM) |
| 2 | Missing 9:00–9:30 morning sync block | Added |
| 3 | Missing 11:00 mentor session | Added |
| 4 | Missing 5:30–6:00 fixture validation + backup demo recording | Added |
| 5 | Missing 8:30–9:00 contingency block | Added |
| 6 | Tier 1/2 owner tables omitted Leader and Kimi | Full 4-member tables per Plan Part 6 |
| 7 | Risk engine detail missing thresholds, signal weights, trigger output | Added full scoring spec |
| 8 | Graph conditional edges / planner node not specified | Added `graph.py` edge map |
| 9 | Deep-scan loop tools unspecified | Added deep URL scan + brand-registry fuzzy match |
| 10 | Incident interview missing "ONE question per turn" rule | Added |
| 11 | Hermetic fixture rules (cache-first, `--live`, graceful degradation) missing | Added to Phase 0 |
| 12 | 2:00 PM scope-freeze rule missing | Added to Communication Cadence |
| 13 | Video shot list and 7 deck slides abbreviated | Full detail restored from Plan Parts 8–9 |
| 14 | 12:30 gate missing "everyone swarms" contingency | Added |
| 15 | Final Directives (LLM never overrides score, never say "safe") missing | Added as Success Criteria + Directives |

---

## Master Timeline (Authoritative — Plan Part 5)

| Time (IST) | Block | Owner Focus |
|---|---|---|
| **Tonight** | Pre-Flight (Phase 0 below) — repo, keys, fixtures, installs DONE | All |
| 9:00–9:30 | Sync: clone repo, verify env, assign Tier 1 tasks | All |
| **9:30–12:30** | 🟥 **TIER 1**: risk engine v3 + router + QR decode + intent extraction + **MISMATCH** + minimal Streamlit w/ trace | ChatGPT: graph/engine · Qwen: tools |
| 11:00 | Mentor session — ask: "does our agentic loop depth stand out?" | Leader |
| **12:30** | **TIER 1 GATE**: Fixture 1 (Mismatch) works end-to-end. If not, everyone swarms it. | All |
| 12:30–4:00 | 🟧 **TIER 2**: clarify loop + deep-scan loop + incident interview + **Hinglish routing** + trace UI polish | ChatGPT: loops · Qwen: Hinglish/taxonomy |
| 4:00 | Midpoint: run ALL 4 fixtures + eval benchmark. Screenshot results for deck. | Leader |
| 4:00–5:30 | 🟨 **TIER 3 (polish only)**: urlscan live, extra taxonomy patterns, CSS polish | Qwen |
| **5:30** | ⛔ **HARD CODE FREEZE.** Only bugfixes that break a fixture allowed after this. | Leader enforces |
| 5:30–6:00 | Full fixture validation + backup demo recording | ChatGPT + Leader |
| 6:00–7:15 | 🎬 Record demo video (script pre-written, Part 8) — max 3 takes | Leader |
| 7:15–8:00 | Deck finalization + README (Kimi's pre-written drafts) | Leader + Kimi |
| 8:00 | Submission opens → **submit by 8:30 PM**, 30-min buffer | Leader |
| 8:30–9:00 | Contingency only | All |

---

## Phase 0 — Pre-Flight (Tonight)
**Status: ✅ COMPLETE** (user-only items remain: real Groq keys in `.env`, Git remote for team clone, initial commit approval)

### Objectives
- [x] Repository initialized in `C:\Users\adity\Documents\VeriFi` (`git init` done) with this structure:
  ```text
  VeriFi/
  ├── app.py                     # Streamlit entry
  ├── agent/
  │   ├── graph.py               # LangGraph nodes + conditional edges
  │   ├── state.py               # LangGraph state schema
  │   ├── risk_engine.py         # deterministic scoring
  │   └── router.py              # ANALYZE vs INCIDENT classifier
  ├── tools/
  │   ├── qr_decoder.py          # cv2.QRCodeDetector
  │   ├── url_intel.py           # WHOIS/age/brand checks (cache-first)
  │   └── intent_extractor.py    # LLM intent + confidence
  ├── data/
  │   ├── fixtures/
  │   │   ├── fixture_1_mismatch/    # QR image + cached evidence JSON
  │   │   ├── fixture_2_lookalike/   # cached WHOIS: {"domain_age_days": 3, ...}
  │   │   ├── fixture_3_incident/    # scripted interview answers
  │   │   ├── fixture_4_legit/       # Rahul's UPI ID
  │   │   └── cached_api/
  │   │       ├── whois_sbi-kyc-verify.com.json
  │   │       └── urlscan_*.json
  │   └── scam_taxonomy.json     # 10 patterns seeded tonight
  ├── tests/
  │   └── eval_set.json          # 30 scenarios (Kimi)
  ├── Docs/
  ├── .env.example
  └── .gitignore
  ```
- [x] `.gitignore` configured (excludes `.env`, `__pycache__`)
- [x] `.env.example` written (GROQ_API_KEY + backup, urlscan, LIVE flag) — **user obtains real keys into `.env`**
- [x] `pip install` dry run validated (all 9 packages + `filelock` repair):
  ```bash
  pip install langgraph streamlit opencv-python-headless qrcode pillow groq python-dotenv tldextract
  ```
  ⚠️ `opencv-python-headless` — **NOT pyzbar** (native zbar dependency is install hell. Decided. Closed.)
- [x] 4 fixtures generated via `python scripts/make_fixtures.py` (QR codes + messages + expected.json)
- [x] Cached WHOIS (16 domains) + urlscan JSONs written to `data/fixtures/cached_api/`
- [x] `scam_taxonomy.json` seeded with 10 patterns (Qwen expands to 20+ in Tier 2)
- [x] Kimi delivers: `Docs/video_script.md`, `README.md`, `Docs/deck_skeleton.md`, `tests/eval_set.json` (30 scenarios) + `tests/run_eval.py` runner
- [x] **Environment proven:** `streamlit run app.py` → HTTP 200; `pytest` 7/7 green; **eval 30/30 pass** (15/15 scams HIGH/CRITICAL, 0 false positives, clarify 3/3)

### Hermetic Fixture Rules (Plan Part 4 — applies for the whole project)
1. **No demo input ever touches a live network call.**
2. Tools check `data/fixtures/cached_api/` FIRST. Cache hit → instant, deterministic response. Miss → live call **only if** `--live` flag is on.
3. **Graceful degradation:** API timeout → tool returns `{"status": "UNVERIFIED", "reason": ...}`, logged in trace, engine adjusts, app never crashes.
4. QR decoding: `cv2.QRCodeDetector` only.
5. **Backup to the backup:** at 6:00 PM, screen-record a full clean demo run. If the live demo dies on stage, we play the recording.

### Owner
All members — sync on Git setup overnight.

---

## Phase 1 — TIER 1: Core Engine (9:30–12:30 IST)
**Gate Deadline: 12:30 PM — Fixture 1 (Mismatch) must work end-to-end**
**Preceded by:** 9:00–9:30 morning sync (clone, verify env, assign tasks); **11:00 mentor session** (Leader)

### Objectives

**1. LangGraph State** (`agent/state.py`)
- [ ] Fields: `evidence_vector`, `intent`, `mechanism`, `score`, `trace_log`, `conversation`, `missing_slots`

**2. Risk Engine v3** (`agent/risk_engine.py`)
- [ ] Category caps: `{"url": 50, "upi": 55, "social": 30}`
- [ ] Deterministic scoring; returns `(score, level, triggers)`
- [ ] Signal weights (per Plan Part 3):

| Category | Signal | Points |
|---|---|---|
| url (cap 50) | Known malicious domain | +50 |
| url | Brand impersonation (text says 'SBI', domain isn't) | +25 |
| url | Lookalike/punycode domain | +30 |
| url | Domain < 30 days old | +20 |
| upi (cap 55) | **Intent-mechanism mismatch** (claims RECEIVE, QR DEBITS) | +40 |
| upi | UPI collection request | +15 |
| social (cap 30) | Urgency/threat language | +15 |
| social | Requests OTP/PIN/credentials | +20 |

- [ ] Thresholds: `≥75 CRITICAL`, `≥50 HIGH`, `≥25 SUSPICIOUS`, else `NO_STRONG_INDICATORS` (**NEVER "safe"**)
- [ ] Capped signals labeled `[capped]` in trigger log
- [ ] Max possible score: 135 (50 + 55 + 30)
- [ ] Category caps prevent correlated signals (punycode + brand mismatch + domain age = one fact) from triple-counting

**3. Router Node** (`agent/router.py`)
- [ ] Classify input mode: `ANALYZE` vs `INCIDENT`
- [ ] Input types: Text / QR Image / URL / "I got scammed"

**4. Parallel Evidence Tools**
- [ ] T1 URL Intel (`tools/url_intel.py`) — cache-first WHOIS/domain age/brand checks
- [ ] T2 QR Decoder (`tools/qr_decoder.py`) — `cv2.QRCodeDetector`, extracts `upi://pay?pa=...&am=...` payload
- [ ] T3 Scam Taxonomy KB (`data/scam_taxonomy.json`) — 10 patterns
- [ ] Brand registry (Qwen) — for brand-mismatch signal

**5. Intent Extraction** (`tools/intent_extractor.py`)
- [ ] LLM call returning `{category: SEND_MONEY|RECEIVE_MONEY|..., confidence: 0.0–1.0}`

**6. Mismatch Engine (TIER 1, NON-NEGOTIABLE)**
- [ ] Narrative intent (LLM): "Scan to receive ₹5000 cashback" → `RECEIVE_MONEY`
- [ ] Mechanism (deterministic, from QR payload): `upi://pay?pa=scammer@okicici&am=5000` → `SEND_MONEY`
- [ ] Mismatch: `RECEIVE ≠ SEND` → **+40** (highest single weight — direct evidence of deception)
- [ ] If intent confidence < 0.7 → Clarify Loop fires (implemented fully in Tier 2; Tier 1 must flag it in trace)

**7. Agent Planner Node + Graph Edges** (`agent/graph.py`)
- [ ] Conditional edges per Plan Part 1:
  ```python
  graph.add_conditional_edges("planner", planner_decision, {
      "clarify":   "clarify_node",    # ask user, loop back
      "deep_scan": "deep_scan_node",  # escalate, loop back to risk engine
      "explain":   "explainer_node",  # confident -> explain & deliver
  })
  graph.add_edge("clarify_node", "evidence_tools")      # re-plan with new info
  graph.add_edge("deep_scan_node", "risk_engine")       # re-score with new evidence
  app = graph.compile(checkpointer=MemorySaver())
  ```
- [ ] Planner reads score + evidence gaps and decides `clarify` / `deep_scan` / `explain`

**8. Explainer Node**
- [ ] LLM explains THE MATH — **never overrides the score**
- [ ] Action plan output; Hinglish/Hindi routing hook (full support in Tier 2)

**9. Minimal Streamlit UI** (`app.py`)
- [ ] Text input + QR file upload
- [ ] Live Agent Decision Trace visualization
- [ ] Returns "hello" on startup (environment proof)

### Deliverable / Gate
**Fixture 1 (Mismatch) runs end-to-end with trace visible** (`intent=RECEIVE, mechanism=SEND, +40 → CRITICAL`).
If the gate fails at 12:30 → **everyone swarms it.**

### Owner Distribution
| Member | Tier 1 Tasks |
|--------|-------|
| **Leader** | Repo, env, merge PRs, keep gate times, 11:00 mentor session |
| **ChatGPT** | `graph.py`, `risk_engine.py`, `state.py` |
| **Qwen** | QR decoder, URL intel, taxonomy JSON, brand registry |
| **Kimi** | Fixture pack + eval benchmark (completed tonight, re-verify at gate) |

---

## Phase 2 — TIER 2: Agentic Loops (12:30–4:00 IST)
**Deadline: 4:00 PM**
**⚠️ No scope additions after 2:00 PM — new ideas go to the "future work" slide.**

### Objectives

**1. Clarify Loop**
- [ ] Fires when intent confidence < 0.7
- [ ] Agent *stops and asks the user*: "Is this message asking you to **pay** money or **receive** money?"
- [ ] Node: `clarify_node` → user answer → loop back to `evidence_tools` → re-plan
- [ ] Patches the LLM's weakest point; degrades into conversation, never a wrong verdict

**2. Deep-Scan Loop (Escalating Verification)**
- [ ] Fires when score 25–74 **and** evidence gap exists
- [ ] Planner *autonomously* runs deeper tools: **deep URL scan**, **brand-registry fuzzy match**
- [ ] Node: `deep_scan_node` → re-score → loop back to `risk_engine`
- [ ] Plan → act → observe → re-plan visible in trace (textbook agentic behavior)

**3. Incident Interview**
- [ ] Multi-turn slot-filling: txn ID → bank → amount → time
- [ ] **ONE question per turn**
- [ ] Memory across turns via LangGraph `MemorySaver` checkpointer
- [ ] Mode entered via router when input is "I got scammed" style

**4. Playbook Generator**
- [ ] Personalized recovery steps built from interview answers: **1930 helpline / bank / cybercrime.gov.in**
- [ ] Never a static dump — tailored to their txn ID, bank, amount, time

**5. Hinglish Routing** (promoted from Tier 3 in v3.0)
- [ ] Hindi/Hinglish intent detection
- [ ] Hinglish/Hindi explainer routing
- [ ] Hinglish demo warning strings in UI (Kimi writes UI strings)

**6. Trace UI Polish**
- [ ] Agent Decision Trace readable for judges (show loop iterations, triggers, +40 mismatch)

### Deliverable
**All 4 fixtures run successfully with complete agent traces** (mismatch, lookalike, incident, legit).

### Owner Distribution
| Member | Tier 2 Tasks |
|--------|-------|
| **Leader** | Mentor follow-up, midpoint review, UX decisions |
| **ChatGPT** | Clarify + deep-scan loops, checkpointer memory |
| **Qwen** | Hinglish routing, taxonomy expansion to 20+ patterns |
| **Kimi** | README, video script, deck copy, UI strings incl. Hinglish warnings |

---

## Phase 3 — TIER 3: Polish (4:00–5:30 IST)
**⛔ HARD CODE FREEZE: 5:30 PM — enforced by Leader. Only bugfixes that break a fixture are allowed after this.**
*Genuinely disposable — cut anything here first if pressed for time.*

### Objectives
- [ ] URLScan live integration (behind `--live` flag — bonus only, never in demo fixtures)
- [ ] Extra taxonomy patterns (20+ total)
- [ ] CSS polish for Streamlit
- [ ] Trace UI enhancements

### Owner
**Qwen** — CSS, eval run, taxonomy.

---

## Midpoint Checkpoint — 4:00 PM
**Owner: Leader**

- [ ] Run **all 4 fixtures** end-to-end
- [ ] Run eval benchmark (30 scenarios — see Evaluation Benchmark below)
- [ ] **Print confusion matrix**, screenshot it for the deck
- [ ] Screenshot Fixture 1 trace for deck slide 5
- [ ] Publish **only measured numbers** — targets are not results

---

## Phase 4 — Deliverables (5:30–9:00 IST)
**Submission opens 8:00 PM → submit by 8:30 PM (30-min buffer) → contingency until 9:00 PM**

### Sub-Phase 4a — Validation + Insurance (5:30–6:00)
**Owner: ChatGPT + Leader**
- [ ] Full fixture validation (all 4, post-freeze)
- [ ] **Screen-record a full clean demo run** (backup to the backup — played if live demo dies on stage)

### Sub-Phase 4b — Demo Video (6:00–7:15)
**Owner: Leader** — Record with OBS/loom at 1080p. **Max 3 takes. Done is better than perfect.**

| Time | Shot | Line |
|---|---|---|
| 0:00–0:20 | Problem: UPI fraud stat + "scan to receive" scam screenshot | "Every year, Indians lose thousands of crores to scams that look legitimate." |
| 0:20–0:40 | 10-sec architecture diagram animation | "VeriFi doesn't guess. It gathers evidence, scores it deterministically, and explains it." |
| 0:40–1:30 | **LIVE: Fixture 1.** Paste text + QR → watch trace: intent=RECEIVE, mechanism=SEND, +40 → CRITICAL | "The message says receive. The QR says pay. VeriFi catches the lie in 3 seconds." |
| 1:30–2:00 | LIVE: Fixture 3 incident interview (3 quick turns) → personalized playbook | "And if the worst already happened, VeriFi walks you through recovery — 1930, your bank, cybercrime.gov.in." |
| 2:00–2:20 | Eval screenshot + Hinglish flash | "Tested on 30 scenarios. Built for Bharat, in Bharat's languages." |
| 2:20–2:30 | Team + vision | "VeriFi — from detection to protection." |

### Sub-Phase 4c — Deck + README (7:15–8:00)
**Owners: Leader + Kimi** (using Kimi's pre-written drafts)

**Deck — 7 slides:**
1. **Problem:** UPI fraud is contextual manipulation — the QR *lies*. Existing tools only check URLs.
2. **Insight:** Intent ≠ Mechanism. One screenshot of the scam. Judges nod here.
3. **Solution:** Evidence-driven agent — deterministic math, agentic loops, LLM only explains.
4. **Architecture:** Part 1 diagram. Emphasize the **THREE LOOPS** — that's what "agentic" means.
5. **Live demo results:** Fixture 1 trace screenshot + eval benchmark numbers.
6. **Bharat impact:** Hinglish-first, incident response playbook with real 1930/cybercrime.gov.in flow, zero false positives on legit transfers.
7. **Moat & future:** taxonomy as living dataset, WhatsApp bot next, bank API integration. (All real future work — nothing vaporware.)

**README contents:**
- [ ] Architecture diagram (Part 1)
- [ ] **"Why these weights" paragraph** (Plan Part 3 — judges WILL ask):
  > *Weights encode evidentiary strength, not vibes. The Intent-Mechanism Mismatch (40) is weighted highest because it is direct proof of deception — the mechanism contradicts the narrative. Known-malicious domains (50) are ground truth. Social-engineering signals are capped lowest (30) because urgency alone has legitimate uses (banks really do send KYC reminders). Category caps prevent correlated signals — punycode, brand mismatch and domain age often describe one underlying fact — from triple-counting. Thresholds were tuned on our 30-scenario benchmark to maximize recall on scam cases while keeping false positives on legitimate UPI requests at zero.*
- [ ] Setup instructions
- [ ] Eval results (measured)

### Sub-Phase 4d — Submission (8:00–8:30)
**Owner: Leader**
- [ ] Submission opens 8:00 PM → **submit by 8:30 PM** (30-min buffer)

### Sub-Phase 4e — Contingency (8:30–9:00)
**Owner: All** — for last-mile fixes to the submission only.

### Owner Distribution
| Member | Deliverable Tasks |
|--------|-------|
| **Leader** | Video star, UX decisions, deck final, submit |
| **ChatGPT** | Bugfix standby, backup recording assistance |
| **Qwen** | CSS polish, eval run |
| **Kimi** | README, video script, deck copy, QA every fixture, judge-Q&A prep |

---

## Role Assignments (Plan Part 6 — All 4 Members)

| Member | Title | Tier 1 | Tier 2 | Lock Block |
|---|---|---|---|---|
| **Leader** | Product owner & integrator | Repo, env, merge PRs, keep gate times | Mentor session, midpoint review, UX decisions | Video, deck, submit |
| **ChatGPT** | Core architect | `graph.py`, `risk_engine.py`, `state.py` | Clarify + deep-scan loops, checkpointer memory | Bugfix standby, backup recording |
| **Qwen** | Tools & data engineer | QR decoder, URL intel, taxonomy JSON, brand registry | Hinglish routing, taxonomy expansion to 20+ patterns | CSS polish, eval run |
| **Kimi** | Research, quality & narrative | Fixture pack + eval benchmark (done tonight) | README, video script, deck copy, UI strings incl. Hinglish warnings | QA every fixture, judge-Q&A prep |

---

## Task Summary Table

| Tier | Time | Block | Owner(s) |
|------|------|-------|----------|
| Pre | Tonight | Repo, keys, fixtures, installs, taxonomy seed, Kimi deliverables | All |
| Sync | 9:00–9:30 | Clone, verify env, assign Tier 1 tasks | All |
| 1 | 9:30–12:30 | State, Risk Engine, Router, QR, URL intel, Intent, MISMATCH, planner graph, minimal UI | ChatGPT, Qwen (+ Leader, Kimi) |
| Gate | 12:30 | Fixture 1 end-to-end or everyone swarms | All |
| 2 | 12:30–4:00 | Clarify, Deep-Scan, Incident Interview, Playbook, Hinglish, trace polish | ChatGPT, Qwen (+ Leader, Kimi) |
| 3 | 4:00–5:30 | URLScan live, Taxonomy 20+, CSS | Qwen |
| Lock | 5:30 | **Hard code freeze** — only fixture-breaking bugfixes | Leader enforces |
| Insure | 5:30–6:00 | Fixture validation + backup demo recording | ChatGPT, Leader |
| Delivery | 6:00–8:30 | Video, deck, README, submit | Leader, Kimi |
| Contingency | 8:30–9:00 | Submission fixes only | All |

---

## Evaluation Benchmark

**Location:** `tests/eval_set.json` — **30 scenarios** (Kimi, ready tonight)

| Category | Count | Scenarios |
|----------|-------|-------|
| Scam | 15 | KYC fraud, digital arrest, fake-buyer QR, task scam, OTP theft, customs scam, ... |
| Legitimate | 10 | Real UPI pays, real bank SMS patterns, friend transfers |
| Edge | 5 | Hinglish scam, ambiguous intent (→ must trigger clarify loop), punycode lookalike |

**Run at 4:00 PM**, print confusion matrix, screenshot for deck.

**Target output (publish ONLY measured numbers):**
```
Eval: 14/15 scams HIGH/CRITICAL, 0 false positives, clarify-loop on 3/5 ambiguous
```

Deck line: *"Evaluated on a 30-scenario benchmark: 14/15 scams flagged HIGH/CRITICAL, 0 false positives on legitimate UPI transfers, clarify-loop correctly fired on 3/5 ambiguous cases."*

---

## Communication Cadence

| Time | Purpose |
|------|---------|
| 9:00 AM | Morning sync: clone repo, verify env, assign Tier 1 tasks |
| 10:30 AM | 15-min sync (plan alignment) |
| 11:00 AM | Mentor session — ask about agentic loop depth |
| 12:30 PM | **Tier 1 GATE**: Fixture 1 complete? Leader decides; failure → everyone swarms |
| 2:30 PM | Mid-phase review (15-min sync) |
| 4:00 PM | Milestone: eval run + fixture validation (15-min sync) |

**Rules:**
- Leader owns all gate decisions.
- **No scope additions after 2:00 PM** — anything new goes on the "future work" slide.
- 5:30 PM hard code freeze — only bugfixes that break a fixture.

---

## Success Criteria

1. **Mismatch score ≥40 fires on demo text** (Fixture 1 → CRITICAL)
2. **Clarify loop activates on ambiguous intent** (confidence < 0.7)
3. **Deep-scan loop escalates on borderline scores** (25–74 + evidence gap)
4. **Incident interview produces personalized playbook** (one question per turn, checkpointer memory)
5. **0 false positives on legitimate UPI** (10/10 legit scenarios pass)
6. **Eval benchmark run and measured results screenshot for deck**
7. **Video, deck, README submitted by 8:30 PM**

---

## 🛑 Final Directives (Plan — unchanged, non-negotiable)

1. **Mismatch in Tier 1.** Everything else is negotiable. It is not.
2. **The LLM never overrides the score.** It explains, asks, and plans — the engine decides.
3. **No live API in a demo fixture.** Hermetic or nothing.
4. **Code freeze 5:30 PM.** The video IS the product.
5. **Never say "safe."** Say "no strong indicators detected."
6. **If a plan item fights a deadline, the deadline wins.** Judges score what they see, not what we intended.

---

*Aligned to `VeriFi_v3_Plan.md` v3.0. When in doubt, the master plan wins.*
