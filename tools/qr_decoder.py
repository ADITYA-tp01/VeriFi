"""VeriFi QR Decoder — cv2.QRCodeDetector, extracts UPI mechanism (Tier 1).

No pyzbar — native zbar dependency is install hell. Decided. Closed.
"""
from __future__ import annotations

from urllib.parse import parse_qs, urlparse

import cv2
import numpy as np

import qrcode


def decode_qr(image_input) -> dict:
    """Decode a QR code from a file path, bytes, or numpy array.

    Returns {"status": "OK", "payload": str} or {"status": "ERROR", "reason": str}.
    """
    try:
        if isinstance(image_input, (bytes, bytearray)):
            arr = np.frombuffer(image_input, dtype=np.uint8)
            img = cv2.imdecode(arr, cv2.IMREAD_COLOR)
        elif isinstance(image_input, str):
            img = cv2.imread(image_input)
        elif isinstance(image_input, np.ndarray):
            img = image_input
        else:
            return {"status": "ERROR", "reason": "unsupported input type"}

        if img is None:
            return {"status": "ERROR", "reason": "could not read image"}

        detector = cv2.QRCodeDetector()
        data, points, _ = detector.detectAndDecode(img)
        if not data:
            return {"status": "ERROR", "reason": "no QR code found in image"}
        return {"status": "OK", "payload": data}
    except Exception as exc:  # graceful degradation — never crash
        return {"status": "ERROR", "reason": str(exc)}


def extract_mechanism(payload: str) -> dict:
    """Determine what scanning this QR actually does: SEND vs RECEIVE.

    upi://pay?pa=...      -> the scanner PAYS (SEND_MONEY)
    upi://collect?pa=...  -> requests money FROM the scanner (collection)
    anything else         -> UNKNOWN mechanism
    """
    if not payload:
        return {"action": "UNKNOWN", "payload": payload}

    parsed = urlparse(payload)
    scheme = parsed.scheme.lower()

    if scheme == "upi":
        # upi://pay?... -> netloc="pay", path=""; upi:pay?... -> path="pay"
        segment = (parsed.path.strip("/") or parsed.netloc).lower()
        if segment == "pay":
            qs = parse_qs(parsed.query)
            return {
                "action": "SEND_MONEY",  # scanning a pay QR debits the scanner
                "payload": payload,
                "payee": (qs.get("pa") or [""])[0],
                "amount": (qs.get("am") or [""])[0],
                "note": (qs.get("tn") or [""])[0],
            }
        if segment == "collect":
            return {"action": "REQUEST_MONEY", "payload": payload}
        return {"action": "UNKNOWN", "payload": payload}

    if scheme in ("http", "https"):
        return {"action": "LINK", "payload": payload, "url": payload}

    return {"action": "UNKNOWN", "payload": payload}


def generate_qr(payload: str, out_path: str) -> str:
    """Generate a QR image for a payload (used to build fixtures)."""
    img = qrcode.make(payload)
    img.save(out_path)
    return out_path
