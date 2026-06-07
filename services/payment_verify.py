"""Verify payment webhooks using shop_key."""

import hashlib
import hmac
import json
from typing import Any


def verify_shop_signature(payload: dict[str, Any], shop_key: str) -> bool:
    """
    Common pattern: sign = HMAC-SHA256(sorted fields, shop_key).
    Adjust field names per Fragment API Uz payment docs.
    """
    sign = payload.get("sign") or payload.get("signature") or payload.get("hash")
    if not sign or not shop_key:
        return False

    data = {k: v for k, v in payload.items() if k not in ("sign", "signature", "hash")}
    check_string = "&".join(f"{k}={data[k]}" for k in sorted(data.keys()))
    expected = hmac.new(
        shop_key.encode(), check_string.encode(), hashlib.sha256
    ).hexdigest()
    return hmac.compare_digest(expected.lower(), str(sign).lower())


def extract_payment_fields(payload: dict[str, Any]) -> tuple[str | None, int | None, int | None]:
    order_id = (
        payload.get("order_id")
        or payload.get("shop_order_id")
        or payload.get("merchant_order_id")
        or payload.get("id")
    )
    amount = payload.get("amount") or payload.get("sum") or payload.get("total")
    user_id = payload.get("user_id") or payload.get("telegram_id") or payload.get("customer_id")
    try:
        amount_int = int(amount) if amount is not None else None
    except (TypeError, ValueError):
        amount_int = None
    try:
        user_int = int(user_id) if user_id is not None else None
    except (TypeError, ValueError):
        user_int = None
    return str(order_id) if order_id else None, amount_int, user_int
