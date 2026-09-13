"""Destination model."""
from datetime import datetime

from sqlalchemy import Boolean, Column, DateTime, Integer, String, Text

from bot.models import Base


class Destination(Base):
    __tablename__ = "destinations"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(128), nullable=False)
    description = Column(Text, nullable=True, default="")
    destination_type = Column(String(32), nullable=False, default="other")
    telegram_url = Column(String(512), nullable=False)
    emoji = Column(String(16), nullable=False, default="🔗")
    button_label = Column(String(64), nullable=False)
    deep_link = Column(String(64), nullable=True)
    active = Column(Boolean, default=True, nullable=False)
    display_order = Column(Integer, default=0, nullable=False)
    click_count = Column(Integer, default=0, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    def __repr__(self) -> str:
        return f"<Destination id={self.id} name={self.name} active={self.active}>"