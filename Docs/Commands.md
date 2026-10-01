# VeriFi — Presentation Commands

Quick-reference for demo day. Run everything from the project root (`C:\Users\adity\Documents\VeriFi`).

---

## 1. One-Time Setup (before you present)

```powershell
# Install dependencies
pip install -r requirements.txt

# Create your .env (Groq key optional — heuristic fallback exists)
copy .env.example .env
notepad .env                # paste GROQ_API_KEY=... if you have it

# Regenerate hermetic fixtures (QR codes + cached API JSONs)
python scripts\make_fixtures.py
```

---

## 2. Pre-Demo Health Check (run 10 min before)

```powershell
# Tests — expect: 18 passed
python -m pytest tests\ -q

# Benchmark — expect: Eval: 15/15 scams HIGH/CRITICAL, 0 false positives, clarify 3/3
python tests\run_eval.py

# Quick artifact audit — expect: AUDIT PASSED
python scripts\audit_phase4.py
```

All three must be green. If any fails, do NOT restart the environment — check the output.

---

## 3. Start the App (demo)

```powershell
streamlit run app.py
```

Opens at **http://localhost:8501** — keep this window open.

---

## 4. The Live Demo Script

### Shot A — Fixture 1: The Mismatch (THE money shot, ~50 sec)

1. In the app, click **"Fixture 1: Mismatch"** (bottom button row)
2. Point at the trace as it renders — say:
   > "The message says receive. The QR says pay. VeriFi catches the lie."
3. Highlight in order:
   - **Score: 105/135 · CRITICAL**
   - **Intent-Mechanism Mismatch: YES — +40**
   - The trace line: `mismatch → MISMATCH +40`
   - Score breakdown bars: `url 50/50 · upi 40/55 · social 15/30` (= 105)

### Shot B — Fixture 3: Incident Interview (~30 sec)

1. Click **"Fixture 3: Incident"**
2. The agent asks ONE question at a time — answer (or paste from `data\fixtures\fixture_3_incident\interview_answers.json`):

| Turn | Question | Answer to give |
|---|---|---|
| 1 | Transaction ID? | `TXN7845123690` |
| 2 | Which bank? | `HDFC Bank` |
| 3 | How much? | `15000` |
| 4 | When? | `2026-09-30 14:32 IST` |

3. Point at the **personalized playbook** — say:
   > "And if the worst already happened, VeriFi walks you through recovery — 1930, your bank, cybercrime.gov.in."

### Shot C — Hinglish Flash (10 sec)

1. Paste into the text box:
   ```
   Turant ye QR scan karo aur cashback milega, warna offer band ho jayegi!
   ```
2. Click **Analyze**
3. Point at the banner: *"हिंग्लिश/हिंदी detect hua"* and the Hinglish explanation

### Shot D — Fixture 4: Zero False Positive (10 sec)

1. Click **"Fixture 4: Legit"**
2. Point at: **NO_STRONG_INDICATORS** — say:
   > "Legitimate transfer — zero false positives across all 10 legit scenarios."

### Shot E — Fixture 2: Lookalike Domain (10 sec, optional)

1. Click **"Fixture 2: Lookalike"**
2. Point at url intel trace: `malicious=True brand_mismatch=True`

---

## 5. Backup / Insurance Commands

```powershell
# Full validation (if a judge asks "does it actually work?")
python -m pytest tests\ -q
python tests\run_eval.py

# Re-run the incident interview outside the browser (text-only proof)
python scripts\demo_fixture3.py

# Restart the app if it crashes
#   Ctrl+C in the streamlit window, then:
streamlit run app.py

# Use a different port if 8501 is occupied
streamlit run app.py --server.port 8601
```

---

## 6. Deck (for submission / slides)

```powershell
# Open the 7-slide deck in browser
start Docs\deck.html

# Then: Ctrl+P → Destination: "Save as PDF" → Layout: Landscape → Save
```

---

## 7. Eval Confusion Matrix (screenshot for slide 5)

```powershell
python tests\run_eval.py
```

Expected output:
```
Confusion matrix (flag = SUSPICIOUS/HIGH/CRITICAL):
                Predicted FLAG   Predicted CLEAN
  Actual SCAM         15                0
  Actual LEGIT         0               10

Eval: 15/15 scams HIGH/CRITICAL, 0 false positives on legit transfers, clarify-loop fired on 3/3 expected cases
```

Screenshot this terminal output → paste into deck slide 5.

---

## 8. Git (after demo, if you need to push)

```powershell
git status
git add -A
git commit -m "post-demo updates"
git push origin master
```

---

## Quick Recovery Table

| Problem | Fix |
|---|---|
| Port 8501 busy | `streamlit run app.py --server.port 8601` |
| App stuck / white screen | Ctrl+C → `streamlit run app.py` |
| Tests fail | `python scripts\make_fixtures.py` → re-run tests |
| Groq API error | Ignore — heuristic fallback works offline, hermetic by design |
| Interview won't continue | Type the answer → click **Submit answer** (one question per turn) |
| Want a fresh session | Refresh the browser page (new thread_id) |

---

## Judge Q&A — One-Line Answers

| Question | Answer |
|---|---|
| "Is it safe?" | We never say safe. We say "no strong indicators detected" — absence of evidence isn't evidence of absence. |
| "Why these weights?" | Read README "Why these weights" — mismatch=40 is direct proof of deception, not a vibe. |
| "Why not just an LLM?" | LLMs hallucinate verdicts. Score is deterministic, reproducible, explainable; LLM narrates and asks when unsure. |
| "What if the API is down?" | Hermetic cache + UNVERIFIED degradation. Never crashes, never lies. |
| "How many tests?" | 18 unit tests + 30-scenario benchmark: 15/15 scams, 0 false positives, 3/3 clarify. |
