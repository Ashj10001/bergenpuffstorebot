"""Analytics: click tracking + statistics."""
from datetime import datetime, timedelta
from typing import Dict, List, Tuple

from sqlalchemy import func, select

from bot.database import get_session
from bot.models.click import ClickEvent
from bot.models.destination import Destination
from bot.models.user import User


def track_click(destination_id: int, user_id: int) -> None:
    with get_session() as session:
        session.add(ClickEvent(destination_id=destination_id, user_id=user_id))
        dest = session.get(Destination, destination_id)
        if dest:
            dest.click_count = (dest.click_count or 0) + 1


def _count_since(session, since: datetime) -> int:
    return session.execute(
        select(func.count(ClickEvent.id)).where(ClickEvent.created_at >= since)
    ).scalar_one()


def get_stats() -> Dict:
    now = datetime.utcnow()
    today_start = datetime(now.year, now.month, now.day)
    week_start = now - timedelta(days=7)
    month_start = now - timedelta(days=30)

    with get_session() as session:
        total_users = session.execute(select(func.count(User.id))).scalar_one()
        total_clicks = session.execute(select(func.count(ClickEvent.id))).scalar_one()
        today_clicks = _count_since(session, today_start)
        week_clicks = _count_since(session, week_start)
        month_clicks = _count_since(session, month_start)

        top_rows = session.execute(
            select(Destination.id, Destination.name, Destination.emoji, Destination.button_label)
            .order_by(Destination.click_count.desc())
            .limit(5)
        ).all()

    top: List[Tuple[str, str, int]] = []
    for row in top_rows:
        dest_id, name, emoji, label = row
        with get_session() as s2:
            d = s2.get(Destination, dest_id)
            top.append((f"{emoji} {label}", name, d.click_count if d else 0))

    return {
        "total_users": total_users,
        "total_clicks": total_clicks,
        "today_clicks": today_clicks,
        "week_clicks": week_clicks,
        "month_clicks": month_clicks,
        "top": top,
    }