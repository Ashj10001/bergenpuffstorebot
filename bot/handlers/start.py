"""Handlers for /start and registration of users."""
import logging
from datetime import datetime

from telegram import Update
from telegram.constants import ParseMode
from telegram.ext import ContextTypes

from bot.config import config
from bot.database import get_session
from bot.models.user import User
from bot.services import destination_service
from bot.keyboards.user import (
    main_menu_keyboard,
    destination_detail_keyboard,
    about_keyboard,
    contact_keyboard,
)
from bot.utils.helpers import safe_html_escape

logger = logging.getLogger(__name__)

WELCOME_TEXT = (
    "🌿 <b>BERGENPUFF STORE</b>\n"
    "\n"
    "Welcome! 👋\n"
    "\n"
    "Explore our official Telegram spaces and choose where you'd like to go."
)

ABOUT_TEXT = (
    "🌿 <b>BERGENPUFF STORE</b>\n"
    "\n"
    "Welcome to Bergenpuff Store.\n"
    "\n"
    "This bot provides a simple way to discover and access our official Telegram spaces.\n"
    "\n"
    "Choose a destination from the menu to connect with the community or receive updates."
)


def _upsert_user(update: Update) -> None:
    tg_user = update.effective_user
    if tg_user is None:
        return
    with get_session() as session:
        user = session.get(User, tg_user.id)
        if user is None:
            session.add(
                User(
                    id=tg_user.id,
                    username=tg_user.username,
                    first_name=tg_user.first_name,
                    language_code=tg_user.language_code,
                )
            )
        else:
            user.username = tg_user.username
            user.first_name = tg_user.first_name
            user.language_code = tg_user.language_code
            user.last_seen_at = datetime.utcnow()


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    _upsert_user(update)

    # Deep link handling: /start channel | /start group
    args = context.args or []
    deep = args[0].lower() if args else None

    if deep:
        dest = destination_service.get_by_deep_link(deep)
        if dest is not None:
            text = (
                f"{dest.emoji} <b>{safe_html_escape(dest.name)}</b>\n"
                "\n"
                f"{safe_html_escape(dest.description or '')}\n"
                "\n"
                "Tap the button below to continue."
            )
            await update.effective_message.reply_text(
                text=text,
                parse_mode=ParseMode.HTML,
                reply_markup=destination_detail_keyboard(dest),
                disable_web_page_preview=True,
            )
            return

    destinations = destination_service.list_active()
    await update.effective_message.reply_text(
        text=WELCOME_TEXT,
        parse_mode=ParseMode.HTML,
        reply_markup=main_menu_keyboard(destinations, config.SUPPORT_USERNAME),
        disable_web_page_preview=True,
    )


async def about(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    if query:
        await query.answer()
        await query.edit_message_text(
            text=ABOUT_TEXT,
            parse_mode=ParseMode.HTML,
            reply_markup=about_keyboard(),
            disable_web_page_preview=True,
        )
    else:
        await update.effective_message.reply_text(
            text=ABOUT_TEXT,
            parse_mode=ParseMode.HTML,
            reply_markup=about_keyboard(),
            disable_web_page_preview=True,
        )


async def contact(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    text = (
        "📞 <b>Contact</b>\n"
        "\n"
        "Need help? Reach out to our support team."
    )
    kb = contact_keyboard(config.SUPPORT_USERNAME)
    if query:
        await query.answer()
        await query.edit_message_text(text=text, parse_mode=ParseMode.HTML, reply_markup=kb)
    else:
        await update.effective_message.reply_text(
            text=text, parse_mode=ParseMode.HTML, reply_markup=kb
        )