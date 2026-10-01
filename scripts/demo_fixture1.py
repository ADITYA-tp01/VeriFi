"""Demo: run Fixture 1 end-to-end and print the full agent decision trace."""
import sys
import uuid
from pathlib import Path

if sys.stdout.encoding and sys.stdout.encoding.lower() != "utf-8":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from agent.graph import app  # noqa: E402

f1 = ROOT / "data" / "fixtures" / "fixture_1_mismatch"
msg = (f1 / "message.txt").read_text(encoding="utf-8")
qr = (f1 / "qr.png").read_bytes()

r = app.invoke(
    {"user_input": msg, "qr_image": qr},
    {"configurable": {"thread_id": str(uuid.uuid4())}},
)

print(f"SCORE: {r['score']}/135  LEVEL: {r['risk_level']}")
print(f"INTENT: {r['intent']}")
print(f"MECHANISM: {r['mechanism']['action']} - {r['mechanism']['payload']}")
print(f"MISMATCH: {r['evidence_vector']['intent_mechanism_mismatch']}")
print("TRIGGERS:")
for t in r["triggers"]:
    print("  ", t)
print("TRACE:")
for i, e in enumerate(r["trace_log"], 1):
    print(f"  {i}. [{e['node']}] {e['decision']} - {e['detail']}")
print("EXPLANATION:", r["explanation"])
