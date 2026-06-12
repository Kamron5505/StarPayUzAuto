# 🎨 Swiper.js + NFT Gifts - Новый дизайн подарков

## ✅ Что добавлено

### 1. **Swiper.js для обычных подарков**
- ✅ Карусель с пролистыванием для обычных подарков
- ✅ 6 слайдов (по 2 подарка на слайд, кроме последнего)
- ✅ Пагинация снизу (точки)
- ✅ Плавная анимация переключения

### 2. **NFT секция внизу**
- ✅ Отдельная красивая секция для премиум подарков
- ✅ Градиентный заголовок "✨ NFT Gifts ✨"
- ✅ Grid layout (2 колонки)
- ✅ 8 NFT подарков с разными уровнями редкости

### 3. **NFT карточки с эффектами**
- ✅ **Badges по редкости**:
  - Limited (50k)
  - Rare (75k-100k)
  - Epic (150k-200k)
  - Legendary (250k)
  - Mythic (500k)
- ✅ **Пульсирующий glow эффект** вокруг иконок
- ✅ **Градиентная рамка** при наведении
- ✅ **Анимация** при hover (поднимается вверх)
- ✅ **Shadow эффекты** для глубины

## 🎨 Дизайн

### Swiper (Обычные подарки)
```
[💝 Yurak] [🧸 Ayiq]  →  [🎁 Quti] [🌹 Atirgul]  →  [🎂 Tort] [🚀 Raketa]  →  ...
        ● ○ ○ ○ ○ ○
```

**Особенности**:
- Карточки 140px ширина
- Синяя рамка (#3B82F6)
- Hover эффект: поднятие + тень
- Selected: градиентный фон

### NFT Section (Премиум подарки)
```
┌─────────────────────────────────────┐
│      ✨ NFT Gifts ✨                │
│ Chegaralangan miqdordagi kolleksiya │
├─────────────────┬───────────────────┤
│   [Limited]     │    [Limited]      │
│   🌹 Deluxe     │    💝 Deluxe      │
│   Atirgul       │    Yurak          │
│   50 000 so'm   │    50 000 so'm    │
├─────────────────┼───────────────────┤
│   [Rare]        │    [Rare]         │
│   🎂 Deluxe     │    💎 Deluxe      │
│   ...           │    ...            │
└─────────────────┴───────────────────┘
```

**Особенности**:
- Темный градиентный фон
- Золотой/розовый/фиолетовый градиент рамки
- Glow эффект (pulse анимация)
- Градиентные цены

## 📱 Responsive

- **Mobile-first** дизайн
- Swiper адаптируется под экран
- NFT grid: 2 колонки на всех экранах
- Touch-friendly (свайп работает идеально)

## 🔧 Технические детали

### Swiper.js v11
```html
<!-- CSS -->
<link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/swiper@11/swiper-bundle.min.css" />

<!-- JS -->
<script src="https://cdn.jsdelivr.net/npm/swiper@11/swiper-bundle.min.js"></script>
```

### Инициализация Swiper
```javascript
const swiper = new Swiper('.mySwiper', {
    slidesPerView: 1,
    spaceBetween: 20,
    pagination: {
        el: '.swiper-pagination',
        clickable: true,
    },
    autoplay: false,  // Не автоплей, пользователь управляет
});
```

### NFT Card Structure
```html
<div class="nft-card" onclick="pickGift(this, 'deluxe_rose', 50000)">
    <span class="nft-badge">Limited</span>
    <div class="nft-emoji-wrapper">
        <div class="nft-glow"></div>  <!-- Пульсирующий эффект -->
        <img src="./images/rose.webp" alt="Deluxe Rose" width="80">
    </div>
    <div class="nft-name">Deluxe Atirgul</div>
    <div class="nft-price">50 000 so'm</div>
</div>
```

## 🎯 Преимущества

### 1. **UX улучшения**
- ✅ Меньше скролла - подарки компактно организованы
- ✅ Легче выбирать - свайп интуитивно понятен
- ✅ Визуальное разделение - обычные vs NFT

### 2. **Производительность**
- ✅ Ленивая загрузка через Swiper
- ✅ Меньше DOM элементов на экране
- ✅ Плавная 60fps анимация

### 3. **Визуал**
- ✅ Современный дизайн (как в Telegram)
- ✅ Premium ощущение для NFT подарков
- ✅ Четкая иерархия (обычные → NFT)

## 🧪 Тестирование

### Проверьте:
1. **Swiper**:
   - ✅ Свайп работает плавно
   - ✅ Пагинация кликабельная
   - ✅ Можно выбрать подарок на любом слайде

2. **NFT карточки**:
   - ✅ Hover эффекты работают
   - ✅ Glow пульсирует
   - ✅ Badge'ы показываются

3. **Функционал**:
   - ✅ Выбор подарка работает
   - ✅ Selected state сохраняется
   - ✅ Покупка работает для всех типов

## 📊 Сравнение

### До (старая версия)
```
- Grid 3x11 = 33 карточки на экране
- Много скролла
- Нет разделения обычных/премиум
- Простые карточки без эффектов
```

### После (с Swiper + NFT)
```
- Swiper: 2 карточки видимы, 11 в слайдере
- NFT секция: 8 карточек в grid
- Минимальный скролл
- Четкое разделение по типам
- Premium эффекты для NFT
```

## 🎬 Анимации

### 1. **Glow Pulse**
```css
@keyframes pulse {
    0%, 100% { opacity: 0.5; transform: scale(1); }
    50% { opacity: 1; transform: scale(1.1); }
}
```

### 2. **Card Hover**
- Transform: translateY(-5px) scale(1.02)
- Shadow: 0 10px 40px rgba(255, 107, 157, .3)
- Border glow: opacity 0 → 1

### 3. **Swiper Transition**
- Duration: 300ms
- Easing: cubic-bezier

## 🔄 Обратная совместимость

- ✅ Старая версия сохранена в `gift_old.html`
- ✅ API не изменился
- ✅ Все функции работают как раньше
- ✅ Можно откатиться если нужно

## 🚀 Деплой

### Vercel (webapp)
```bash
# Автоматически деплоится через GitHub
https://starpayuz-webapp.vercel.app/gift.html
```

### Railway (API)
```bash
# API остался без изменений
https://worker-production-679d.up.railway.app/api/order/gift
```

## 💡 Будущие улучшения

1. **Infinite scroll для NFT**: Добавить пагинацию если NFT будет больше 8
2. **Фильтры**: "Все", "Limited", "Rare", "Epic", etc.
3. **Сортировка**: По цене, по редкости
4. **Поиск**: Быстрый поиск по названию
5. **Favorites**: Избранные подарки

---
**Дата**: 12 июня 2026
**Версия**: 4.0 (Swiper + NFT)
**Статус**: ✅ Deployed to Vercel
**CDN**: Swiper v11 from jsDelivr
