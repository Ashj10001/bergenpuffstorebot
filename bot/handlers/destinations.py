"""Click tracking for destination detail views."""
import logging

from telegram import Update
from telegram.ext import ContextTypes

from bot.services import analytics_service, destination_service

logger = logging.getLogger(__name__)


async def on_destination_open(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Optional soft-tracking callback.

    Triggered via callback_data="dest:open:<id>". URL buttons do not
    generate callbacks in Telegram, so this is used only if a
    destination is opened via the detail page.
    """
    query = update.callback_query
    if query is None:
        return
    data = query.data or ""
    parts = data.split(":")
    if len(parts) != 3 or not parts[2].isdigit():
        await query.answer()
        return

    dest_id = int(parts[2])
    dest = destination_service.get(dest_id)
    if dest is None or not dest.active:
        await query.answer("This destination is no longer available.", show_alert=True)
        return

    analytics_service.track_click(dest_id, query.from_user.id)
    await query.answer()