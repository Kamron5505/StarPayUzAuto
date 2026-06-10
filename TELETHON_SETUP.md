# 🎁 Настройка отправки подарков через Telethon

## Что это?

Telethon — это библиотека для работы с Telegram API как **user-клиент** (не бот). Это позволяет отправлять подарки от имени обычного аккаунта.

---

## 📋 Шаг 1: Получить API_ID и API_HASH

1. Зайти на **https://my.telegram.org/apps**
2. Войти через свой Telegram аккаунт
3. Создать новое приложение:
   - **App title**: StarPayUz
   - **Short name**: starpayuz
   - **Platform**: Other
4. Скопировать:
   - **API ID** (например: `12345678`)
   - **API Hash** (например: `abc123def456...`)

---

## 📋 Шаг 2: Добавить в .env

Откройте файл `.env` и добавьте:

```env
# Telethon (для отправки подарков)
API_ID=12345678
API_HASH=your_api_hash_here
PHONE_NUMBER=+998901234567
SESSION_NAME=starpay_session
```

**Важно:**
- `PHONE_NUMBER` — номер телефона Telegram аккаунта, от которого будут отправляться подарки
- Это должен быть **активный аккаунт** (не бот!)
- При первом запуске Telegram попросит код подтверждения

---

## 📋 Шаг 3: Установить зависимости

```bash
pip install -r requirements.txt
```

Или вручную:

```bash
pip install telethon>=1.36.0
```

---

## 📋 Шаг 4: Первый запуск (авторизация)

При первом запуске бота Telethon попросит:

1. **Код подтверждения** (придет в Telegram на указанный номер)
2. **2FA пароль** (если включен)

```bash
python bot.py
```

Вы увидите:

```
Please enter the code you received: 12345
```

Введите код из Telegram и нажмите Enter.

После успешной авторизации создастся файл сессии (`starpay_session.session`) — **НЕ УДАЛЯЙТЕ ЕГО** и **НЕ КОММИТЬТЕ В GIT!**

---

## 📋 Шаг 5: Получить ID подарков

ID подарков можно получить через Telegram Bot API или вручную.

**Текущие подарки в коде** (нужно обновить на реальные):

```python
gift_mapping = {
    "bear": "premium_gift_bear",
    "rose": "premium_gift_rose",
    "cake": "premium_gift_cake",
    "diamond": "premium_gift_diamond",
    "heart": "premium_gift_heart",
    "ring": "premium_gift_ring",
    "rocket": "premium_gift_rocket",
    "trophy": "premium_gift_trophy",
}
```

Чтобы получить реальные ID:

1. Запустить скрипт для получения доступных подарков
2. Или использовать Telegram API напрямую

---

## 🔒 Безопасность

**⚠️ ВАЖНО:**

1. **Файл сессии** (`starpay_session.session`) содержит авторизацию:
   - Добавьте `*.session` в `.gitignore`
   - НЕ публикуйте его
   
2. **API_HASH** — это секретный ключ:
   - Храните в `.env`
   - НЕ коммитьте в репозиторий

3. **Rate limits:**
   - Telegram ограничивает количество запросов
   - При FloodWait нужно ждать указанное время

---

## 🧪 Тестирование

После настройки протестируйте отправку подарка:

```python
from services.telethon_client import gift_sender

result = await gift_sender.send_gift(
    username="test_user",
    gift_sticker_id="premium_gift_bear",
    message="🎁 Test gift from StarPayUz"
)

print(result)
```

---

## ❓ Troubleshooting

### 1. "API_ID and API_HASH are required"

→ Проверьте `.env` файл и убедитесь, что переменные установлены.

### 2. "Username not found"

→ Пользователь не существует или username неправильный.

### 3. "FloodWait"

→ Слишком много запросов. Подождите указанное время.

### 4. "Telethon client not connected"

→ Клиент не запущен. Проверьте логи запуска бота.

---

## 📚 Полезные ссылки

- **Telethon документация**: https://docs.telethon.dev/
- **Telegram API**: https://core.telegram.org/api
- **My Telegram Apps**: https://my.telegram.org/apps
