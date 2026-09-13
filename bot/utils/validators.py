"""Validation helpers."""
import re

TELEGRAM_URL_RE = re.compile(
    r"^https?://(t\.me|telegram\.me)/.+$", re.IGNORECASE
)


def is_valid_telegram_url(url: str) -> bool:
    if not url or not isinstance(url, str):
        return False
    return bool(TELEGRAM_URL_RE.match(url.strip()))


def normalize_emoji(raw: str) -> str:
    raw = (raw or "").strip()
    if not raw:
        return "🔗"
    return raw[:4]
