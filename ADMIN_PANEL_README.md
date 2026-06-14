# StarPayUz Admin Panel

Профессиональная панель управления для Telegram-бота @starpayuzauto_bot.

## 🚀 Технологии

- **Backend:** FastAPI + SQLAlchemy (async) + Alembic
- **Frontend:** Vanilla JS SPA + Chart.js + Telegram WebApp стиль
- **Auth:** JWT + Telegram WebApp initData
- **Cache:** Redis (опционально)
- **Database:** PostgreSQL (через asyncpg)
- **Realtime:** WebSocket
- **Deploy:** Docker Compose

## 📋 Функции

### 1. Dashboard
- Общая статистика: пользователи, баланс, доходы
- Графики роста пользователей (30 дней)
- Графики объёма транзакций (30 дней)
- WebSocket для обновлений в реальном времени

### 2. Пользователи
- Просмотр всех пользователей (пагинация)
- Поиск по Telegram ID, Username, SP ID
- Просмотр профиля
- Блокировка / Разблокировка
- Удаление

### 3. Баланс
- Начисление баланса
- Списание баланса
- Установка баланса вручную
- Обнуление баланса
- История операций с причиной

### 4. Рассылка
- Создание рассылок (текст, фото, видео, документы)
- Поддержка Inline-кнопок
- Фильтры получателей (язык, баланс, дата)
- Фоновая отправка с прогрессом
- Отчёт об отправке

### 5. Настройки
- Динамические настройки в БД
- Категории: цены, комиссии, лимиты, общие
- Инициализация настроек по умолчанию
- Мгновенное применение

### 6. Логи
- Журнал действий администраторов
- Фильтрация по типу действия
- IP адрес, время, детали
- Все изменения отслеживаются

## 🏗 Структура

```
admin/
├── main.py              # FastAPI entry point
├── config.py            # Admin panel config
├── database.py          # SQLAlchemy async setup
├── models/              # SQLAlchemy models
│   ├── admin_user.py    # Admin users
│   ├── log.py           # Activity logs
│   ├── setting.py       # App settings
│   ├── broadcast.py     # Broadcasts
│   └── transaction.py   # Balance transactions
├── schemas/             # Pydantic schemas
├── services/            # Business logic
│   ├── auth_service.py  # JWT + password auth
│   ├── log_service.py   # Activity logging
│   ├── bot_notifier.py  # Telegram bot API
│   └── cache.py         # Redis caching
├── routers/             # FastAPI routes
│   ├── auth.py          # Authentication
│   ├── dashboard.py     # Statistics
│   ├── users.py         # User management
│   ├── balance.py       # Balance operations
│   ├── broadcasts.py    # Mass messaging
│   ├── settings.py      # System settings
│   ├── logs.py          # Activity logs
│   └── ws.py            # WebSocket
└── static/              # Frontend SPA
    ├── index.html       # Main page
    ├── css/style.css    # Dark Telegram theme
    └── js/
        ├── app.js       # Core application
        ├── dashboard.js # Dashboard page
        ├── users.js     # Users page
        ├── balance.js   # Balance page
        ├── broadcasts.js# Broadcasts page
        ├── settings.js  # Settings page
        └── logs.js      # Logs page

alembic/                 # Database migrations
docker-compose.yml       # Docker Compose
Dockerfile               # Admin panel image
```

## 🔧 Установка и запуск

### Через Docker Compose (рекомендуется)

```bash
# Клонируйте репозиторий
git clone https://github.com/your-username/starpayuz.git
cd starpayuz

# Настройте .env файл
cp .env.example .env
# Отредактируйте .env: BOT_TOKEN, DATABASE_URL, JWT_SECRET_KEY, etc.

# Запустите все сервисы
docker-compose up -d

# Admin panel: http://localhost:8000
# Bot API: http://localhost:8080
```

### Локальный запуск (для разработки)

```bash
# Установка зависимостей
pip install -r requirements.txt

# Настройка .env
cp .env.example .env

# Запуск PostgreSQL и Redis (через Docker)
docker run -d --name starpayuz-db -e POSTGRES_DB=starpayuz -e POSTGRES_PASSWORD=postgres -p 5432:5432 postgres:16-alpine
docker run -d --name starpayuz-redis -p 6379:6379 redis:7-alpine

# Запуск Admin Panel
python run_admin.py

# Или через uvicorn напрямую
uvicorn admin.main:app --host 0.0.0.0 --port 8000 --reload
```

