"""Admin inline keyboards."""
from typing import List

from telegram import InlineKeyboardButton, InlineKeyboardMarkup

from bot.models.destination import Destination


def admin_root_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        [
            [InlineKeyboardButton("➕ Add Destination", callback_data="admin:add")],
            [InlineKeyboardButton("📋 Manage Destinations", callback_data="admin:list")],
            [
                InlineKeyboardButton("📊 Statistics", callback_data="admin:stats"),
                InlineKeyboardButton("⚙️ Settings", callback_data="admin:settings"),
            ],
            [InlineKeyboardButton("⬅️ Back to Menu", callback_data="menu:home")],
        ]
    )


def admin_list_keyboard(destinations: List[Destination]) -> InlineKeyboardMarkup:
    rows = []
    for d in destinations:
        status = "🟢" if d.active else "🔴"
        rows.append(
            [
                InlineKeyboardButton(
                    f"{status} {d.emoji} {d.name}",
                    callback_data=f"admin:view:{d.id}",
                )
            ]
        )
    rows.append([InlineKeyboardButton("⬅️ Back", callback_data="admin:home")])
    return InlineKeyboardMarkup(rows)


def admin_view_keyboard(dest_id: int, active: bool) -> InlineKeyboardMarkup:
    toggle_label = "🚫 Disable" if active else "✅ Enable"
    return InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton("✏️ Edit Name", callback_data=f"admin:edit:{dest_id}:name"),
                InlineKeyboardButton("🔤 Edit Label", callback_data=f"admin:edit:{dest_id}:button_label"),
            ],
            [
                InlineKeyboardButton("📝 Edit Description", callback_data=f"admin:edit:{dest_id}:description"),
                InlineKeyboardButton("🔗 Edit URL", callback_data=f"admin:edit:{dest_id}:telegram_url"),
            ],
            [
                InlineKeyboardButton("😀 Edit Emoji", callback_data=f"admin:edit:{dest_id}:emoji"),
                InlineKeyboardButton("🔢 Edit Order", callback_data=f"admin:edit:{dest_id}:display_order"),
            ],
            [InlineKeyboardButton(toggle_label, callback_data=f"admin:toggle:{dest_id}")],
            [InlineKeyboardButton("🗑 Delete", callback_data=f"admin:delete:{dest_id}")],
            [InlineKeyboardButton("⬅️ Back", callback_data="admin:list")],
        ]
    )


def admin_type_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton("📢 Channel", callback_data="admin:type:channel"),
                InlineKeyboardButton("💬 Group", callback_data="admin:type:group"),
            ],
            [
                InlineKeyboardButton("⭐ VIP", callback_data="admin:type:vip"),
                InlineKeyboardButton("🤝 Community", callback_data="admin:type:community"),
            ],
            [InlineKeyboardButton("🔗 Other", callback_data="admin:type:other")],
            [InlineKeyboardButton("❌ Cancel", callback_data="admin:home")],
        ]
    )


def admin_active_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton("✅ Active", callback_data="admin:active:yes"),
                InlineKeyboardButton("🚫 Inactive", callback_data="admin:active:no"),
            ]
        ]
    )


def admin_confirm_delete_keyboard(dest_id: int) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton("🗑 Yes, delete", callback_data=f"admin:delete_confirm:{dest_id}"),
                InlineKeyboardButton("❌ Cancel", callback_data=f"admin:view:{dest_id}"),
            ]
        ]
    )


def admin_settings_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        [
            [InlineKeyboardButton("⬅️ Back", callback_data="admin:home")],
        ]
    )


def admin_back_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        [[InlineKeyboardButton("⬅️ Back", callback_data="admin:home")]]
    )