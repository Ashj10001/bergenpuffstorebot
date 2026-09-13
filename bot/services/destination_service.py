"""Destination CRUD + seed data."""
import logging
from typing import List, Optional

from sqlalchemy import select

from bot.database import get_session
from bot.models.destination import Destination

logger = logging.getLogger(__name__)

DEFAULT_DESTINATIONS = [
    {
        "name": "Bergenpuff Store Official Channel",
        "description": "Get the latest official updates from Bergenpuff Store.",
        "destination_type": "channel",
        "telegram_url": "https://t.me/+zt2vLsddWi9jMGI0",
        "emoji": "📢",
        "button_label": "Official Channel",
        "deep_link": "channel",
        "active": True,
        "display_order": 1,
    },
    {
        "name": "Bergenpuff Store Community Group",
        "description": "Connect and interact with the Bergenpuff Store community.",
        "destination_type": "group",
        "telegram_url": "https://t.me/+3cs1A8bpS8AwOWQ0",
        "emoji": "💬",
        "button_label": "Community Group",
        "deep_link": "group",
        "active": True,
        "display_order": 2,
    },
]


def seed_defaults() -> None:
    with get_session() as session:
        for data in DEFAULT_DESTINATIONS:
            existing = session.execute(select(Destination).where(Destination.telegram_url == data["telegram_url"])).scalar_one_or_none()
            if existing is None:
                session.add(Destination(**data))
                logger.info("Seeded destination: %s", data["name"])


def _detach_all(session, rows):
    for r in rows:
        session.expunge(r)
    return rows


def list_active() -> List[Destination]:
    with get_session() as session:
        rows = session.execute(select(Destination).where(Destination.active.is_(True)).order_by(Destination.display_order.asc(), Destination.id.asc())).scalars().all()
        return _detach_all(session, list(rows))


def list_all() -> List[Destination]:
    with get_session() as session:
        rows = session.execute(select(Destination).order_by(Destination.display_order.asc(), Destination.id.asc())).scalars().all()
        return _detach_all(session, list(rows))


def get(destination_id: int) -> Optional[Destination]:
    with get_session() as session:
        dest = session.get(Destination, destination_id)
        if dest is not None:
            session.expunge(dest)
        return dest


def get_by_deep_link(deep_link: str) -> Optional[Destination]:
    with get_session() as session:
        dest = session.execute(select(Destination).where(Destination.deep_link == deep_link, Destination.active.is_(True))).scalar_one_or_none()
        if dest is not None:
            session.expunge(dest)
        return dest


def create(name, description, destination_type, telegram_url, emoji, button_label, active=True, display_order=None):
    with get_session() as session:
        if display_order is None:
            existing = session.execute(select(Destination.display_order)).scalars().all()
            display_order = (max(existing) + 1) if existing else 1
        dest = Destination(name=name, description=description, destination_type=destination_type, telegram_url=telegram_url, emoji=emoji, button_label=button_label, active=active, display_order=display_order)
        session.add(dest)
        session.flush()
        session.refresh(dest)
        session.expunge(dest)
        return dest


def update(destination_id, **fields):
    with get_session() as session:
        dest = session.get(Destination, destination_id)
        if dest is None:
            return False
        for k, v in fields.items():
            if hasattr(dest, k):
                setattr(dest, k, v)
        return True


def delete(destination_id):
    with get_session() as session:
        dest = session.get(Destination, destination_id)
        if dest is None:
            return False
        session.delete(dest)
        return True


def toggle_active(destination_id):
    with get_session() as session:
        dest = session.get(Destination, destination_id)
        if dest is None:
            return None
        dest.active = not dest.active
        return dest.active

