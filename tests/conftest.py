"""Hermetic tests — no live network (Plan Part 4): no LLM, no live WHOIS."""
import os

os.environ["GROQ_API_KEY"] = ""
os.environ["GROQ_API_KEY_BACKUP"] = ""
os.environ["LIVE"] = "0"
