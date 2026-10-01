"""Live LLM verification — fixture 1 through the full graph with real Groq keys."""
import sys
from pathlib import Path

if sys.stdout.encoding and sys.stdout.encoding.lower() != "utf-8":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from uuid import uuid4  # noqa: E402

from agent.graph import app  # noqa: E402

F1 = ROOT / "data" / "fixtures" / "fixture_1_mismatch"
msg = (F1 / "message.txt").read_text(encoding="utf-8")
qr = (F1 / "qr.png").read_bytes()

cfg = {"configurable": {"thread_id": str(uuid4())}}
r = app.invoke({"user_input": msg, "qr_image": qr}, cfg)

intent = r.get("intent") or {}
print("intent:", intent)
print("score:", r["score"], "/", 135, "->", r["risk_level"])
print("mismatch:", (r.get("evidence_vector") or {}).get("intent_mechanism_mismatch"))
print()
print("explanation:")
print(r.get("explanation", ""))

llm_used = intent.get("source") == "llm"
# fallback templates start with "VeriFi scored this" (en) — LLM prose won't
fallback = (r.get("explanation") or "").startswith("VeriFi scored this")
print()
print("INTENT FROM LLM:", llm_used)
print("EXPLANATION FROM LLM:", not fallback)
print("SCORE UNCHANGED (105 CRITICAL):", r["score"] == 105 and r["risk_level"] == "CRITICAL")

ok = llm_used and not fallback and r["score"] == 105 and r["risk_level"] == "CRITICAL"
sys.exit(0 if ok else 1)
