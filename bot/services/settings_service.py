"""Bot settings key/value store."""
from typing import Optional

from bot.database import get_session
from bot.models.settings import BotSetting


def get(key: str, default: Optional[str] = None) -> Optional[str]:
    with get_session() as session:
        row = session.get(BotSetting, key)
        return row.value if row else default


def set(key: str, value: str) -> None:  # noqa: A001
    with get_session() as session:
        row = session.get(BotSetting, key)
        if row is None:
            session.add(BotSetting(key=key, value=value))
        else:
            row.value = value