"""Broadcast management router"""
import asyncio
import json
import logging
from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import func, select, text
from sqlalchemy.ext.asyncio import AsyncSession

from admin.database import get_db
from admin.models.broadcast import Broadcast
from admin.routers.auth import require_admin
from admin.schemas.auth import AdminUserInfo
from admin.schemas.broadcast import (
    BroadcastCreate,
    BroadcastInfo,
    BroadcastListResponse,
    BroadcastStatusResponse,
)
from admin.services.bot_notifier import send_broadcast_message
from admin.services.log_service import log_admin_action

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/admin/broadcasts", tags=["broadcasts"])


@router.post("", response_model=BroadcastInfo)
async def create_broadcast(
    request: BroadcastCreate,
    admin: AdminUserInfo = Depends(require_admin),
    db: AsyncSession = Depends(get_db),
):
    """Create a new broadcast"""
    broadcast = Broadcast(
        admin_id=admin.id,
        message_type=request.message_type,
        content=request.content,
        file_id=request.file_id,
        file_url=request.file_url,
        buttons=request.buttons,
        filters=request.filters,
        status="draft",
    )
    db.add(broadcast)
    await db.commit()
    await db.refresh(broadcast)

    await log_admin_action(
        db,
        admin.id,
        admin.username,
        "broadcast_create",
        entity_type="broadcast",
        entity_id=str(broadcast.id),
        details=f"Created broadcast #{broadcast.id} type={request.message_type}",
    )

    return BroadcastInfo(
        id=broadcast.id,
        admin_id=broadcast.admin_id,
        message_type=broadcast.message_type,
        content=broadcast.content,
        file_id=broadcast.file_id,
        file_url=broadcast.file_url,
        buttons=broadcast.buttons,
        filters=broadcast.filters,
        status=broadcast.status,
        sent_count=broadcast.sent_count,
        total_count=broadcast.total_count,
        error_count=broadcast.error_count,
        created_at=broadcast.created_at,
    )


@router.get("", response_model=BroadcastListResponse)
async def get_broadcasts(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    admin: AdminUserInfo = Depends(require_admin),
    db: AsyncSession = Depends(get_db),
):
    """Get list of broadcasts"""
    total_result = await db.execute(select(func.count(Broadcast.id)))
    total = total_result.scalar() or 0

    result = await db.execute(
        select(Broadcast)
        .order_by(Broadcast.created_at.desc())
        .offset((page - 1) * page_size)
        .limit(page_size)
    )
    broadcasts_data = result.scalars().all()

    broadcasts = [
        BroadcastInfo(
            id=b.id,
            admin_id=b.admin_id,
            message_type=b.message_type,
            content=b.content,
            file_id=b.file_id,
            file_url=b.file_url,
            buttons=b.buttons,
            filters=b.filters,
            status=b.status,
            sent_count=b.sent_count,
            total_count=b.total_count,
            error_count=b.error_count,
            created_at=b.created_at,
            completed_at=b.completed_at,
        )
        for b in broadcasts_data
    ]

    return BroadcastListResponse(total=total, page=page, page_size=page_size, broadcasts=broadcasts)


@router.get("/{broadcast_id}", response_model=BroadcastInfo)
async def get_broadcast(
    broadcast_id: int,
    admin: AdminUserInfo = Depends(require_admin),
    db: AsyncSession = Depends(get_db),
):
    """Get broadcast details"""
    result = await db.execute(
        select(Broadcast).where(Broadcast.id == broadcast_id)
    )
    broadcast = result.scalar_one_or_none()
    if not broadcast:
        raise HTTPException(status_code=404, detail="Broadcast not found")

    return BroadcastInfo(
        id=broadcast.id,
        admin_id=broadcast.admin_id,
        message_type=broadcast.message_type,
        content=broadcast.content,
        file_id=broadcast.file_id,
        file_url=broadcast.file_url,
        buttons=broadcast.buttons,
        filters=broadcast.filters,
        status=broadcast.status,
        sent_count=broadcast.sent_count,
        total_count=broadcast.total_count,
        error_count=broadcast.error_count,
        created_at=broadcast.created_at,
        completed_at=broadcast.completed_at,
    )


