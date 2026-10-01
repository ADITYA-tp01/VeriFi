"""Probe: stronger Hinglish prompt + live clarify triggers (conf < 0.7)."""
import sys
from pathlib import Path

if sys.stdout.encoding and sys.stdout.encoding.lower() != "utf-8":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
from dotenv import load_dotenv  # noqa: E402

load_dotenv()
import os  # noqa: E402

from groq import Groq  # noqa: E402
from tools.intent_extractor import extract_intent  # noqa: E402

client = Groq(api_key=os.getenv("GROQ_API_KEY"))
MODEL = os.getenv("GROQ_MODEL", "openai/gpt-oss-120b")

prompt = (
    "Explain to a Hindi-speaking UPI user why this message scored 15/135 "
    "(urgency language only).\n"
    "Rules: NEVER say safe. Under 80 words. End with action plan.\n"
    "CRITICAL LANGUAGE RULE: You MUST reply ONLY in Hinglish (Hindi written in "
    "Roman/Latin script), like 'Aapko ye message scan nahi karna chahiye...'. "
    "Do NOT reply in English at all. Your first word must be Hindi in Roman script."
)
resp = client.chat.completions.create(
    model=MODEL,
    messages=[{"role": "user", "content": prompt}],
    temperature=0.3,
    max_tokens=800,
)
print("=== STRONGER HINGLISH PROMPT ===")
print(resp.choices[0].message.content[:450])
print()

print("=== CLARIFY TRIGGER HUNT (need conf < 0.7) ===")
candidates = [
    "payment",
    "ye wala bhej dun?",
    "money transfer help",
    "do the needful",
    "the thing we discussed",
    "UPI kar diya",
    "help me with the transaction",
    "wo wala payment kar diya kya",
    "account me daal diya",
    "bhej dun ya rukun?",
]
for t in candidates:
    i = extract_intent(t)
    flag = "  <== CLARIFY FIRES" if i["confidence"] < 0.7 else ""
    print(f"{t!r}: {i['category']:16} conf={i['confidence']} src={i['source']}{flag}")
