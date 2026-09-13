"""Click event model for analytics."""
from datetime import datetime

from sqlalchemy import BigInteger, Column, DateTime, ForeignKey, Integer
from sqlalchemy.orm import relationship

from bot.models import Base


class ClickEvent(Base):
    __tablename__ = "click_events"

    id = Column(Integer, primary_key=True, autoincrement=True)
    destination_id = Column(Integer, ForeignKey("destinations.id"), nullable=False, index=True)
    user_id = Column(BigInteger, nullable=False, index=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)

    destination = relationship("Destination", lazy="joined")

    def __repr__(self) -> str:
        return f"<ClickEvent dest={self.destination_id} user={self.user_id}>"