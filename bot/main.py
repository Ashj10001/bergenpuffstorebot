"""Build and run the bot."""
import asyncio
import logging

from telegram import BotCommand
from telegram.ext import (
    Application,
    ApplicationBuilder,
    CallbackQueryHandler,
    CommandHandler,
    MessageHandler,
    filters,
)

from bot.config import config
from bot.database import init_db
from bot.services import destination_service
from bot.handlers import start as start_handlers
from bot.handlers import menu as menu_handlers
from bot.handlers import destinations as dest_handlers
from bot.handlers import admin as admin_handlers
from bot.handlers.errors import error_handler

logger = logging.getLogger(__name__)


async def _post_init(app: Application) -> None:
    await app.bot.set_my_commands(
        [
            BotCommand("start", "Show the main menu"),
            BotCommand("menu", "Show the main menu"),
            BotCommand("about", "About Bergenpuff Store"),
            BotCommand("admin", "Admin panel (admins only)"),
        ]
    )
    me = await app.bot.get_me()
    logger.info("Commands registered. Bot @%s is ready.", me.username)


async def _admin_text_router(update, context):
    """Route incoming text messages to the correct admin flow step."""
    if not update.effective_user or update.effective_user.id not in config.ADMIN_IDS:
        return
    flow = context.user_data.get("admin_flow")
    if not flow:
        return
    if flow.get("step") == "edit_value":
        await admin_handlers.admin_edit_apply(update, context)
    else:
        await admin_handlers.admin_flow_text(update, context)


def build_application() -> Application:
    config.validate()
    init_db()
    destination_service.seed_defaults()

    app = (
        ApplicationBuilder()
        .token(config.BOT_TOKEN)
        .post_init(_post_init)
        .build()
    )

    # Commands
    app.add_handler(CommandHandler("start", start_handlers.start))
    app.add_handler(CommandHandler("menu", start_handlers.start))
    app.add_handler(CommandHandler("about", start_handlers.about))
    app.add_handler(CommandHandler("admin", admin_handlers.admin_command))

    # User callbacks
    app.add_handler(CallbackQueryHandler(menu_handlers.menu_home, pattern=r"^menu:home$"))
    app.add_handler(CallbackQueryHandler(start_handlers.about, pattern=r"^menu:about$"))
    app.add_handler(CallbackQueryHandler(start_handlers.contact, pattern=r"^menu:contact$"))
    app.add_handler(CallbackQueryHandler(dest_handlers.on_destination_open, pattern=r"^dest:open:\d+$"))

    # Admin callbacks
    app.add_handler(CallbackQueryHandler(admin_handlers.admin_home, pattern=r"^admin:home$"))
    app.add_handler(CallbackQueryHandler(admin_handlers.admin_add_start, pattern=r"^admin:add$"))
    app.add_handler(CallbackQueryHandler(admin_handlers.admin_list, pattern=r"^admin:list$"))
    app.add_handler(CallbackQueryHandler(admin_handlers.admin_stats, pattern=r"^admin:stats$"))
    app.add_handler(CallbackQueryHandler(admin_handlers.admin_settings, pattern=r"^admin:settings$"))
    app.add_handler(CallbackQueryHandler(admin_handlers.admin_view, pattern=r"^admin:view:\d+$"))
    app.add_handler(CallbackQueryHandler(admin_handlers.admin_toggle, pattern=r"^admin:toggle:\d+$"))
    app.add_handler(CallbackQueryHandler(admin_handlers.admin_delete_prompt, pattern=r"^admin:delete:\d+$"))
    app.add_handler(CallbackQueryHandler(admin_handlers.admin_delete_confirm, pattern=r"^admin:delete_confirm:\d+$"))
    app.add_handler(CallbackQueryHandler(admin_handlers.admin_flow_type, pattern=r"^admin:type:\w+$"))
    app.add_handler(CallbackQueryHandler(admin_handlers.admin_flow_active, pattern=r"^admin:active:(yes|no)$"))
    app.add_handler(CallbackQueryHandler(admin_handlers.admin_edit_start, pattern=r"^admin:edit:\d+:\w+$"))

    # Admin text-input router (runs in group 1 so it doesn't clash with commands)
    app.add_handler(
        MessageHandler(filters.TEXT & ~filters.COMMAND, _admin_text_router),
        group=1,
    )

    # Errors
    app.add_error_handler(error_handler)

    return app


async def run_bot() -> None:
    app = build_application()
    logger.info("Starting BergenpuffStoreBot (polling)...")
    await app.initialize()
    await app.start()
    await app.updater.start_polling(drop_pending_updates=True)
    try:
        await asyncio.Event().wait()
    finally:
        await app.updater.stop()
        await app.stop()
        await app.shutdown()