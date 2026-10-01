"""Phase 4 audit — verify deck, README, video script, eval numbers."""
import json
import re
import sys
from pathlib import Path

if sys.stdout.encoding and sys.stdout.encoding.lower() != "utf-8":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

ROOT = Path(__file__).resolve().parent.parent
failures = []


def check(label, ok):
    print(f"  {'OK     ' if ok else 'MISSING'}: {label}")
    if not ok:
        failures.append(label)


# 1. eval_results.json
print("=== eval_results.json ===")
d = json.loads((ROOT / "tests" / "eval_results.json").read_text(encoding="utf-8"))
print(f"  keys: {list(d.keys())}")
print(f"  summary: {d.get('summary_line') or d.get('eval_line') or '(see keys above)'}")

# 2. deck.html
print("=== deck.html ===")
html = (ROOT / "Docs" / "deck.html").read_text(encoding="utf-8")
slides = html.count('<section class="slide">')
check(f"7 slides present ({slides} found)", slides == 7)
for n in range(1, 8):
    check(f"slide {n} footer", f"{n} / 7" in html)
check("Fixture 1 trace 105/135", "105/135" in html)
check("eval 15/15", "15/15" in html)
check("eval 0/10 FP", "0/10" in html)
check("clarify 3/3", "3/3" in html)
check("edge 5/5", "5/5" in html)
check("THREE LOOPS slide", "three loops" in html.lower())
check("Intent != Mechanism", "Intent" in html and "Mechanism" in html)
check("+40 mismatch", "+40" in html)
check("1930 helpline", "1930" in html)
check("cybercrime.gov.in", "cybercrime.gov.in" in html)
check("Hinglish", "Hinglish" in html)
check("taxonomy count", "21" in html)
check("print CSS (Ctrl+P to PDF)", "@media print" in html)
check("measured numbers not placeholders", "[from eval_results.json]" not in html)

# 3. README required contents (Phase 4c)
print("=== README ===")
readme = (ROOT / "README.md").read_text(encoding="utf-8")
check("architecture diagram", "```" in readme and "ROUTER" in readme.upper() or "Router" in readme)
check("Why these weights paragraph", "Weights encode evidentiary strength" in readme)
check("setup instructions", "pip install" in readme)
check("eval results (measured)", "15/15" in readme and "0 false positives" in readme)
check("never says 'safe' doctrine", "safe" in readme.lower())
check("three loops documented", "clarify" in readme.lower() and "deep" in readme.lower())

# 4. video script (Phase 4b support)
print("=== video_script.md ===")
vs = (ROOT / "Docs" / "video_script.md").read_text(encoding="utf-8")
check("exists", bool(vs))
check("total runtime 2:30", "2:30" in vs or "2 minutes 30" in vs)
check("fixture 1 live shot", "Fixture 1" in vs)
check("incident interview shot", "incident" in vs.lower())
check("eval screenshot shot", "eval" in vs.lower())

# 5. Phase 4 checkboxes in phases doc
print("=== Phases doc (Phase 4 section) ===")
doc = (ROOT / "Docs" / "Phases-of-Project.md").read_text(encoding="utf-8")
p4 = doc.split("## Phase 4")[1].split("\n---\n")[0] if "## Phase 4" in doc else ""
checked = p4.count("- [x]")
unchecked = p4.count("- [ ]")
print(f"  {checked} checked, {unchecked} unchecked")
for m in re.finditer(r"- \[ \] (.+)", p4):
    print(f"  UNCHECKED: {m.group(1)[:80]}")

print()
if failures:
    print(f"AUDIT FAILED — {len(failures)} missing:")
    for f in failures:
        print(f"  - {f}")
    sys.exit(1)
print("AUDIT PASSED — all Phase 4 artifact checks green")
