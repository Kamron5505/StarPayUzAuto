import aiohttp
import hashlib
import time
from typing import Optional, Dict, Any
import config


class FragmentAPIClient:
    """Client for fragment-api.uz API"""
    
    def __init__(self):
        self.api_key = config.FRAGMENT_API_KEY
        self.api_url = config.FRAGMENT_API_URL
        self.shop_id = config.SHOP_ID
        self.shop_key = config.SHOP_KEY
    
    async def _make_request(self, endpoint: str, method: str = "GET", data: Optional[Dict] = None) -> Dict[str, Any]:
        """Make API request"""
        url = f"{self.api_url}/{endpoint}"
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        async with aiohttp.ClientSession() as session:
            if method == "GET":
                async with session.get(url, headers=headers, params=data) as response:
                    return await response.json()
            elif method == "POST":
                async with session.post(url, headers=headers, json=data) as response:
                    return await response.json()
    
    async def create_payment(self, amount: float, order_id: str, user_id: int, description: str) -> Optional[Dict]:
        """Create payment link"""
        data = {
            "shop_id": self.shop_id,
            "amount": amount,
            "order_id": order_id,
            "description": description,
            "return_url": f"{config.WEBAPP_URL}/payment/success",
            "callback_url": f"{config.WEBAPP_URL}/payment/callback"
        }
        
        try:
            response = await self._make_request("payment/create", "POST", data)
            return response
        except Exception as e:
            print(f"Error creating payment: {e}")
            return None
    
    async def check_payment(self, order_id: str) -> Optional[Dict]:
        """Check payment status"""
        try:
            response = await self._make_request(f"payment/check", "GET", {"order_id": order_id})
            return response
        except Exception as e:
            print(f"Error checking payment: {e}")
            return None
    
    async def buy_stars(self, user_id: int, amount: int) -> Optional[Dict]:
        """Purchase Telegram stars"""
        data = {
            "user_id": user_id,
            "amount": amount
        }
        
        try:
            response = await self._make_request("stars/buy", "POST", data)
            return response
        except Exception as e:
            print(f"Error buying stars: {e}")
            return None
    
    async def buy_premium(self, user_id: int, duration_months: int) -> Optional[Dict]:
        """Purchase Telegram Premium"""
        data = {
            "user_id": user_id,
            "duration": duration_months
        }
        
        try:
            response = await self._make_request("premium/buy", "POST", data)
            return response
        except Exception as e:
            print(f"Error buying premium: {e}")
            return None
    
    def verify_callback(self, data: Dict) -> bool:
        """Verify payment callback signature"""
        received_signature = data.get("signature", "")
        
        # Create signature string
        sign_string = f"{data.get('order_id')}:{data.get('amount')}:{self.shop_key}"
        expected_signature = hashlib.sha256(sign_string.encode()).hexdigest()
        
        return received_signature == expected_signature


# Global API client instance
api_client = FragmentAPIClient()
