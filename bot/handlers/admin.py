"""Admin panel handlers."""
import logging

from telegram import Update
from telegram.constants import ParseMode
from telegram.ext import ContextTypes

from bot.config import config
from bot.services import analytics_service, destination_service
from bot.utils.validators import is_valid_telegram_url, normalize_emoji
from bot.utils.helpers import safe_html_escape
from bot.keyboards.admin import (
    admin_active_keyboard,
    admin_back_keyboard,
    admin_confirm_delete_keyboard,
    admin_list_keyboard,
    admin_root_keyboard,
    admin_settings_keyboard,
    admin_type_keyboard,
    admin_view_keyboard,
)

logger = logging.getLogger(__name__)


def _is_admin(user_id: int) -> bool:
    return user_id in config.ADMIN_IDS


async def _guard(update: Update) -> bool:
    user = update.effective_user
    if user is None or not _is_admin(user.id):
        if update.callback_query:
            await update.callback_query.answer("⛔ Not authorized.", show_alert=True)
        return False
    return True


# ------------------ Entry ------------------

async def admin_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not await _guard(update):
        return
    context.user_data.pop("admin_flow", None)
    await update.effective_message.reply_text(
        "⚙️ <b>ADMIN PANEL</b>",
        parse_mode=ParseMode.HTML,
        reply_markup=admin_root_keyboard(),
    )


