"""Verify the intent-extractor call pattern works with openai/gpt-oss-120b."""
import json
import sys
from pathlib import Path

if sys.stdout.encoding and sys.stdout.encoding.lower() != "utf-8":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from dotenv import load_dotenv  # noqa: E402

load_dotenv()
import os  # noqa: E402

from groq import Groq  # noqa: E402

MODEL = "openai/gpt-oss-120b"
client = Groq(api_key=os.getenv("GROQ_API_KEY"))

system = 'Reply ONLY as JSON: {"category": "NEUTRAL", "confidence": 0.5}'
user = "hello there"

attempts = [
    ("temp0 + json_object", dict(temperature=0, response_format={"type": "json_object"})),
    ("temp0 only", dict(temperature=0)),
    ("temp1 only", dict(temperature=1)),
    ("defaults", dict()),
]
for label, kwargs in attempts:
    try:
        r = client.chat.completions.create(
            model=MODEL,
            messages=[{"role": "system", "content": system},
                      {"role": "user", "content": user}],
            max_tokens=400,
            **kwargs,
        )
        raw = r.choices[0].message.content
        data = json.loads(raw)
        print(f"OK   {label} -> {data}")
    except Exception as e:
        print(f"FAIL {label} -> {str(e)[:140]}")

# Also verify backup key works with same call
print()
try:
    c2 = Groq(api_key=os.getenv("GROQ_API_KEY_BACKUP"))
    r = c2.chat.completions.create(model=MODEL,
        messages=[{"role": "user", "content": "Reply exactly: OK"}],
        max_tokens=300, temperature=0)
    print("BACKUP key ->", r.choices[0].message.content.strip())
except Exception as e:
    print("BACKUP FAIL:", str(e)[:140])
