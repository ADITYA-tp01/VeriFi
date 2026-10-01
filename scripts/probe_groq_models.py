"""Probe which Groq chat model works with the configured keys."""
import json
import sys
import urllib.error
import urllib.request
from pathlib import Path

if sys.stdout.encoding and sys.stdout.encoding.lower() != "utf-8":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from dotenv import load_dotenv  # noqa: E402

load_dotenv()
import os  # noqa: E402

key = os.getenv("GROQ_API_KEY")

candidates = [
    "llama-3.1-8b-instant",
    "llama-3.1-70b-versatile",
    "llama3-70b-8192",
    "llama3-8b-8192",
    "gemma2-9b-it",
    "llama-3.3-70b-versatile",
    "openai/gpt-oss-20b",
    "moonshotai/kimi-k2-instruct",
    "qwen/qwen3-32b",
    "deepseek-r1-distill-llama-70b",
]

working = []
for m in candidates:
    body = json.dumps(
        {"model": m, "messages": [{"role": "user", "content": "say OK"}],
         "max_tokens": 10, "temperature": 0}
    ).encode()
    req = urllib.request.Request(
        "https://api.groq.com/openai/v1/chat/completions",
        data=body,
        headers={"Authorization": f"Bearer {key}", "Content-Type": "application/json"},
    )
    try:
        with urllib.request.urlopen(req, timeout=20) as r:
            d = json.loads(r.read().decode())
        reply = d["choices"][0]["message"]["content"][:30]
        print(f"WORKS : {m} -> {reply}")
        working.append(m)
    except urllib.error.HTTPError as e:
        msg = e.read().decode()[:70]
        print(f"FAIL  : {m} -> {e.code} {msg}")
    except Exception as e:
        print(f"ERROR : {m} -> {e}")

print()
print("WORKING MODELS:", working or "none")
sys.exit(0 if working else 1)
