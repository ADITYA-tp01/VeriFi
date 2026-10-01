# 🎨 PROMPT.md — VeriFi Production UI/UX Rebuild
### Paste this ENTIRE file into Antigravity with the `antigravity-design-expert` / ui-ux-pro-max skill active. Attach screenshots of the current UI if possible.

---

## 1. ROLE

You are a world-class UI/UX engineer operating under the **Antigravity Design** philosophy: weightless, spatial, glassmorphic, motion-rich interfaces built with React + Tailwind + GSAP. You are redesigning the frontend of a live, working AI product for a hackathon final. Your output must look like a **funded YC startup's security product** — not a student project, not a template, not a dashboard theme.

---

## 2. PRODUCT CONTEXT (read carefully — design must serve THIS story)

**VeriFi — Evidence-Driven Financial Safety Agent** (Bharat Agentic 2026, FinTech track)

VeriFi protects Indian users from UPI/QR/phishing fraud. The user pastes a suspicious SMS/WhatsApp message, a URL, or a QR code image. An **agentic AI pipeline** then:
1. Routes the input (ANALYZE mode vs INCIDENT mode)
2. Runs parallel evidence tools (URL intel, QR payload decode, scam-taxonomy match)
3. Scores risk with a **deterministic engine** (0–135, category-capped) — the LLM never decides the score, it only explains it
4. Detects our signature **Intent–Mechanism Mismatch**: the message *claims* "scan to RECEIVE ₹5000 cashback" but the QR payload *actually executes* a SEND/debit — this mismatch is the hero insight of the product
5. Runs agent loops: asks the user a clarifying question when intent is ambiguous; escalates to deeper scans when the score is borderline
6. In **Incident mode** ("I've already been scammed"), it interviews the victim one question at a time (txn ID → bank → amount → when) and generates a personalized recovery playbook (Call 1930, bank nodal officer, cybercrime.gov.in, evidence preservation, device check)

**The design must communicate three things instantly to a judge watching from 2 meters away:**
- 🧮 *"This is evidence and math, not an LLM guessing"* (deterministic credibility)
- 🔄 *"This is a real agent — it plans, asks, escalates, and acts"* (visible agentic loops)
- 🇮🇳 *"This is built for Bharat"* (Hinglish/Hindi support, real Indian scam patterns, 1930 helpline)

---

## 3. CURRENT STATE (what you're replacing)

An existing **React + Vite** app (localhost:5173) with: a header (VeriFi logo, "BHARAT AGENTIC 2026" badge, Analyze Threat / Incident Response tabs, language dropdown, "Engine Active" pill), 4 quick-demo scenario chips, an input card (Text / URL / QR tabs + big CTA button "RUN VERIFI DEEP INVESTIGATION"), a results view (circular 68/100 score gauge, "HIGH RISK" badge, headline, "View Risk Factors" accordion, Intent-vs-Mechanism comparison panel with "MISMATCH DETECTED" badge and a KEY MISMATCH FINDING callout).

The current UI is functional but flat: static cards, no motion, weak hierarchy, generic dark-blue theme. **Keep every feature and API contract. Rebuild the entire visual and interaction layer.**

## 4. HARD CONSTRAINTS — DO NOT BREAK

- ✅ Stack stays: **React + Vite + Tailwind CSS + GSAP (ScrollTrigger)**. Add `gsap` via npm. No UI frameworks like MUI/AntD.
- ✅ **Zero changes to agent logic, API calls, state shape, or scoring.** You own the presentation layer only. All data fields currently rendered must still be rendered.
- ✅ All 4 quick-demo scenarios must remain **one click** from the landing state — judges will click them live.
- ✅ Keep both modes: Analyze Threat and Incident Response. Keep the language toggle (English / हिंदी).
- ✅ Respect `prefers-reduced-motion: reduce` — disable all non-essential animation.
- ✅ Performance: `will-change: transform` on animated elements; never animate `box-shadow`/`filter` continuously; 60fps on a mid-range laptop.
- ✅ No lorem ipsum, no placeholder images, no dead buttons. Everything on screen must work.

---

## 5. DESIGN DIRECTION — "THE FRAUD WAR ROOM"

**Mood:** A premium cyber-security command center meets fintech trust. Think *Linear's polish × Stripe's restraint × a SOC dashboard's authority* — with Antigravity's weightless glass aesthetic. Dark, deep, confident. Every rupee of visual noise removed.

