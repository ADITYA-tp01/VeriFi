# VeriFi — Demo Video Script (2:30)

**Record:** OBS/loom, 1080p, max 3 takes. Backup recording of a clean full run at 6:00 PM.
**Total runtime: 2 minutes 30 seconds.** Done is better than perfect.

---

## Shot List

### 0:00–0:20 — The Problem
**Visual:** UPI fraud statistic on screen, then a real "scan to receive cashback" scam screenshot (blur any personal data).
**Narration:**
> "Every year, Indians lose thousands of crores to scams that look legitimate. The message says *you'll receive money*. The QR quietly *debits* you. Existing tools check URLs — they never check the lie."

### 0:20–0:40 — Architecture (10-sec animation)
**Visual:** Part 1 architecture diagram, animate input → router → evidence → risk engine → planner → the three loops.
**Narration:**
> "VeriFi doesn't guess. It gathers evidence — URL intel, QR decoding, scam taxonomy — scores it with deterministic, category-capped math, and an agent that plans, asks, and re-plans. The LLM explains the math. It never overrides it."

### 0:40–1:30 — LIVE: Fixture 1 (THE MONEY SHOT)
**Visual:** Streamlit app. Click "Load Fixture 1". Camera follows the decision trace as it renders.
**On screen (point at each):** `intent=RECEIVE_MONEY` → `mechanism=SEND_MONEY` → `MISMATCH +40` → `105/135 → CRITICAL`.
**Narration:**
> "Watch. The message claims receive. The QR says pay. Intent and mechanism don't match — that's direct evidence of deception, worth +40 points. The engine scores everything deterministically: brand impersonation, a three-day-old lookalike domain, urgency language. One hundred five of one hundred thirty-five — CRITICAL. And here's the trace: every decision the agent made, in order."

*(Pause 2 seconds on the trigger list — let judges read "+40 CRITICAL: claims RECEIVE, QR actually DEBITS".)*

### 1:30–2:00 — LIVE: Fixture 3 Incident Interview
**Visual:** Type "I got scammed yesterday — Rs.15000 deducted…". Show 3 quick interview turns (txn ID → bank → amount), then the personalized playbook.
**Narration:**
> "And if the worst already happened, VeriFi switches modes — it interviews you one question at a time, remembers your answers, and builds a recovery playbook around *your* transaction: call 1930, contact your bank, file at cybercrime.gov.in."

*(Tier 2 build — if interview isn't demo-ready, show the incident branch response + play the backup recording.)*

### 2:00–2:20 — Eval + Hinglish
**Visual:** Screenshot of `run_eval.py` output (confusion matrix + summary line), then a Hinglish scam sample being flagged.
**Narration:**
> "Tested on a thirty-scenario benchmark: fifteen of fifteen scams flagged high or critical, zero false positives on legitimate UPI transfers, the clarify loop firing exactly when intent is ambiguous. Built for Bharat — in Bharat's languages."

### 2:20–2:30 — Team + Vision
**Visual:** Team, then VeriFi wordmark.
**Narration:**
> "VeriFi — from detection to protection."

---

## Pre-record Checklist
- [ ] `.env` with Groq key OR confirmed heuristic fallback (either is fine)
- [ ] Fixture 1 loads and shows CRITICAL — verified in-app before rolling
- [ ] Browser zoom ≥ 120% so trace text is readable at 1080p
- [ ] Backup recording exists (recorded 6:00 PM, tested playable)
- [ ] Max 3 takes — after that, ship what we have
