"""Global error handler."""
import logging

from telegram import Update
from telegram.constants import ParseMode
from telegram.ext import ContextTypes

logger = logging.getLogger(__name__)

USER_FRIENDLY_ERROR = (
    "😔 Something went wrong on our side.\n"
    "Please try again in a moment, or use /start to reset."
)


async def error_handler(update: object, context: ContextTypes.DEFAULT_TYPE) -> None:
    logger.exception("Unhandled exception:", exc_info=context.error)

    if not isinstance(update, Update):
        return

    try:
        if update.callback_query:
            await update.callback_query.answer(
                "Something went wrong. Please try again.", show_alert=False
            )
        elif update.effective_message:
            await update.effective_message.reply_text(
                USER_FRIENDLY_ERROR, parse_mode=ParseMode.HTML
            )
    except Exception as e:
        logger.debug("Failed to notify user of error: %s", e)