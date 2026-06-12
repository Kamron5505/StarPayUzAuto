# 🎁 Получение реальных Gift IDs из Telegram

## Проблема
Текущие ID для делюкс подарков - это placeholder'ы. Нужно получить **реальные ID** от Telegram API.

## ✅ Решение: API Endpoint

Я добавил endpoint который получает список всех доступных подарков из Telegram:

```
GET https://worker-production-679d.up.railway.app/api/gifts/available
```

## 🔧 Как использовать

### Метод 1: Через браузер
1. Откройте в браузере:
   ```
   https://worker-production-679d.up.railway.app/api/gifts/available
   ```

2. Вы получите JSON с полным списком подарков:
   ```json
   {
     "ok": true,
     "gifts": [
       {
         "id": "5170145012310081615",
         "stars": 1,
         "availability_remains": null,
         "availability_total": null,
         "limited": false,
         "sticker_id": "..."
       },
       {
         "id": "5170145012310081616",
         "stars": 25,
         "availability_remains": 500000,
         "availability_total": 1000000,
         "limited": true
       },
       ...
     ],
     "count": 50
   }
   ```

### Метод 2: Через curl
```bash
curl https://worker-production-679d.up.railway.app/api/gifts/available
```

### Метод 3: Через Python
```python
import requests

response = requests.get('https://worker-production-679d.up.railway.app/api/gifts/available')
data = response.json()

if data['ok']:
    for gift in data['gifts']:
        print(f"Gift ID: {gift['id']}, Stars: {gift['stars']}, Limited: {gift['limited']}")
```

## 📊 Структура ответа

```json
{
  "ok": true,
  "gifts": [
    {
      "id": "5170145012310081615",          // ← Gift ID (нужен для отправки)
      "stars": 1,                           // ← Стоимость в Stars
      "availability_remains": null,         // ← Остаток (null = неограничен)
      "availability_total": null,           // ← Всего выпущено
      "limited": false,                     // ← Ограниченный тираж?
      "sticker_id": "5170145012310081615"   // ← ID стикера
    }
  ],
  "count": 50
}
```

## 🎯 Следующие шаги

### 1. Получите список подарков
Вызовите endpoint и сохраните результат:
```bash
curl https://worker-production-679d.up.railway.app/api/gifts/available > gifts.json
```

### 2. Определите какой подарок какому ID соответствует
Сортируйте по `stars`:
- `stars: 1` → обычные подарки (Heart, Bear, etc.)
- `stars: 25` → Deluxe Rose, Deluxe Heart
- `stars: 50` → Deluxe Cake
- `stars: 100` → Deluxe Diamond
- `stars: 250` → Golden Trophy
- `stars: 500` → Star Crown
- `stars: 1000` → Blue Gem
- `stars: 2500` → Fire Phoenix

### 3. Обновите `api/server.py`
Замените placeholder IDs на реальные в `gift_mapping`:

```python
gift_mapping = {
    # Regular gifts (уже правильные)
    "heart": "5170145012310081615",
    "bear": "5170233102089322756",
    # ...
    
    # Deluxe gifts (заменить на реальные!)
    "deluxe_rose": "REAL_ID_HERE",      # 25 stars
    "deluxe_heart": "REAL_ID_HERE",     # 25 stars
    "deluxe_cake": "REAL_ID_HERE",      # 50 stars
    "deluxe_diamond": "REAL_ID_HERE",   # 100 stars
    "golden_trophy": "REAL_ID_HERE",    # 250 stars
    "star_crown": "REAL_ID_HERE",       # 500 stars
    "blue_gem": "REAL_ID_HERE",         # 1000 stars
    "fire_phoenix": "REAL_ID_HERE",     # 2500 stars
}
```

### 4. Закоммитьте изменения
```bash
git add api/server.py
git commit -m "Update deluxe gift IDs with real Telegram gift IDs"
git push origin main
```

## ⚠️ Возможные проблемы

### Ошибка: "Gift sender не инициализирован"
**Причина**: Telethon не запущен на Railway

**Решение**: Проверьте Railway logs:
```
INFO - Telethon gift sender initialized
INFO - Telethon client started successfully
```

Если не видите этих логов, проверьте переменные окружения:
- `API_ID=30654977`
- `API_HASH=921be05f47930bd6e60860faa4c6b0d5`
- `TELETHON_SESSION_STRING=...`

### Ошибка: "Client not connected"
**Причина**: Telethon клиент отключился

**Решение**: Перезапустите Railway deployment

### Пустой список подарков
**Причина**: 
1. `GetStarGiftsRequest` не существует в вашей версии Telethon
2. API изменился

**Решение**: Обновите Telethon:
```bash
pip install --upgrade telethon
```

## 🧪 Тестирование

После обновления IDs, протестируйте отправку делюкс подарка:

1. Откройте https://starpayuz-webapp.vercel.app/gift.html
2. Выберите Deluxe Atirgul (50,000 сум)
3. Введите username: `StarPayUzAdmin`
4. Нажмите "Sotib olish"

**Ожидаемый результат**:
- ✅ Подарок отправлен успешно
- ✅ Получатель получил настоящий Deluxe подарок (не обычный)
- ✅ В Railway logs: `Star gift sent to @StarPayUzAdmin: <REAL_ID>`

## 💡 Дополнительные возможности

### Автоматическое обновление gift_mapping
Можно сделать, чтобы система автоматически подгружала актуальные IDs:

```python
# В api/server.py
async def get_dynamic_gift_mapping():
    """Dynamically fetch gift IDs from Telegram"""
    from services.telethon_client import gift_sender
    
    if not gift_sender:
        return None
    
    result = await gift_sender.get_available_gifts()
    if not result.get('ok'):
        return None
    
    # Создаем маппинг по количеству Stars
    mapping = {}
    for gift in result['gifts']:
        stars = gift.get('stars', 0)
        if stars == 1:
            mapping['heart'] = gift['id']  # Первый с 1 star
        elif stars == 25:
            if 'deluxe_rose' not in mapping:
                mapping['deluxe_rose'] = gift['id']
            else:
                mapping['deluxe_heart'] = gift['id']
        # ... и т.д.
    
    return mapping
```

### Кеширование
Чтобы не вызывать Telegram API каждый раз:

```python
# Кешировать на 1 час
from functools import lru_cache
import time

_gift_cache = None
_cache_time = 0

async def get_cached_gifts():
    global _gift_cache, _cache_time
    now = time.time()
    
    # Если кеш старше 1 часа, обновить
    if _gift_cache is None or now - _cache_time > 3600:
        _gift_cache = await gift_sender.get_available_gifts()
        _cache_time = now
    
    return _gift_cache
```

---
**Дата**: 12 июня 2026
**Endpoint**: `GET /api/gifts/available`
**Статус**: ✅ Deployed and ready
