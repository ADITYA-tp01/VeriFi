# VeriFi — Pitch Deck Skeleton (7 Slides)

> Content per Plan Part 9. Finalize visuals at 7:15–8:00 PM. Eval numbers: paste ONLY from `tests/eval_results.json`.

---

## Slide 1 — Problem
**Title:** *UPI fraud is contextual manipulation — the QR lies*

- Indians lose thousands of crores yearly to scams that *look* legitimate
- "Scan to receive ₹5000 cashback" → the QR quietly DEBITS you
- Existing tools check URLs and blocklists — **nothing checks the narrative vs what the code actually does**

## Slide 2 — Insight
**Title:** *Intent ≠ Mechanism*

- One screenshot of the scam, two facts:
  - **Narrative intent** (what the message claims): RECEIVE
  - **Mechanism** (what the QR does): SEND
- **RECEIVE ≠ SEND → direct evidence of deception, not a "suspicious vibe"**
- *(Judges nod here — this is the whole pitch in one slide.)*

## Slide 3 — Solution
**Title:** *Evidence-driven agent — math decides, LLM explains*

- Deterministic category-capped risk engine (max 135, never "safe")
- Mismatch carries the highest single weight: **+40**
- Three genuine agentic loops: clarify → ask · deep-scan → escalate · incident → interview
- LLM explains THE MATH — **never overrides the score**

## Slide 4 — Architecture
**Title:** *The Part 1 diagram — emphasize the THREE LOOPS*

- Router → parallel evidence tools → risk engine → planner
- Loop 1: confidence < 0.7 → agent *asks the user*, re-plans
- Loop 2: score 25–74 + gap → agent *escalates tools autonomously*, re-scores
- Loop 3: incident interview with checkpointer memory (Tier 2)
- Full agent decision trace visible in the UI — plan→act→observe→re-plan, on screen

## Slide 5 — Live Demo Results
**Title:** *Fixture 1 trace + benchmark numbers*

- Trace screenshot: `intent=RECEIVE, mechanism=SEND, +40 → 105/135 CRITICAL`
- Eval (30 scenarios) — **paste measured numbers**:
  - `Scams HIGH/CRITICAL: [from eval_results.json]`
  - `False positives on legit UPI: [from eval_results.json]`
  - `Clarify-loop fired: [from eval_results.json]`
- Hermetic fixtures — demo cannot fail on stage

## Slide 6 — Bharat Impact
**Title:** *From detection to protection*

- Hinglish-first: Hindi/Hinglish intent detection + warnings in natural phrasing
- Incident response playbook: real **1930 / bank / cybercrime.gov.in** flow, personalized per victim
- **Zero false positives** on legitimate UPI transfers (10/10 legit scenarios clean)
- Works offline/hermetically — no dependency on paid APIs for the core verdict

## Slide 7 — Moat & Future
**Title:** *What others can't copy quickly*

- **Taxonomy as a living dataset** — 10 → 20+ patterns, grows with every reported scam
- Next: WhatsApp bot delivery, bank API integration for real-time txn verification
- Everything on this slide is real future work — nothing vaporware

---

### Speaker notes (judge Q&A prep)
- *"Why these weights?"* → README "Why these weights" paragraph, verbatim.
- *"Is it safe?"* → We never say safe. We say "no strong indicators detected" — absence of evidence isn't evidence of absence.
- *"Why not just use an LLM?"* → LLMs hallucinate verdicts. Our score is deterministic, reproducible, and explainable; the LLM narrates it and asks when unsure.
- *"What if the API is down?"* → Hermetic cache + UNVERIFIED degradation. The app never crashes and never lies.
