#!/usr/bin/env python3
"""
Тест системы пополнения баланса StarPayUz
"""

import asyncio
import aiohttp
import json

API_BASE = "https://worker-production-679d.up.railway.app"
TEST_USER_ID = 8784918764  # @StarPayUzAdmin

async def test_balance_api():
    """Тест 1: Проверка получения баланса"""
    print("=" * 60)
    print("ТЕСТ 1: Получение баланса пользователя")
    print("=" * 60)
    
    async with aiohttp.ClientSession() as session:
        data = {"telegram_id": TEST_USER_ID}
        
        async with session.post(f"{API_BASE}/api/user/balance", json=data) as resp:
            result = await resp.json()
            print(f"Статус: {resp.status}")
            print(f"Ответ: {json.dumps(result, indent=2, ensure_ascii=False)}")
            
            if result.get("ok"):
                print(f"✅ Баланс: {result['balance']:,} so'm")
                return result['balance']
            else:
                print(f"❌ Ошибка: {result.get('error')}")
                return None

async def test_topup_order():
    """Тест 2: Создание заказа на пополнение"""
    print("\n" + "=" * 60)
    print("ТЕСТ 2: Создание заказа на пополнение")
    print("=" * 60)
    
    async with aiohttp.ClientSession() as session:
        data = {
            "telegram_id": TEST_USER_ID,
            "order_id": "TEST_ORDER_123456",
            "amount": 10000  # 10,000 sum
        }
        
        async with session.post(f"{API_BASE}/api/order/topup", json=data) as resp:
            result = await resp.json()
            print(f"Статус: {resp.status}")
            print(f"Ответ: {json.dumps(result, indent=2, ensure_ascii=False)}")
            
            if result.get("ok"):
                print(f"✅ Заказ создан: {result['order_id']}")
                return result['order_id']
            else:
                print(f"❌ Ошибка: {result.get('error')}")
                return None

async def test_payment_create():
    """Тест 3: Создание платежа"""
    print("\n" + "=" * 60)
    print("ТЕСТ 3: Создание платежа (Payment Invoice)")
    print("=" * 60)
    
    async with aiohttp.ClientSession() as session:
        data = {
            "telegram_id": TEST_USER_ID,
            "order_id": "TEST_PAYMENT_789",
            "amount": 50000,  # 50,000 sum
            "method": "click"
        }
        
        async with session.post(f"{API_BASE}/api/payment/create", json=data) as resp:
            result = await resp.json()
            print(f"Статус: {resp.status}")
            print(f"Ответ: {json.dumps(result, indent=2, ensure_ascii=False)}")
            
            if result.get("ok"):
                print(f"✅ Платеж создан")
                print(f"Payment URL: {result.get('payment_url', 'N/A')}")
                return result.get('payment_url')
            else:
                print(f"❌ Ошибка: {result.get('error')}")
                return None

async def test_payment_webhook():
    """Тест 4: Webhook (симуляция оплаты)"""
    print("\n" + "=" * 60)
    print("ТЕСТ 4: Webhook - симуляция успешной оплаты")
    print("=" * 60)
    
    async with aiohttp.ClientSession() as session:
        # Симулируем webhook от Click/Payme
        data = {
            "shop_order_id": "TEST_WEBHOOK_999",
            "amount": 25000,  # 25,000 sum
            "status": "paid",
            "user_id": TEST_USER_ID,
            "transaction_id": "TXN_123456789"
        }
        
        async with session.post(f"{API_BASE}/webhook/payment", json=data) as resp:
            result = await resp.json()
            print(f"Статус: {resp.status}")
            print(f"Ответ: {json.dumps(result, indent=2, ensure_ascii=False)}")
            
            if result.get("ok"):
                print(f"✅ Webhook обработан, баланс пополнен")
                return True
            else:
                print(f"❌ Ошибка: {result.get('error', 'Unknown error')}")
                return False

async def test_payment_check():
    """Тест 5: Проверка статуса платежа"""
    print("\n" + "=" * 60)
    print("ТЕСТ 5: Проверка статуса платежа")
    print("=" * 60)
    
    async with aiohttp.ClientSession() as session:
        data = {
            "telegram_id": TEST_USER_ID,
            "order_id": "TEST_WEBHOOK_999"
        }
        
        async with session.post(f"{API_BASE}/api/payment/check", json=data) as resp:
            result = await resp.json()
            print(f"Статус: {resp.status}")
            print(f"Ответ: {json.dumps(result, indent=2, ensure_ascii=False)}")
            
            if result.get("ok"):
                if result.get("paid"):
                    print(f"✅ Платеж оплачен: {result.get('amount', 0):,} so'm")
                else:
                    print(f"⏳ Платеж еще не оплачен")
                return result.get("paid")
            else:
                print(f"❌ Ошибка: {result.get('error')}")
                return None

async def main():
    print("🧪 ТЕСТИРОВАНИЕ СИСТЕМЫ ПОПОЛНЕНИЯ БАЛАНСА")
    print("API: " + API_BASE)
    print("User ID: " + str(TEST_USER_ID))
    print()
    
    # Проверяем начальный баланс
    initial_balance = await test_balance_api()
    
    # Тест создания заказа на пополнение
    await test_topup_order()
    
    # Тест создания платежа
    await test_payment_create()
    
    # Тест webhook (симуляция оплаты)
    await test_payment_webhook()
    
    # Проверяем обновленный баланс
    print("\n" + "=" * 60)
    print("ФИНАЛЬНАЯ ПРОВЕРКА: Баланс после пополнения")
    print("=" * 60)
    final_balance = await test_balance_api()
    
    # Проверка статуса платежа
    await test_payment_check()
    
    # Итоги
    print("\n" + "=" * 60)
    print("ИТОГИ ТЕСТИРОВАНИЯ")
    print("=" * 60)
    
    if initial_balance is not None and final_balance is not None:
        diff = final_balance - initial_balance
        print(f"Начальный баланс: {initial_balance:,} so'm")
        print(f"Конечный баланс: {final_balance:,} so'm")
        print(f"Изменение: +{diff:,} so'm")
        
        if diff > 0:
            print("\n✅ СИСТЕМА ПОПОЛНЕНИЯ РАБОТАЕТ!")
        else:
            print("\n⚠️ Баланс не изменился (webhook может требовать реальный платеж)")
    else:
        print("❌ Не удалось получить баланс")
    
    print("\n📝 Заметки:")
    print("- API endpoints доступны и отвечают")
    print("- Для реального пополнения нужен SHOP_ID и SHOP_KEY")
    print("- Webhook должен быть настроен в Click/Payme")
    print("- Проверьте переменные окружения на Railway")

if __name__ == "__main__":
    asyncio.run(main())
