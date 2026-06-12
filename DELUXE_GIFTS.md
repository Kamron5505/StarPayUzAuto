# 🌟 Удалённые/Премиум Подарки (Deluxe Gifts)

## ✅ Что добавлено

Теперь в системе есть **4 уровня подарков**:

### 1. **Regular Gifts** (Обычные) - 3,000 - 20,000 сум
- 💝 Yurak, 🧸 Ayiq — **3,000 сум**
- 🎁 Quti, 🌹 Atirgul — **5,000 сум**
- 🎂 Tort, 🚀 Raketa, 🍾 Shampan, 💐 Guldasta — **10,000 сум**
- 💎 Olmos, 🏆 Kubok, 💍 Uzuk — **20,000 сум**

### 2. **Deluxe Gifts** (Удалённые) - 50,000 - 100,000 сум
Золотая рамка и эффект мерцания ✨
- 🌹✨ Deluxe Atirgul — **50,000 сум** (25 Stars)
- 💝✨ Deluxe Yurak — **50,000 сум** (25 Stars)
- 🎂✨ Deluxe Tort — **75,000 сум** (50 Stars)
- 💎✨ Deluxe Olmos — **100,000 сум** (100 Stars)

### 3. **Premium Gifts** (Премиум) - 150,000 - 200,000 сум
Фиолетовая рамка и специальные эффекты
- 🏆✨ Oltin Kubok — **150,000 сум** (250 Stars)
- 👑✨ Yulduz Toj — **200,000 сум** (500 Stars)

### 4. **Exclusive Gifts** (Эксклюзив) - 250,000 - 500,000 сум
Розовая рамка и уникальные анимации
- 💠 Ko'k Javohir — **250,000 сум** (1,000 Stars)
- 🔥🦅 Olovli Qanot — **500,000 сум** (2,500 Stars)

## 🎨 Визуальные изменения

### В webapp (gift.html):
1. **Разделение на секции**:
   - "Gift tanlang" - обычные подарки
   - "⭐ Deluxe Gifts" - премиум раздел

2. **Цветовые акценты**:
   - Обычные: синяя рамка (#3B82F6)
   - Deluxe: золотая рамка (#FFD700)
   - Premium: фиолетовая рамка (#9F7AEA)
   - Exclusive: розовая рамка (#FF6B9D)

3. **Анимации**:
   - Эффект мерцания (shimmer) для премиум подарков
   - Drop-shadow эффекты для делюкс подарков
   - Анимация при наведении

## 🔧 Технические изменения

### 1. `config.py`
```python
# Добавлены новые поля:
"tier": "regular" | "deluxe" | "premium" | "exclusive"
"stars": количество Stars (для отображения эквивалента)
"limited": True/False (ограниченный тираж)
```

### 2. `api/server.py`
```python
# Обновлен gift_mapping с ID новых подарков:
"deluxe_rose": "5170145012310081616",
"deluxe_heart": "5170145012310081617",
# ... и т.д.
```

⚠️ **ВАЖНО**: ID для делюкс подарков временные (placeholder). Нужно получить реальные ID через `payments.getStarGifts`.

### 3. `services/telethon_client.py`
```python
# Обновлен метод get_available_gifts():
# Теперь использует GetStarGiftsRequest вместо GetStickerSetRequest
# Возвращает полную информацию о подарках включая:
- id (gift ID)
- stars (стоимость в Stars)
- availability_remains (остаток лимитированных)
- availability_total (общее количество)
- limited (ограниченный или нет)
```

## 📋 Как получить реальные Gift IDs

### Метод 1: Через Telethon
```python
from services.telethon_client import gift_sender

# Получить список всех доступных подарков
gifts = await gift_sender.get_available_gifts()

# gifts['gifts'] содержит:
[
  {
    "id": "5170145012310081615",
    "stars": 1,
    "limited": False,
    "availability_remains": None
  },
  {
    "id": "5170145012310081616",
    "stars": 25,
    "limited": True,
    "availability_remains": 500000
  },
  ...
]
```

### Метод 2: Создать API endpoint
Добавить в `api/server.py`:
```python
async def api_get_available_gifts(request: web.Request) -> web.Response:
    """Get list of available Star Gifts"""
    from services.telethon_client import gift_sender
    
    if not gift_sender:
        return web.json_response({"ok": False, "error": "Gift sender not initialized"})
    
    result = await gift_sender.get_available_gifts()
    return web.json_response(result)

# В create_app():
app.router.add_get("/api/gifts/available", api_get_available_gifts)
```

Затем вызвать:
```bash
curl https://worker-production-679d.up.railway.app/api/gifts/available
```

## 🧪 Тестирование

### 1. Откройте webapp
https://starpayuz-webapp.vercel.app/gift.html

### 2. Проверьте интерфейс
- ✅ Обычные подарки отображаются первыми
- ✅ Секция "⭐ Deluxe Gifts" видна ниже
- ✅ Разные цвета рамок для разных уровней
- ✅ Эффект мерцания на делюкс подарках

### 3. Попробуйте купить делюкс подарок
1. Выберите любой делюкс подарок (например, Deluxe Atirgul - 50,000 сум)
2. Введите username
3. Нажмите "Sotib olish"

### Ожидаемое поведение:
- ✅ Если баланс достаточный → подарок отправляется
- ⚠️ Если Gift ID неправильный → ошибка "STARGIFT_USAGE_LIMITED" или "GIFT_NOT_FOUND"

## ⚠️ Известные ограничения

### 1. Placeholder IDs
Текущие ID для делюкс подарков - это placeholder'ы. Нужно:
1. Получить реальные ID через `GetStarGiftsRequest`
2. Обновить `gift_mapping` в `api/server.py`

### 2. Наличие Stars
Для отправки делюкс подарков нужно больше Stars на аккаунте:
- Regular: 1-5 Stars
- Deluxe: 25-100 Stars
- Premium: 250-500 Stars
- Exclusive: 1000-2500 Stars

### 3. Ограниченные подарки
Некоторые подарки могут быть распроданы:
- `availability_remains` покажет остаток
- Если `availability_remains = 0` → подарок недоступен

## 📊 Следующие шаги

1. **Получить реальные Gift IDs**:
   ```bash
   # Вызвать через Railway logs или создать endpoint
   curl https://worker-production-679d.up.railway.app/api/gifts/available
   ```

2. **Обновить gift_mapping**:
   - Заменить placeholder ID на реальные
   - Сопоставить каждый подарок с его Telegram ID

3. **Добавить проверку наличия**:
   - Перед отправкой проверять `availability_remains`
   - Показывать "Tugagan" если подарок закончился

4. **Пополнить Stars на аккаунте**:
   - Убедиться, что на +998971051000 достаточно Stars
   - Для тестирования делюкс подарков нужно минимум 25 Stars

## 🎁 Преимущества системы

- ✅ **4 уровня подарков** - от бюджетных до эксклюзивных
- ✅ **Визуальное разделение** - пользователи сразу видят премиум варианты
- ✅ **Гибкие цены** - от 3,000 до 500,000 сум
- ✅ **Scalable** - легко добавить новые подарки
- ✅ **Анимации** - красивые эффекты для премиум уровней

---
**Дата**: 12 июня 2026
**Статус**: ✅ Deployed to Railway & Vercel
**Версия**: 3.0 (с делюкс подарками)
