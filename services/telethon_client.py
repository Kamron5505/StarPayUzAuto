"""Telethon client for sending Telegram gifts"""

import logging
from typing import Any

from telethon import TelegramClient, functions
from telethon.errors import (
    FloodWaitError,
    UserIdInvalidError,
)
from telethon.sessions import StringSession
from telethon.tl.types import InputStickerSetShortName

logger = logging.getLogger(__name__)


class TelethonGiftSender:
    """Отправка подарков через Telegram User Client"""

    def __init__(self, api_id: int, api_hash: str, session: str | StringSession = "session"):
        self.api_id = api_id
        self.api_hash = api_hash
        self.session = session
        self.client: TelegramClient | None = None

    async def start(self, phone: str | None = None):
        """Запуск клиента"""
        if not self.api_id or not self.api_hash:
            raise ValueError("API_ID and API_HASH are required")

        # Если передана строка сессии, используем StringSession
        if isinstance(self.session, str) and len(self.session) > 50:
            session = StringSession(self.session)
        else:
            session = self.session

        self.client = TelegramClient(session, self.api_id, self.api_hash)
        await self.client.start(phone=phone)
        logger.info("Telethon client started successfully")

    async def stop(self):
        """Остановка клиента"""
        if self.client:
            await self.client.disconnect()
            logger.info("Telethon client stopped")

    async def send_gift(
        self, username: str, gift_sticker_id: str, message: str = ""
    ) -> dict[str, Any]:
        """
        Отправка подарка пользователю через Telethon MTProto
        
        Args:
            username: Username получателя (без @)
            gift_sticker_id: ID стикера подарка из Telegram
            message: Опциональное сообщение к подарку
            
        Returns:
            dict с результатом операции
        """
        if not self.client or not self.client.is_connected():
            return {
                "ok": False,
                "error": "Telethon client not connected",
            }

        username = username.lstrip("@")

        try:
            # Получаем пользователя
            try:
                user = await self.client.get_entity(username)
                user_id = user.id
            except Exception as e:
                logger.error(f"User not found: @{username}, error: {e}")
                return {
                    "ok": False,
                    "error": f"Username @{username} topilmadi",
                }

            # Используем payments.sendStarGift для отправки подарка
            from telethon.tl.functions.payments import SendStarGiftRequest
            from telethon.tl.types import InputUser
            
            try:
                # Отправляем подарок через payments.sendStarGift
                result = await self.client(
                    SendStarGiftRequest(
                        user_id=InputUser(user_id=user_id, access_hash=user.access_hash),
                        gift_id=int(gift_sticker_id),
                        hide_name=False,
                        message=message if message else None,
                    )
                )
                
                logger.info(f"Star gift sent to @{username}: {gift_sticker_id}")
                return {
                    "ok": True,
                    "username": username,
                    "gift_id": gift_sticker_id,
                    "result": str(result),
                }
                
            except Exception as e:
                logger.error(f"Failed to send star gift: {e}")
                # Если метод не существует, пробуем альтернативный способ
                if "SendStarGiftRequest" in str(e) or "not found" in str(e).lower():
                    logger.warning("SendStarGiftRequest not available, trying alternative method")
                    # Пробуем отправить через форму покупки подарка
                    try:
                        from telethon.tl.functions.payments import SendStarsFormRequest
                        
                        result = await self.client(
                            SendStarsFormRequest(
                                form_id=int(gift_sticker_id),
                                invoice=None,
                            )
                        )
                        
                        logger.info(f"Gift sent via form to @{username}: {gift_sticker_id}")
                        return {
                            "ok": True,
                            "username": username,
                            "gift_id": gift_sticker_id,
                            "result": str(result),
                        }
                    except Exception as e2:
                        logger.error(f"Alternative method also failed: {e2}")
                
                return {
                    "ok": False,
                    "error": f"Xatolik: {str(e)}",
                }

        except FloodWaitError as e:
            logger.error(f"FloodWait: need to wait {e.seconds}s")
            return {
                "ok": False,
                "error": f"Juda ko'p so'rovlar. {e.seconds} soniya kuting",
                "retry_after": e.seconds,
            }

        except Exception as e:
            logger.exception(f"Failed to send gift: {e}")
            return {
                "ok": False,
                "error": f"Xatolik: {str(e)}",
            }

    async def get_available_gifts(self) -> dict[str, Any]:
        """Получить список доступных подарков"""
        if not self.client or not self.client.is_connected():
            return {"ok": False, "error": "Client not connected"}

        try:
            # Получаем набор стикеров с подарками
            result = await self.client(
                functions.messages.GetStickerSetRequest(
                    stickerset=InputStickerSetShortName(short_name="PremiumGifts"),
                    hash=0,
                )
            )

            gifts = []
            for doc in result.documents:
                gifts.append(
                    {
                        "id": doc.id,
                        "access_hash": doc.access_hash,
                        "emoji": getattr(doc.attributes[0], "alt", "🎁")
                        if doc.attributes
                        else "🎁",
                    }
                )

            return {"ok": True, "gifts": gifts}

        except Exception as e:
            logger.exception(f"Failed to get gifts: {e}")
            return {"ok": False, "error": str(e)}


# Глобальный экземпляр (инициализируется при запуске бота)
gift_sender: TelethonGiftSender | None = None


async def init_gift_sender(api_id: int, api_hash: str, session: str = "", phone: str | None = None):
    """Инициализация отправителя подарков"""
    global gift_sender
    gift_sender = TelethonGiftSender(api_id, api_hash, session or "starpayuz_session")
    await gift_sender.start(phone)
    return gift_sender


async def stop_gift_sender():
    """Остановка отправителя подарков"""
    global gift_sender
    if gift_sender:
        await gift_sender.stop()
