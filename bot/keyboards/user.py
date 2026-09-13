"""User-facing inline keyboards."""
from typing import List

from telegram import InlineKeyboardButton, InlineKeyboardMarkup

from bot.models.destination import Destination

BACK_TO_MENU = InlineKeyboardButton("⬅️ Back to Menu", callback_data="menu:home")
ABOUT_BUTTON = InlineKeyboardButton("ℹ️ About Us", callback_data="menu:about")
CONTACT_BUTTON = InlineKeyboardButton("📞 Contact", callback_data="menu:contact")


def main_menu_keyboard(
    destinations: List[Destination],
    support_username: str = "",
) -> InlineKeyboardMarkup:
    """Build the main menu.

    Each destination becomes a Telegram URL button so the URL stays hidden.
    """
    rows: List[List[InlineKeyboardButton]] = []

    for dest in destinations:
        label = f"{dest.emoji} {dest.button_label}".strip()
        rows.append([InlineKeyboardButton(label, url=dest.telegram_url)])

    # Footer row: About + Contact
    footer = [ABOUT_BUTTON]
    if support_username:
        footer.append(
            InlineKeyboardButton(
                "📞 Contact", url=f"https://t.me/{support_username}"
            )
        )
    else:
        footer.append(CONTACT_BUTTON)

    rows.append(footer)
    return InlineKeyboardMarkup(rows)


def about_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup([[BACK_TO_MENU]])


def contact_keyboard(support_username: str = "") -> InlineKeyboardMarkup:
    rows = []
    if support_username:
        rows.append(
            [
                InlineKeyboardButton(
                    "📩 Open Support Chat",
                    url=f"https://t.me/{support_username}",
                )
            ]
        )
    rows.append([BACK_TO_MENU])
    return InlineKeyboardMarkup(rows)


def destination_detail_keyboard(dest: Destination) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        [
            [InlineKeyboardButton(f"{dest.emoji} Open {dest.button_label}", url=dest.telegram_url)],
            [InlineKeyboardButton("⬅️ Back", callback_data="menu:home")],
        ]
    )