### Миграции БД

```bash
# Автоматическое создание таблиц (при первом запуске)
# Таблицы создаются автоматически через метаданные SQLAlchemy

# Ручное применение миграций Alembic
alembic upgrade head

# Создание новой миграции
alembic revision --autogenerate -m "description"
```

## 🔐 Аутентификация

Первый вход:
1. Запустите админ-панель
2. Войдите с логином `admin` и паролем `admin123`
3. **Обязательно смените пароль!**

Через Telegram (рекомендуется):
1. Укажите `ADMIN_IDS` в .env (Telegram ID администраторов)
2. Введите команду `/admin` в боте
3. Нажмите кнопку "Admin Panelni ochish"

> **Важно:** В production обязательно смените `JWT_SECRET_KEY` и `DEFAULT_ADMIN_PASSWORD` в `.env`!

## 🌐 Переменные окружения

| Переменная | Описание | По умолчанию |
|------------|----------|-------------|
| `DATABASE_URL` | PostgreSQL connection string | `postgresql://postgres:postgres@localhost:5432/starpayuz` |
| `REDIS_URL` | Redis connection string | `redis://localhost:6379/0` |
| `JWT_SECRET_KEY` | Secret key for JWT tokens | `change-me-in-production` |
| `JWT_EXPIRATION_HOURS` | Token validity period | `24` |
| `ADMIN_PANEL_URL` | Public URL of admin panel | `http://localhost:8000` |
| `ADMIN_HOST` | Bind address | `0.0.0.0` |
| `ADMIN_PORT` | Bind port | `8000` |
| `DEFAULT_ADMIN_USERNAME` | Default admin login | `admin` |
| `DEFAULT_ADMIN_PASSWORD` | Default admin password | `admin123` |
| `ADMIN_IDS` | Telegram IDs of admins (comma-separated) | — |
| `BOT_TOKEN` | Telegram bot token (for bot API calls) | — |
| `LOG_LEVEL` | Logging level | `info` |

## 📡 API Endpoints

### Auth
- `POST /api/admin/auth/login` — Login with username/password
- `POST /api/admin/auth/telegram` — Login via Telegram WebApp
- `GET /api/admin/auth/me` — Get current admin info

### Dashboard
- `GET /api/admin/dashboard/stats` — Dashboard statistics + charts

### Users
- `GET /api/admin/users` — List users (paginated)
- `GET /api/admin/users/search` — Search users
- `GET /api/admin/users/{id}` — Get user details
- `POST /api/admin/users/{id}/block` — Block user
- `POST /api/admin/users/{id}/unblock` — Unblock user
- `DELETE /api/admin/users/{id}` — Delete user

### Balance
- `POST /api/admin/balance/add` — Add balance
- `POST /api/admin/balance/deduct` — Deduct balance
- `POST /api/admin/balance/set` — Set exact balance
- `POST /api/admin/balance/reset` — Reset balance to 0
- `GET /api/admin/balance/history` — Transaction history

### Broadcasts
- `POST /api/admin/broadcasts` — Create broadcast
- `GET /api/admin/broadcasts` — List broadcasts
- `GET /api/admin/broadcasts/{id}` — Get broadcast details
- `POST /api/admin/broadcasts/{id}/send` — Start sending

### Settings
- `GET /api/admin/settings` — Get all settings
- `PUT /api/admin/settings/{key}` — Update setting
- `POST /api/admin/settings/init` — Init default settings

### Logs
- `GET /api/admin/logs` — Get activity logs

### WebSocket
- `WS /api/admin/ws` — Real-time admin updates

## 🔒 Безопасность

- ✅ JWT аутентификация с adjustable TTL
- ✅ SHA-256 хеширование паролей
- ✅ SQL-injection защита (параметризованные запросы)
- ✅ Telegram WebApp initData валидация
- ✅ IP адреса логируются
- ✅ CORS настройка
- ✅ Все действия админов логируются

## 🐳 Docker

```bash
# Сборка и запуск
docker-compose up -d

# Просмотр логов
docker-compose logs -f admin

# Остановка
docker-compose down

# Пересборка
docker-compose build --no-cache admin
```
