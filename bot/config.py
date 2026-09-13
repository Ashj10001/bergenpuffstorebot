"""Configuration loader using environment variables."""
import os
from dotenv import load_dotenv

load_dotenv()


def _parse_admin_ids(raw: str) -> set[int]:
    ids: set[int] = set()
    if not raw:
        return ids
    for part in raw.split(","):
        part = part.strip()
        if part.isdigit():
            ids.add(int(part))
    return ids


class Config:
    BOT_TOKEN: str = os.getenv("BOT_TOKEN", "").strip()
    ADMIN_IDS: set[int] = _parse_admin_ids(os.getenv("ADMIN_IDS", ""))
    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///bergenpuff.db").strip()
    SUPPORT_USERNAME: str = os.getenv("SUPPORT_USERNAME", "").strip().lstrip("@")

    @classmethod
    def validate(cls) -> None:
        if not cls.BOT_TOKEN:
            raise RuntimeError(
                "BOT_TOKEN is not set. Add it to your environment variables."
            )
        if not cls.ADMIN_IDS:
            raise RuntimeError(
                "ADMIN_IDS is empty. Set at least one numeric Telegram ID."
            )


config = Config()
