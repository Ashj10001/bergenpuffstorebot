"""Main menu callbacks."""
import logging

from telegram import Update
from telegram.constants import ParseMode
from telegram.ext import ContextTypes

from bot.config import config
from bot.services import destination_service
from bot.keyboards.user import main_menu_keyboard

logger = logging.getLogger(__name__)

WELCOME_TEXT = (
    "🌿 <b>BERGENPUFF STORE</b>\n"
    "\n"
    "Welcome! 👋\n"
    "\n"
    "Explore our official Telegram spaces and choose where you'd like to go."
)


async def menu_home(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    if query is None:
        return
    await query.answer()
    destinations = destination_service.list_active()
    try:
        await query.edit_message_text(
            text=WELCOME_TEXT,
            parse_mode=ParseMode.HTML,
            reply_markup=main_menu_keyboard(destinations, config.SUPPORT_USERNAME),
            disable_web_page_preview=True,
        )
    except Exception as e:
        logger.debug("menu_home edit failed: %s", e)