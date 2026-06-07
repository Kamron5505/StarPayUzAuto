# StarPayUz - Telegram Bot

🤖 Telegram bot для автоматической покупки Telegram Stars, Premium и других услуг.

## Особенности

✨ **Основной функционал:**
- ⭐ Покупка Telegram Stars
- 💎 Покупка Telegram Premium (с premium emoji)
- 📱 Virtual номера (в разработке)
- 🎁 Gift подарки (в разработке)
- 💰 Пополнение баланса
- 👥 Реферальная система
- 📦 История заказов

🎨 **Дизайн:**
- Цветные кнопки с использованием Telegram Bot API 9.4
- Premium emoji для премиум функций
- Адаптивный Web App интерфейс
- Градиентные кнопки по типам услуг

## Установка

1. **Клонировать репозиторий:**
```bash
cd D:\StarPayUzAuto
```

2. **Установить зависимости:**
```bash
pip install -r requirements.txt
```

3. **Настроить .env файл:**
Файл `.env` уже создан с вашими данными:
- BOT_TOKEN - токен вашего бота
- FRAGMENT_API_KEY - API ключ fragment-api.uz
- SHOP_ID и SHOP_KEY - для обработки платежей

4. **Обновить config.py:**
Добавьте свой Telegram ID в список ADMINS:
```python
ADMINS = [your_telegram_id]
```

## Запуск

### Запуск бота:
```bash
python bot.py
```

### Запуск webhook сервера (для обработки платежей):
```bash
python webhook_server.py
```

Webhook сервер будет доступен на `http://localhost:8080`

## Структура проекта

```
StarPayUzAuto/
├── bot.py                 # Основной файл бота
├── config.py             # Конфигурация
├── database.py           # Модели базы данных
├── api_client.py         # Клиент для fragment-api.uz
├── keyboards.py          # Клавиатуры бота
├── webhook_server.py     # Сервер для обработки платежей
├── handlers/
│   ├── start.py         # Обработчик команды /start
│   ├── shop.py          # Обработчики покупок
│   ├── balance.py       # Обработчики баланса
│   └── profile.py       # Профиль и реферралы
├── webapp/
│   └── index.html       # Web App интерфейс
├── .env                 # Переменные окружения
└── requirements.txt     # Зависимости

```

## API Integration

Бот интегрирован с **fragment-api.uz** для:
- Создания платежных ссылок
- Проверки статуса платежей
- Покупки Telegram Stars
- Покупки Telegram Premium

### Методы API:

- `create_payment()` - создать платеж
- `check_payment()` - проверить статус платежа
- `buy_stars()` - купить Stars
- `buy_premium()` - купить Premium

## База данных

Используется SQLite с async SQLAlchemy. Таблицы:

- **users** - пользователи бота
- **orders** - заказы
- **transactions** - транзакции

## Web App

Web App доступен по адресу: `http://your-domain.com/webapp/index.html`

Обновите `WEBAPP_URL` в `.env` после деплоя.

## Deployment

### Для деплоя на VPS:

1. Установите Python 3.11+
2. Настройте reverse proxy (nginx) для webhook сервера
3. Используйте systemd для автозапуска бота
4. Настройте SSL сертификат для webhook

### Пример nginx конфига:

```nginx
server {
    listen 80;
    server_name your-domain.com;

    location /payment/ {
        proxy_pass http://localhost:8080;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }

    location /webapp/ {
        proxy_pass http://localhost:8080;
    }
}
```

## Цветовая схема кнопок

- ⭐ **Stars**: Золотой градиент (#FFD700 → #FFA500)
- 💎 **Premium**: Синий градиент (#00BFFF → #1E90FF)
- 📱 **Phone**: Серый градиент (#808080 → #696969)
- 🎁 **Gift**: Розовый градиент (#FF69B4 → #FF1493)

## Безопасность

- Все платежные коллбэки проверяются через подпись
- Данные пользователей защищены
- Используется HTTPS для webhook

## Поддержка

Telegram: @StarPayUz_Admin
Email: support@starpayuz.com

## Лицензия

MIT License

---

Создано с ❤️ для StarPayUz
