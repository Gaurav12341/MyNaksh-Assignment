import base64
import hashlib
import hmac
import json
import os
import secrets
import time
from typing import Any

from app.core.config import get_settings


PBKDF2_ITERATIONS = 210_000
TOKEN_TTL_SECONDS = 60 * 60 * 8


def hash_password(password: str, salt: str | None = None) -> tuple[str, str]:
    salt = salt or secrets.token_hex(16)
    digest = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt.encode("utf-8"), PBKDF2_ITERATIONS)
    return base64.urlsafe_b64encode(digest).decode("ascii"), salt


def verify_password(password: str, password_hash: str, salt: str) -> bool:
    candidate, _ = hash_password(password, salt)
    return hmac.compare_digest(candidate, password_hash)


def create_token(claims: dict[str, Any]) -> str:
    payload = claims | {"iat": int(time.time()), "exp": int(time.time()) + TOKEN_TTL_SECONDS}
    payload_json = json.dumps(payload, separators=(",", ":"), sort_keys=True).encode("utf-8")
    payload_b64 = base64.urlsafe_b64encode(payload_json).decode("ascii").rstrip("=")
    signature = _sign(payload_b64)
    return f"{payload_b64}.{signature}"


def verify_token(token: str) -> dict[str, Any] | None:
    try:
        payload_b64, signature = token.split(".", 1)
    except ValueError:
        return None
    if not hmac.compare_digest(_sign(payload_b64), signature):
        return None
    padded = payload_b64 + "=" * (-len(payload_b64) % 4)
    try:
        payload = json.loads(base64.urlsafe_b64decode(padded.encode("ascii")))
    except (ValueError, json.JSONDecodeError):
        return None
    if int(payload.get("exp", 0)) < int(time.time()):
        return None
    return payload


def _sign(payload_b64: str) -> str:
    secret = get_settings().auth_secret.encode("utf-8")
    digest = hmac.new(secret, payload_b64.encode("ascii"), hashlib.sha256).digest()
    return base64.urlsafe_b64encode(digest).decode("ascii").rstrip("=")


def make_guid() -> str:
    return str(secrets.SystemRandom().randint(0, 2**128 - 1)).zfill(39) if os.getenv("DETERMINISTIC_TEST_GUID") else __import__("uuid").uuid4().hex
