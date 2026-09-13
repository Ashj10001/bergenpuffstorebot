"""User model."""
from datetime import datetime

from sqlalchemy import BigInteger, Column, DateTime, String

from bot.models import Base


class User(Base):
    __tablename__ = "users"

    id = Column(BigInteger, primary_key=True)
    username = Column(String(64), nullable=True)
    first_name = Column(String(128), nullable=True)
    language_code = Column(String(16), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    last_seen_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    def __repr__(self):
        return "<User id=" + str(self.id) + " username=" + str(self.username) + ">"
