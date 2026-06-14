"""Dashboard router - statistics and charts"""
import hashlib
import json
import logging
from datetime import datetime, timedelta, timezone

from fastapi import APIRouter, Depends
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from admin.database import get_db
from admin.routers.auth import require_admin
from admin.schemas.auth import AdminUserInfo
from admin.schemas.dashboard import ChartDataPoint, DashboardResponse, DashboardStats
from admin.services.cache import cache_get, cache_set

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/admin/dashboard", tags=["dashboard"])

CACHE_TTL = 120  # 2 minutes cache for dashboard stats


@router.get("/stats", response_model=DashboardResponse)
async def get_dashboard_stats(
    admin: AdminUserInfo = Depends(require_admin),
    db: AsyncSession = Depends(get_db),
):
    """Get dashboard statistics (cached for 2 minutes)"""
    # Try cache first
    cache_key = "dashboard:stats"
    cached = await cache_get(cache_key)
    if cached:
        return DashboardResponse(**cached)

    now = datetime.now(timezone.utc)
    today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
    week_start = today_start - timedelta(days=7)
    month_start = today_start - timedelta(days=30)

    # Total users
    result = await db.execute(text("SELECT COUNT(*) FROM users"))
    total_users = result.scalar() or 0

    # Active users (users who have made orders)
    result = await db.execute(
        text("SELECT COUNT(DISTINCT telegram_id) FROM orders")
    )
    active_users = result.scalar() or 0

    # New users today
    result = await db.execute(
        text("SELECT COUNT(*) FROM users WHERE created_at >= :since"),
        {"since": today_start},
    )
    new_users_today = result.scalar() or 0

    # New users this week
    result = await db.execute(
        text("SELECT COUNT(*) FROM users WHERE created_at >= :since"),
        {"since": week_start},
    )
    new_users_week = result.scalar() or 0

    # New users this month
    result = await db.execute(
        text("SELECT COUNT(*) FROM users WHERE created_at >= :since"),
        {"since": month_start},
    )
    new_users_month = result.scalar() or 0

    # Total balance
    result = await db.execute(text("SELECT COALESCE(SUM(balance), 0) FROM users"))
    total_balance = result.scalar() or 0

    # Total orders count
    result = await db.execute(text("SELECT COUNT(*) FROM orders"))
    total_orders = result.scalar() or 0

    # Total transactions count
    result = await db.execute(text("SELECT COUNT(*) FROM transactions"))
    total_transactions = result.scalar() or 0

    # Total revenue (sum of completed payments)
    result = await db.execute(
        text("SELECT COALESCE(SUM(amount), 0) FROM payments WHERE status = 'paid'")
    )
    total_revenue = result.scalar() or 0

    # User growth chart (last 30 days) - use daily aggregation for efficiency
    user_growth = []
    for i in range(29, -1, -1):
        day = today_start - timedelta(days=i)
        day_end = day + timedelta(days=1)
        result = await db.execute(
            text("SELECT COUNT(*) FROM users WHERE created_at >= :start AND created_at < :end"),
            {"start": day, "end": day_end},
        )
        count = result.scalar() or 0
        user_growth.append(
            ChartDataPoint(date=day.strftime("%Y-%m-%d"), value=count)
        )

    # Transaction volume chart (last 30 days)
    transaction_volume = []
    for i in range(29, -1, -1):
        day = today_start - timedelta(days=i)
        day_end = day + timedelta(days=1)
        result = await db.execute(
            text(
                "SELECT COALESCE(SUM(amount), 0) FROM payments "
                "WHERE created_at >= :start AND created_at < :end AND status = 'paid'"
            ),
            {"start": day, "end": day_end},
        )
        value = result.scalar() or 0
        transaction_volume.append(
            ChartDataPoint(date=day.strftime("%Y-%m-%d"), value=value)
        )

    revenue_data = transaction_volume

    stats = DashboardStats(
        total_users=total_users,
        active_users=active_users,
        new_users_today=new_users_today,
        new_users_week=new_users_week,
        new_users_month=new_users_month,
        total_balance=total_balance,
        total_transactions=total_transactions,
        total_orders=total_orders,
        total_revenue=total_revenue,
    )

    response = DashboardResponse(
        stats=stats,
        user_growth=user_growth,
        transaction_volume=transaction_volume,
        revenue_data=revenue_data,
    )

    # Cache the result
    await cache_set(cache_key, response.model_dump(), ttl=CACHE_TTL)

    return response
