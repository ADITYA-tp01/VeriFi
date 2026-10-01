"""Demo: Fixture 3 incident interview -> personalized playbook (Tier 2 Loop 3)."""
import json
import sys
import uuid
from pathlib import Path

if sys.stdout.encoding and sys.stdout.encoding.lower() != "utf-8":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from langgraph.types import Command  # noqa: E402

from agent.graph import app  # noqa: E402

F3 = ROOT / "data" / "fixtures" / "fixture_3_incident"
msg = (F3 / "message.txt").read_text(encoding="utf-8")
answers = json.loads((F3 / "interview_answers.json").read_text(encoding="utf-8"))

cfg = {"configurable": {"thread_id": str(uuid.uuid4())}}
r = app.invoke({"user_input": msg}, cfg)
turn = 1
while "__interrupt__" in r:
    q = r["__interrupt__"][0].value
    key = ["txn_id", "bank", "amount", "time"][turn - 1]
    print(f"TURN {turn}  Q: {q}")
    print(f"         A: {answers[key]}")
    r = app.invoke(Command(resume=answers[key]), cfg)
    turn += 1

print("\nSLOTS:", r["incident_slots"])
print("\nTRACE:")
for i, e in enumerate(r["trace_log"], 1):
    print(f"  {i}. [{e['node']}] {e['decision']}")
print("\nPLAYBOOK:\n")
print(r["playbook"])