@router.post("/{broadcast_id}/send", response_model=BroadcastStatusResponse)
async def send_broadcast(
    broadcast_id: int,
    admin: AdminUserInfo = Depends(require_admin),
    db: AsyncSession = Depends(get_db),
):
    """Send a broadcast to users (optionally filtered)"""
    result = await db.execute(
        select(Broadcast).where(Broadcast.id == broadcast_id)
    )
    broadcast = result.scalar_one_or_none()
    if not broadcast:
        raise HTTPException(status_code=404, detail="Broadcast not found")

    if broadcast.status == "sending":
        raise HTTPException(status_code=400, detail="Broadcast already sending")

    # Parse filters
    filters_dict = {}
    if broadcast.filters:
        try:
            filters_dict = json.loads(broadcast.filters)
        except json.JSONDecodeError:
            filters_dict = {}

    # Build WHERE clause based on filters
    where_clauses = []
    params = {}

    if "language" in filters_dict and filters_dict["language"]:
        where_clauses.append("language = :lang")
        params["lang"] = filters_dict["language"]

    if "min_balance" in filters_dict:
        where_clauses.append("balance >= :min_bal")
        params["min_bal"] = int(filters_dict["min_balance"])

    if "max_balance" in filters_dict:
        where_clauses.append("balance <= :max_bal")
        params["max_bal"] = int(filters_dict["max_balance"])

    if "created_after" in filters_dict:
        where_clauses.append("created_at >= :after")
        params["after"] = filters_dict["created_after"]

    # Count matching users
    count_sql = "SELECT COUNT(*) FROM users"
    if where_clauses:
        count_sql += " WHERE " + " AND ".join(where_clauses)

    count_result = await db.execute(text(count_sql), params)
    total_users = count_result.scalar() or 0

    # Update broadcast status
    broadcast.status = "sending"
    broadcast.total_count = total_users
    await db.commit()

    # Start sending in background
    asyncio.create_task(
        _process_broadcast(broadcast_id, admin.id, admin.username, filters_dict)
    )

    await log_admin_action(
        db,
        admin.id,
        admin.username,
        "broadcast_send",
        entity_type="broadcast",
        entity_id=str(broadcast_id),
        details=f"Started broadcast #{broadcast_id} to {total_users} users (filters: {filters_dict})",
    )

    return BroadcastStatusResponse(
        id=broadcast.id,
        status=broadcast.status,
        sent_count=0,
        total_count=total_users,
        error_count=0,
    )


async def _process_broadcast(
    broadcast_id: int,
    admin_id: int,
    admin_username: str,
    filters: dict | None = None,
):
    """Process a broadcast in the background with optional filters"""
    from admin.database import async_session_factory

    async with async_session_factory() as db:
        try:
            result = await db.execute(
                select(Broadcast).where(Broadcast.id == broadcast_id)
            )
            broadcast = result.scalar_one_or_none()
            if not broadcast:
                return

            # Build query with filters
            where_clauses = []
            params = {}

            if filters:
                if "language" in filters and filters["language"]:
                    where_clauses.append("language = :lang")
                    params["lang"] = filters["language"]
                if "min_balance" in filters:
                    where_clauses.append("balance >= :min_bal")
                    params["min_bal"] = int(filters["min_balance"])
                if "max_balance" in filters:
                    where_clauses.append("balance <= :max_bal")
                    params["max_bal"] = int(filters["max_balance"])
                if "created_after" in filters:
                    where_clauses.append("created_at >= :after")
                    params["after"] = filters["created_after"]

            sql = "SELECT telegram_id FROM users"
            if where_clauses:
                sql += " WHERE " + " AND ".join(where_clauses)
            sql += " ORDER BY telegram_id"

            users_result = await db.execute(text(sql), params)
            users = users_result.fetchall()

            sent = 0
            errors = 0

            for user_row in users:
                telegram_id = user_row[0]
                try:
                    success = await send_broadcast_message(
                        telegram_id,
                        broadcast.message_type,
                        broadcast.content,
                        broadcast.file_id,
                        broadcast.file_url,
                        broadcast.buttons,
                    )
                    if success:
                        sent += 1
                    else:
                        errors += 1
                except Exception as e:
                    logger.error(f"Broadcast error for {telegram_id}: {e}")
                    errors += 1

                if (sent + errors) % 10 == 0:
                    await db.execute(
                        text(
                            "UPDATE broadcasts SET sent_count = :sent, error_count = :err "
                            "WHERE id = :bid"
                        ),
                        {"sent": sent, "err": errors, "bid": broadcast_id},
                    )
                    await db.commit()

                await asyncio.sleep(0.05)

            broadcast.status = "completed"
            broadcast.sent_count = sent
            broadcast.error_count = errors
            broadcast.completed_at = datetime.now(timezone.utc)
            await db.commit()

            await log_admin_action(
                db,
                admin_id,
                admin_username,
                "broadcast_completed",
                entity_type="broadcast",
                entity_id=str(broadcast_id),
                details=f"Broadcast #{broadcast_id} completed. Sent: {sent}, Errors: {errors}, Total: {len(users)}",
            )

        except Exception as e:
            logger.exception(f"Broadcast processing error: {e}")
            await db.execute(
                text("UPDATE broadcasts SET status = 'cancelled' WHERE id = :bid"),
                {"bid": broadcast_id},
            )
            await db.commit()
