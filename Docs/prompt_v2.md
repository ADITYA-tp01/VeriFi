 # 🔧 PROMPT v2 — VeriFi UI Refinement Pass (Density, Light Mode, Overlap Fixes, Human-Centered UX)
### Paste into Antigravity as a follow-up to the previous redesign. Do NOT regress anything that already works.

## 0. CONTEXT

The v1 redesign landed the right aesthetic (dark glass, risk-color language, mismatch panel). This pass fixes layout density, light-mode contrast, an overlapping badge bug, and re-centers the UX on the real user: **a non-technical Indian user who is either (a) checking if a payment request is a scam, or (b) already scammed and panicking.** Every design decision must pass the test: *"Would a worried 55-year-old understand what to do in 5 seconds?"*

All Antigravity design principles from v1 still apply (glass, GSAP motion, risk-color system). All data contracts, agent logic, and features remain untouched.

---

## 1. 🕳️ KILL THE EMPTY SPACE (highest priority)

Current problem: giant vertical gaps, a narrow centered column (~60% width), chips/cards floating in void.

**New layout rules:**
- Content container: `max-width: 1200px`, horizontal padding `24px`. Nothing narrower unless it's a modal.
- Vertical rhythm: section gaps `24–32px` max. No gap may exceed `48px` anywhere. The hero must fit within **55vh** — headline + subline + input card + CTA visible without scrolling on a 1080p screen.
- Scenario chips: a **4-column grid** filling the full container width (2×2 on tablet, stacked on mobile). Each chip gets: risk-color left accent bar, risk label, title, AND a one-line description (e.g. "'Scan to receive ₹5000 cashback' — the QR debits you instead"). Chips are content cards, not floating pills.
- **Results view becomes a bento grid, not a single column:**
  ```
  ┌─────────────────────────────────────────────────┐
  │  VERDICT BANNER (badge + headline + gauge,      │
  │  compact single row, ~140px tall)               │
  ├──────────────────────────────┬──────────────────┤
  │  INTENT vs MECHANISM (2/3)   │  AGENT TRACE     │
  │                              │  docked (1/3)    │
  ├──────────────────────────────┤  (persists in    │
  │  RISK FACTORS — rows with    │  results view)   │
  │  category chips (2/3)        │                  │
  ├──────────────────────────────┼──────────────────┤
  │  WHAT TO DO NOW (1/2)        │  EVIDENCE / JSON │
  │  big action checklist        │  details (1/2)   │
  └──────────────────────────────┴──────────────────┘
  ```
- **Agent Trace is no longer a tiny centered card.** During analysis: full-container-width terminal-style panel (mono font, steps lighting up in sequence). After results load: it docks into the right column of the bento grid, collapsed to completed steps, expandable. It must always look intentional, never lost.
- Risk-factor rows: full width of their grid cell, `12–16px` padding, chips for category (UPI/URL/SOCIAL), points right-aligned in mono. No card-inside-card empty padding.

## 2. 🐛 FIX THE "MISMATCH DETECTED" OVERLAP

The badge currently sits on top of card text. Rebuild the Intent-vs-Mechanism panel as a **3-column flex row**:
`[CLAIMS card] [fixed 120px center connector column] [EXECUTES card]`
- The center column permanently reserves space: ⚡ collision node on top, "MISMATCH DETECTED" (or "CONSISTENT") badge beneath it. Nothing absolute-positioned over text. Ever.
- On mobile: stack vertically, connector rotates 90° between the cards.
- Card subtitles ("Narrative intent extracted from text") must never be covered — give cards `padding-inline: 20px`.

## 3. ☀️ LIGHT MODE MUST BE READABLE (WCAG AA or delete it)

Current light mode fails contrast (light-red callout text on white = invisible).
- Full token pass for light theme: body text `#0F172A` on `#F8FAFC`; muted text `#475569` (never lighter); risk colors darkened one step — CRITICAL `#DC2626`, HIGH `#EA580C`, SUSPICIOUS `#CA8A04`, CLEAN `#059669`.
- Callouts/alerts in light mode: tinted background (`#FEF2F2` for red) + dark colored text (`#991B1B`) + 1px tinted border. **Never** low-opacity colored text on white.
- Glass panels in light mode: white at 70% opacity, `blur(12px)`, border `#E2E8F0`, shadow `0 20px 40px rgba(15,23,42,0.08)`.
- Verify every screen in BOTH themes. **If light mode cannot pass a visual check in time, lock the app to dark mode and remove the toggle — shipping a broken theme is worse than shipping one theme.**

## 4. 🧘 HUMAN-CENTERED UX — DESIGN FOR A PANICKING USER

**Analyze mode (prevention):**
- Verdict headlines stay blunt and instructional: "Do not proceed with this payment." / "No strong indicators — still confirm with the recipient."
- Directly under the verdict banner: one primary action button, risk-colored. CRITICAL/HIGH → "🚨 What to do right now" (scrolls to actions). CLEAN → "Understand this result".
- "What to do now" checklist uses plain imperative sentences, checkboxes, ≥16px text. No jargon — "Report to 1930" not "Escalate via national helpline infrastructure."

**Incident mode (post-scam) — redesign the tone completely:**
- This user is panicking. The UI must *lower their heart rate*. Swap the alarming palette: incident mode uses **calm indigo/emerald**, not red. No pulsing warnings.
- Opening message from the agent: *"Take a breath — you're doing the right thing. Answer 4 quick questions and I'll prepare your complaint, step by step."*
- Chat interview: one question per bubble, big tap-target quick-reply chips where possible (e.g. bank names), a progress bar "Step 2 of 4", generous 18px text.
- Finale: the playbook renders as a **"Your Complaint Kit"**: numbered step cards (Call 1930 → Bank nodal officer → cybercrime.gov.in → Preserve evidence → Secure device), each with a **copy button** for the pre-filled complaint text (auto-filled with their txn ID/bank/amount), plus a prominent **"Download / Copy full complaint"** primary button. The user should feel they walked in panicking and walked out with paperwork done.

**Global simplicity rules:** body text ≥16px (18px in incident mode), one primary CTA per screen, buttons ≥48px tall, icon+label on every action, nothing important communicated by color alone (always pair with icon + text).

## 5. ✅ ACCEPTANCE CRITERIA (all must pass)

1. No vertical gap > 48px; hero fully visible at 1080p without scrolling.
2. Results view fills the 1200px container as a bento grid — no single-narrow-column layouts.
3. "MISMATCH DETECTED" badge has reserved space and overlaps zero text, in both themes, all viewport widths.
4. Light mode: every text element ≥ 4.5:1 contrast — or light mode is removed.
5. Agent trace is full-width during analysis, docked in results — never a floating island.
6. Incident mode contains zero red alarm styling; includes the "Complaint Kit" with working copy buttons.
7. All previous v1 wins preserved: glass surfaces, GSAP choreography, staggered entrances, risk-color ambient glow, scenario grid one-click demos, `prefers-reduced-motion` support, zero console errors.
8. A first-time user can answer "Is this a scam?" and "What do I do?" within 5 seconds of the result appearing.
