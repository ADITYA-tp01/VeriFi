"""VeriFi eval benchmark — 30 scenarios (Plan Part 7). Hermetic: no network, no LLM.

Usage: python tests/run_eval.py
Writes: tests/eval_results.json (numbers for the deck — publish only measured results)
"""
from __future__ import annotations

import io
import json
import os
import sys
import uuid
from pathlib import Path

os.environ["GROQ_API_KEY"] = ""
os.environ["GROQ_API_KEY_BACKUP"] = ""
os.environ["LIVE"] = "0"

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

import qrcode  # noqa: E402
from langgraph.types import Command  # noqa: E402

from agent.graph import app  # noqa: E402

EVAL_SET = ROOT / "tests" / "eval_set.json"
EVAL_RESULTS = ROOT / "tests" / "eval_results.json"

FLAG_LEVELS = ("SUSPICIOUS", "HIGH", "CRITICAL")
HI_LEVELS = ("HIGH", "CRITICAL")


def make_qr_bytes(payload: str) -> bytes:
    buf = io.BytesIO()
    qrcode.make(payload).save(buf, format="PNG")
    return buf.getvalue()


def run_scenario(sc: dict) -> dict:
    text = sc["input"]["text"]
    payload = sc["input"].get("qr_payload")
    cfg = {"configurable": {"thread_id": str(uuid.uuid4())}}

    user_input = {"user_input": text}
    if payload:
        user_input["qr_image"] = make_qr_bytes(payload)

    result = app.invoke(user_input, cfg)
    clarify_fired = "__interrupt__" in result

    if clarify_fired:
        answer = sc["expect"].get("clarify_answer", "pay")
        result = app.invoke(Command(resume=answer), cfg)

    return {
        "id": sc["id"],
        "type": sc["type"],
        "name": sc["name"],
        "score": result.get("score", 0),
        "level": result.get("risk_level"),
        "clarify_fired": clarify_fired,
        "mismatch": bool((result.get("evidence_vector") or {}).get("intent_mechanism_mismatch")),
        "triggers": result.get("triggers") or [],
    }


def check(sc: dict, out: dict) -> bool:
    exp = sc["expect"]
    if sc["type"] == "scam":
        ok = out["level"] in exp.get("level_in", HI_LEVELS) and out["clarify_fired"] == exp.get("clarify", False)
        if "mismatch" in exp:
            ok = ok and out["mismatch"] == exp["mismatch"]
        return ok
    if sc["type"] == "legit":
        ok = out["level"] == "NO_STRONG_INDICATORS" and not out["clarify_fired"]
        return ok
    # edge
    if exp.get("clarify"):
        if not out["clarify_fired"]:
            return False
        if "level_in_after" in exp:
            return out["level"] in exp["level_in_after"]
        return True
    ok = out["level"] in exp.get("level_in", FLAG_LEVELS) and not out["clarify_fired"]
    if "mismatch" in exp:
        ok = ok and out["mismatch"] == exp["mismatch"]
    return ok


def main() -> int:
    data = json.loads(EVAL_SET.read_text(encoding="utf-8"))
    scenarios = data["scenarios"]

    rows = []
    for sc in scenarios:
        out = run_scenario(sc)
        out["pass"] = check(sc, out)
        rows.append(out)
        mark = "PASS" if out["pass"] else "FAIL"
        print(f"[{mark}] {out['id']:<32} score={out['score']:>3}  level={out['level']:<22} clarify={out['clarify_fired']}")

    scams = [r for r in rows if r["type"] == "scam"]
    legits = [r for r in rows if r["type"] == "legit"]
    edges = [r for r in rows if r["type"] == "edge"]

    scams_hi = sum(1 for r in scams if r["level"] in HI_LEVELS)
    scams_flagged = sum(1 for r in scams if r["level"] in FLAG_LEVELS)
    legit_fp = sum(1 for r in legits if r["level"] in FLAG_LEVELS or r["clarify_fired"])
    legit_clean = len(legits) - legit_fp

    clarify_expected = [s for s in scenarios if s["expect"].get("clarify")]
    clarify_ids = {s["id"] for s in clarify_expected}
    clarify_fired = sum(1 for r in rows if r["id"] in clarify_ids and r["clarify_fired"])

    # Confusion matrix (scam vs legit; FLAG = SUSPICIOUS+)
    tp = scams_flagged
    fn = len(scams) - tp
    fp = sum(1 for r in legits if r["level"] in FLAG_LEVELS)
    tn = len(legits) - fp

    edge_pass = sum(1 for r in edges if r["pass"])

    print()
    print("=" * 74)
    print(f"Scams flagged HIGH/CRITICAL : {scams_hi}/{len(scams)}")
    print(f"Scams flagged (any warning) : {scams_flagged}/{len(scams)}")
    print(f"Legit false positives       : {fp}/{len(legits)}")
    print(f"Clarify-loop fired (expected): {clarify_fired}/{len(clarify_expected)}")
    print(f"Edge cases passed           : {edge_pass}/{len(edges)}")
    print("-" * 74)
    print("Confusion matrix (flag = SUSPICIOUS/HIGH/CRITICAL):")
    print(f"                Predicted FLAG   Predicted CLEAN")
    print(f"  Actual SCAM   {tp:>8}         {fn:>8}")
    print(f"  Actual LEGIT  {fp:>8}         {tn:>8}")
    print("-" * 74)
    print(
        f"Eval: {scams_hi}/{len(scams)} scams HIGH/CRITICAL, "
        f"{fp} false positives on legit transfers, "
        f"clarify-loop fired on {clarify_fired}/{len(clarify_expected)} expected cases"
    )
    print("=" * 74)

    results = {
        "summary": {
            "scams_high_critical": f"{scams_hi}/{len(scams)}",
            "scams_any_flag": f"{scams_flagged}/{len(scams)}",
            "legit_false_positives": f"{fp}/{len(legits)}",
            "clarify_expected": f"{clarify_fired}/{len(clarify_expected)}",
            "edge_passed": f"{edge_pass}/{len(edges)}",
            "total_passed": f"{sum(1 for r in rows if r['pass'])}/{len(rows)}",
        },
        "confusion_matrix": {"tp": tp, "fn": fn, "fp": fp, "tn": tn},
        "rows": rows,
    }
    EVAL_RESULTS.write_text(json.dumps(results, indent=2), encoding="utf-8")
    print(f"Saved: {EVAL_RESULTS.relative_to(ROOT)}")

    failed = [r["id"] for r in rows if not r["pass"]]
    if failed:
        print(f"FAILED: {', '.join(failed)}")
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
