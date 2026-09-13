"""Generic key-value settings model."""
from datetime import datetime

from sqlalchemy import Column, DateTime, String, Text

from bot.models import Base


class BotSetting(Base):
    __tablename__ = "bot_settings"

    key = Column(String(64), primary_key=True)
    value = Column(Text, nullable=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self) -> str:
        return f"<BotSetting {self.key}={self.value}>"