async def admin_home(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not await _guard(update):
        return
    context.user_data.pop("admin_flow", None)
    q = update.callback_query
    await q.answer()
    try:
        await q.edit_message_text(
            "⚙️ <b>ADMIN PANEL</b>",
            parse_mode=ParseMode.HTML,
            reply_markup=admin_root_keyboard(),
        )
    except Exception as e:
        logger.debug("admin_home: %s", e)


# ------------------ List & View ------------------

async def admin_list(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not await _guard(update):
        return
    q = update.callback_query
    await q.answer()
    dests = destination_service.list_all()
    text = "📋 <b>Destinations</b>\n\nSelect one to manage:" if dests else "📋 No destinations yet."
    try:
        await q.edit_message_text(text=text, parse_mode=ParseMode.HTML,
                                  reply_markup=admin_list_keyboard(dests))
    except Exception as e:
        logger.debug("admin_list: %s", e)


async def admin_view(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not await _guard(update):
        return
    q = update.callback_query
    parts = (q.data or "").split(":")
    if len(parts) != 3 or not parts[2].isdigit():
        await q.answer("Invalid.")
        return
    dest = destination_service.get(int(parts[2]))
    if dest is None:
        await q.answer("Not found.", show_alert=True)
        return
    await q.answer()
    status = "🟢 Active" if dest.active else "🔴 Inactive"
    text = (
        f"{dest.emoji} <b>{safe_html_escape(dest.name)}</b>\n\n"
        f"<b>Type:</b> {safe_html_escape(dest.destination_type)}\n"
        f"<b>Label:</b> {safe_html_escape(dest.button_label)}\n"
        f"<b>Status:</b> {status}\n"
        f"<b>Order:</b> {dest.display_order}\n"
        f"<b>Description:</b> {safe_html_escape(dest.description or '—')}"
    )
    try:
        await q.edit_message_text(text=text, parse_mode=ParseMode.HTML,
                                  reply_markup=admin_view_keyboard(dest.id, dest.active),
                                  disable_web_page_preview=True)
    except Exception as e:
        logger.debug("admin_view: %s", e)


# ------------------ Toggle / Delete ------------------

async def admin_toggle(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not await _guard(update):
        return
    q = update.callback_query
    parts = (q.data or "").split(":")
    if len(parts) != 3 or not parts[2].isdigit():
        await q.answer("Invalid.")
        return
    dest_id = int(parts[2])
    new_state = destination_service.toggle_active(dest_id)
    if new_state is None:
        await q.answer("Not found.", show_alert=True)
        return
    await q.answer("Enabled ✅" if new_state else "Disabled 🚫")
    await admin_view(update, context)


async def admin_delete_prompt(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not await _guard(update):
        return
    q = update.callback_query
    parts = (q.data or "").split(":")
    if len(parts) != 3 or not parts[2].isdigit():
        await q.answer("Invalid.")
        return
    dest_id = int(parts[2])
    await q.answer()
    try:
        await q.edit_message_text(
            "🗑 <b>Confirm deletion</b>\n\nThis cannot be undone.",
            parse_mode=ParseMode.HTML,
            reply_markup=admin_confirm_delete_keyboard(dest_id),
        )
    except Exception as e:
        logger.debug("delete_prompt: %s", e)


async def admin_delete_confirm(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not await _guard(update):
        return
    q = update.callback_query
    parts = (q.data or "").split(":")
    if len(parts) != 3 or not parts[2].isdigit():
        await q.answer("Invalid.")
        return
    ok = destination_service.delete(int(parts[2]))
    await q.answer("Deleted ✅" if ok else "Not found.", show_alert=not ok)
    await admin_list(update, context)


# ------------------ Statistics ------------------

async def admin_stats(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not await _guard(update):
        return
    q = update.callback_query
    await q.answer()
    stats = analytics_service.get_stats()
    top_lines = "\n".join(f"{label} — <b>{count}</b> clicks" for label, _name, count in stats["top"]) or "—"
    text = (
        "📊 <b>STATISTICS</b>\n\n"
        f"👥 <b>Total users:</b> {stats['total_users']}\n"
        f"🖱 <b>Total clicks:</b> {stats['total_clicks']}\n"
        f"📅 <b>Today:</b> {stats['today_clicks']}\n"
        f"🗓 <b>This week:</b> {stats['week_clicks']}\n"
        f"📆 <b>This month:</b> {stats['month_clicks']}\n\n"
        f"🏆 <b>Top destinations</b>\n{top_lines}"
    )
    try:
        await q.edit_message_text(text=text, parse_mode=ParseMode.HTML,
                                  reply_markup=admin_back_keyboard())
    except Exception as e:
        logger.debug("admin_stats: %s", e)


# ------------------ Settings ------------------

async def admin_settings(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not await _guard(update):
        return
    q = update.callback_query
    await q.answer()
    text = (
        "⚙️ <b>Settings</b>\n\n"
        f"Support username: <code>{safe_html_escape(config.SUPPORT_USERNAME or '—')}</code>\n"
        f"Admins configured: <b>{len(config.ADMIN_IDS)}</b>"
    )
    try:
        await q.edit_message_text(text=text, parse_mode=ParseMode.HTML,
                                  reply_markup=admin_settings_keyboard())
    except Exception as e:
        logger.debug("admin_settings: %s", e)


# ------------------ Add Destination Flow ------------------

async def admin_add_start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not await _guard(update):
        return
    q = update.callback_query
    await q.answer()
    context.user_data["admin_flow"] = {"step": "name", "data": {}}
    try:
        await q.edit_message_text(
            "➕ <b>Add Destination</b>\n\n<b>Step 1/7:</b> Send the destination <b>name</b>.",
            parse_mode=ParseMode.HTML,
            reply_markup=admin_back_keyboard(),
        )
    except Exception as e:
        logger.debug("add_start: %s", e)


async def admin_flow_text(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handles all text-input steps of the Add Destination flow."""
    if not await _guard(update):
        return
    flow = context.user_data.get("admin_flow")
    if not flow:
        return

    step = flow["step"]
    data = flow["data"]
    text = (update.message.text or "").strip()

    if step == "name":
        if len(text) < 2:
            await update.message.reply_text("Name too short. Try again:")
            return
        data["name"] = text[:128]
        flow["step"] = "type"
        await update.message.reply_text(
            "📂 <b>Step 2/7:</b> Choose the type:",
            parse_mode=ParseMode.HTML,
            reply_markup=admin_type_keyboard(),
        )
        return

    if step == "url":
        if not is_valid_telegram_url(text):
            await update.message.reply_text(
                "❌ Invalid Telegram URL.\nMust start with https://t.me/ or https://telegram.me/\n\nTry again:"
            )
            return
        data["telegram_url"] = text
        flow["step"] = "label"
        await update.message.reply_text("🔤 <b>Step 4/7:</b> Send the button label.",
                                        parse_mode=ParseMode.HTML)
        return

    if step == "label":
        if not text:
            await update.message.reply_text("Label cannot be empty. Try again:")
            return
        data["button_label"] = text[:64]
        flow["step"] = "emoji"
        await update.message.reply_text("😀 <b>Step 5/7:</b> Send an emoji.",
                                        parse_mode=ParseMode.HTML)
        return

    if step == "emoji":
        data["emoji"] = normalize_emoji(text)
        flow["step"] = "description"
        await update.message.reply_text("📝 <b>Step 6/7:</b> Send a short description.",
                                        parse_mode=ParseMode.HTML)
        return

    if step == "description":
        data["description"] = text[:400]
        flow["step"] = "active"
        await update.message.reply_text(
            "✅ <b>Step 7/7:</b> Should it be active now?",
            parse_mode=ParseMode.HTML,
            reply_markup=admin_active_keyboard(),
        )
        return


async def admin_flow_type(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handles the type-selection callback."""
    if not await _guard(update):
        return
    q = update.callback_query
    flow = context.user_data.get("admin_flow")
    if not flow or flow.get("step") != "type":
        await q.answer()
        return
    dest_type = (q.data or "").split(":")[-1]
    flow["data"]["destination_type"] = dest_type
    flow["step"] = "url"
    await q.answer()
    try:
        await q.edit_message_text(
            "🔗 <b>Step 3/7:</b> Send the Telegram URL\n"
            "(must be https://t.me/... — it will stay hidden behind the button).",
            parse_mode=ParseMode.HTML,
        )
    except Exception as e:
        logger.debug("flow_type: %s", e)


async def admin_flow_active(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handles final active/inactive selection and saves the destination."""
    if not await _guard(update):
        return
    q = update.callback_query
    flow = context.user_data.get("admin_flow")
    if not flow or flow.get("step") != "active":
        await q.answer()
        return
    active = (q.data or "").endswith(":yes")
    data = flow["data"]

    try:
        dest = destination_service.create(
            name=data["name"],
            description=data.get("description", ""),
            destination_type=data.get("destination_type", "other"),
            telegram_url=data["telegram_url"],
            emoji=data.get("emoji", "🔗"),
            button_label=data["button_label"],
            active=active,
        )
    except Exception as e:
        logger.exception("Failed creating destination: %s", e)
        await q.answer("Save failed.", show_alert=True)
        return

    context.user_data.pop("admin_flow", None)
    await q.answer("Saved ✅")
    try:
        await q.edit_message_text(
            f"✅ <b>Saved</b>\n\n{dest.emoji} {safe_html_escape(dest.name)}",
            parse_mode=ParseMode.HTML,
            reply_markup=admin_root_keyboard(),
        )
    except Exception as e:
        logger.debug("flow_active: %s", e)


# ------------------ Inline Edit Flow ------------------

async def admin_edit_start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not await _guard(update):
        return
    q = update.callback_query
    parts = (q.data or "").split(":")
    if len(parts) != 4 or not parts[2].isdigit():
        await q.answer("Invalid.")
        return
    dest_id = int(parts[2])
    field = parts[3]
    context.user_data["admin_flow"] = {"step": "edit_value", "dest_id": dest_id, "field": field}
    await q.answer()
    try:
        await q.edit_message_text(
            f"✏️ Send the new value for <b>{safe_html_escape(field)}</b>:",
            parse_mode=ParseMode.HTML,
            reply_markup=admin_back_keyboard(),
        )
    except Exception as e:
        logger.debug("edit_start: %s", e)


async def admin_edit_apply(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not await _guard(update):
        return
    flow = context.user_data.get("admin_flow")
    if not flow or flow.get("step") != "edit_value":
        return

    field = flow["field"]
    dest_id = flow["dest_id"]
    raw = (update.message.text or "").strip()

    value: object = raw
    if field == "telegram_url":
        if not is_valid_telegram_url(raw):
            await update.message.reply_text("❌ Invalid Telegram URL. Try again:")
            return
    elif field == "emoji":
        value = normalize_emoji(raw)
    elif field == "display_order":
        if not raw.isdigit():
            await update.message.reply_text("❌ Must be a number. Try again:")
            return
        value = int(raw)

    ok = destination_service.update(dest_id, **{field: value})
    context.user_data.pop("admin_flow", None)
    await update.message.reply_text(
        "✅ Updated." if ok else "❌ Destination not found.",
        reply_markup=admin_root_keyboard(),
    )