**Color system (CSS variables, Tailwind config):**
```
--bg-abyss:      #070B14   /* page background — near-black navy */
--bg-panel:      rgba(15, 23, 42, 0.55)  /* glass panels */
--border-glass:  rgba(148, 163, 184, 0.12)
--text-primary:  #F1F5F9
--text-muted:    #94A3B8
--accent:        #6366F1 → #06B6D4   /* indigo→cyan gradient, CTAs only */
--risk-critical: #EF4444   /* red    — CRITICAL  */
--risk-high:     #F97316   /* orange — HIGH      */
--risk-suspicious:#EAB308  /* amber  — SUSPICIOUS */
--risk-clean:    #10B981   /* emerald— CLEAN / no indicators */
```
- Background: deep abyss navy with a **subtle animated radial glow** (very slow drifting indigo/cyan orbs at 6–10% opacity, GPU-composited) + a faint isometric grid overlay that fades at edges. Depth, not distraction.
- Risk color is a **first-class design language**: every result view inherits the verdict's color as ambient glow, border tint, and gauge stroke. A judge should know the verdict from the room's reflection alone.

**Typography:**
- Display/headings: **"Space Grotesk"** (600/700) — technical, modern
- Body/UI: **"Inter"** (400/500/600)
- Numbers/scores/mono data (UPI handles, domains, trace logs): **"JetBrains Mono"** — monospace = "this is evidence, machine-verified"
- Scale: score number ≥ 72px, section headings 24–28px, body 15–16px, captions 12–13px. Readable from 2 meters.

**Surfaces:** All cards are glass: `backdrop-filter: blur(12px)`, 1px glass border, layered soft shadow `0 20px 40px rgba(0,0,0,0.35)`, `border-radius: 16–20px`. Cards float — nothing sits flat on the background.

---

## 6. LAYOUT & COMPONENT SPEC

### 6.1 Header (sticky, glass)
Logo shield (subtle float animation, 4s ease-in-out infinite ±6px) · "VeriFi" wordmark in Space Grotesk · "BHARAT AGENTIC 2026" as a small outlined chip · mode switcher **Analyze Threat / Incident Response** as a segmented control with a sliding pill indicator (GSAP-animated, not a jump) · language toggle · "Engine Active" status dot with a soft breathing pulse (emerald).

### 6.2 Hero input zone (above the fold, the stage)
- Center it like a product landing page, not a form. Headline: **"Is that payment request lying to you?"** with sub: *"Paste a message, link, or QR — VeriFi investigates the evidence, not the vibes."*
- **Input type tabs** (Text / URL / QR) as an animated segmented control; the input card morphs between states (textarea ↔ URL field ↔ QR dropzone) with a 0.35s crossfade + slight Y-shift.
- QR dropzone: dashed glass border that glows cyan on drag-over; on drop, thumbnail preview floats in.
- CTA button: full-width gradient (indigo→cyan), label **"Run Deep Investigation"**, with a shine sweep on hover and a 0.98 scale press. 
- **Quick Demo Scenarios** as 4 floating glass chips in a row beneath: *UPI Fraud — Cashback QR (CRITICAL)*, *Phishing — Electricity Bill (HIGH)*, *Advance Fee — Lottery URL (SUSPICIOUS)*, *Legitimate — Merchant Receipt (CLEAN)*. Each chip carries its risk-color accent bar and score. Staggered entrance on load (0.1s apart, drop-in from Y with slight rotation — per Antigravity rules). On hover: lift 4px + glow.

### 6.3 ⏳ The Analyzing Sequence (CRITICAL — this is where "agentic" becomes visible)
Do NOT show a spinner. When the agent runs, show a **live Agent Trace**: a vertical timeline of steps that light up in sequence as the backend progresses, each in JetBrains Mono with an icon:
```
✓ Input routed → ANALYZE mode
✓ QR decoded → upi://pay?pa=scammer@okicici&am=5000
✓ URL intel → domain checked
✓ Scam taxonomy → 2 patterns matched
◌ Planner deciding: escalate to deep scan…
```
Each step fades/slides in (0.25s), active step pulses, completed steps collapse to compact. If the clarify-loop or deep-scan-loop fires, the timeline **branches visually** (a small fork indicator) — this is our #1 proof of agency; make it unmistakable.

