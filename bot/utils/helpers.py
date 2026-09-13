"""Small helpers."""
from datetime import datetime


def utcnow() -> datetime:
    return datetime.utcnow()


def safe_html_escape(text: str) -> str:
    if text is None:
        return ""
    return (
        text.replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
    )
