from aiogram.types import (
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    KeyboardButton,
    ReplyKeyboardMarkup,
    WebAppInfo,
)

from bot.config import settings


def _btn(
    text: str,
    *,
    web_app_url: str | None = None,
    callback_data: str | None = None,
    url: str | None = None,
    style: str | None = None,
    icon_custom_emoji_id: str | None = None,
) -> InlineKeyboardButton:
    kwargs: dict = {"text": text}
    if web_app_url:
        kwargs["web_app"] = WebAppInfo(url=web_app_url)
    if callback_data:
        kwargs["callback_data"] = callback_data
    if url:
        kwargs["url"] = url
    if style:
        kwargs["style"] = style
    if icon_custom_emoji_id:
        kwargs["icon_custom_emoji_id"] = icon_custom_emoji_id
    return InlineKeyboardButton(**kwargs)


def main_inline_keyboard() -> InlineKeyboardMarkup:
    base = settings.webapp_base_url
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                _btn(
                    "🌟 Stars olish",
                    web_app_url=f"{base}/app/stars.html",
                    style="primary",
                    icon_custom_emoji_id=settings.custom_emoji_star,
                ),
                _btn(
                    "💎 Premium olish",
                    web_app_url=f"{base}/app/premium.html",
                    style="success",
                    icon_custom_emoji_id=settings.custom_emoji_premium,
                ),
            ],
            [
                _btn(
                    "📞 Nomer olish",
                    web_app_url=f"{base}/app/phone.html",
                    icon_custom_emoji_id=settings.custom_emoji_phone,
                ),
                _btn(
                    "🎁 Gift olish",
                    web_app_url=f"{base}/app/gift.html",
                    icon_custom_emoji_id=settings.custom_emoji_gift,
                ),
            ],
            [
                _btn("📦 Buyurtmalarim", callback_data="orders"),
            ],
            [
                _btn("👥 Referallar", callback_data="referrals"),
                _btn("💸 Hisobni to'ldirish", callback_data="topup", style="success"),
            ],
            [
                _btn("👨‍💻 Qo'llab-quvvatlash", url=settings.support_url),
            ],
        ]
    )


def bottom_reply_keyboard() -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        keyboard=[
            [
                KeyboardButton(text="💰 Narxlar"),
                KeyboardButton(text="📚 Qo'llanma"),
            ],
            [KeyboardButton(text="🔄 Tilni almashtirish")],
        ],
        resize_keyboard=True,
        is_persistent=True,
    )