### 6.4 🎯 Results View (the money shot)
Reveal with a choreographed GSAP sequence:
1. **Verdict banner** slides in: risk badge (HIGH RISK etc.) in risk color + one-line plain-language verdict headline.
2. **Score gauge**: circular, animated count-up from 0 to final score (GSAP, ~1.2s, easeOut), stroke gradient in the verdict's risk color, glow at the arc tip. Number in JetBrains Mono, large.
3. **Intent vs Mechanism Verification** — the signature panel. Two glass cards facing each other:
   - LEFT (cyan tint): **"WHAT THE MESSAGE CLAIMS"** — e.g. RECEIVE MONEY / PAY BILL + one-line explanation
   - RIGHT (red tint): **"WHAT THE MECHANISM EXECUTES"** — e.g. SEND MONEY / PHISHING PAGE + the decoded payload (mono font)
   - Between them: a **⚡ collision node**. On reveal, the two cards slide toward center and a "MISMATCH DETECTED" badge slams in (scale 1.4→1.0 with a subtle screen-shake of 2px, once). When intent and mechanism agree, show a green "CONSISTENT" state instead.
   - Below: **KEY MISMATCH FINDING** callout strip in red-tinted glass.
4. **Risk Factors accordion**: the weighted evidence list, each row showing `+40 — Intent-Mechanism Mismatch` style chips with per-category grouping (URL / UPI / Social) and the category caps visible. Judges must see the *math*. Rows expand to show raw evidence JSON in mono.
5. **Recommended actions**: 2–3 plain-language next steps as checklist cards.
6. Subtle parallax: background orbs move at 0.5× scroll speed; foreground cards at 1×.

### 6.5 🚨 Incident Response Mode
- A **chat-style interview UI**, not a form: agent bubble asks one question ("What was the transaction ID?"), user replies, next question slides in. Typing indicator (3-dot bounce). Bubbles are glass; agent bubbles have the shield avatar.
- Progress: slim stepper showing slots filled (txn ✓ → bank ✓ → amount ◌ → when ◌).
- Finale: the **Personalized Recovery Playbook** renders as a numbered action card deck (Call 1930 · Bank nodal officer · cybercrime.gov.in · Preserve evidence · Secure device), each card flipping in with a stagger. Include a "Copy playbook" button.

### 6.6 Language toggle
Switching to हिंदी must visibly re-render verdicts, actions, and UI strings (Devanagari, correct font fallback). The toggle animates with a sliding pill.

### 6.7 Footer
One slim glass strip: "VeriFi — Evidence-Driven Financial Safety · Bharat Agentic 2026" + the disclaimer: *"VeriFi reports evidence-based indicators, never guarantees safety. Always verify with your bank."*

---

## 7. MOTION RULES (Antigravity doctrine — enforce all)
- No instant state changes: minimum `0.3s ease-out` everywhere.
- Staggered entrances on every card grid (0.1s offsets).
- GSAP ScrollTrigger: sections float in from Y+40 with 2–3° rotation settling to 0.
- All verdict reveals choreographed as one timeline, not independent animations.
- Ambient background animation must be subtle, slow (≥8s loops), GPU-only.
- `prefers-reduced-motion`: everything appears instantly, no loops.

## 8. STATES YOU MUST DESIGN
- **Empty/landing** (hero, inviting) · **Analyzing** (live trace timeline) · **Result: CRITICAL / HIGH / SUSPICIOUS / CLEAN** (4 distinct ambient color treatments — CLEAN uses emerald + copy: "No strong indicators detected" — **never** the word "Safe") · **Degraded** (a tool returned UNVERIFIED → show a neutral gray "unverified" chip in the trace, UI never errors) · **Clarify-loop question** (agent asks user inline: "Does this message ask you to pay or receive?" with two big tap targets).

## 9. JUDGE-DEMO ACCEPTANCE CRITERIA (definition of done)
1. Landing → click "Cashback QR" scenario → full mismatch verdict revealed with choreography, in under 4 seconds of visible flow.
2. Every verdict readable from 2 meters (score, badge, mismatch panel).
3. Agent trace visibly shows planning/escalation — a non-technical judge can point at the screen and say "I see it thinking."
4. Incident mode completes a 3-question interview and renders the playbook without scrolling bugs.
5. Zero console errors, zero layout shift during animations, 60fps on integrated graphics.
6. The word "Safe" appears nowhere. Lorem ipsum appears nowhere. Dead buttons exist nowhere.

**Deliverable:** the complete redesigned React frontend, componentized (`/components`: Header, Hero, ScenarioChips, AgentTrace, ScoreGauge, MismatchPanel, RiskFactors, IncidentChat, PlaybookDeck, Footer), Tailwind config extended with the tokens above, GSAP timelines in a `/motion` module. Preserve all existing data contracts.
