"""Balance management router"""
import logging

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from admin.database import get_db
from admin.routers.auth import require_admin
from admin.schemas.auth import AdminUserInfo
from admin.schemas.balance import (
    BalanceChangeRequest,
    BalanceDeductRequest,
    BalanceResetRequest,
    BalanceResponse,
    BalanceSetRequest,
    TransactionHistoryResponse,
    TransactionInfo,
)
from admin.services.log_service import log_admin_action

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/admin/balance", tags=["balance"])


async def _get_user_balance(db: AsyncSession, telegram_id: int) -> int | None:
    """Get user's current balance"""
    result = await db.execute(
        text("SELECT balance FROM users WHERE telegram_id = :tid"),
        {"tid": telegram_id},
    )
    row = result.fetchone()
    return row[0] if row else None


async def _update_user_balance(
    db: AsyncSession, telegram_id: int, new_balance: int
) -> bool:
    """Update user's balance"""
    result = await db.execute(
        text("UPDATE users SET balance = :bal WHERE telegram_id = :tid"),
        {"bal": new_balance, "tid": telegram_id},
    )
    await db.commit()
    return result.rowcount > 0


async def _record_transaction(
    db: AsyncSession,
    telegram_id: int,
    amount: int,
    tx_type: str,
    balance_before: int,
    balance_after: int,
    reason: str | None,
    admin_id: int,
):
    """Record a balance transaction"""
    await db.execute(
        text(
            "INSERT INTO transactions (telegram_id, amount, type, balance_before, "
            "balance_after, reason, admin_id, created_at) "
            "VALUES (:tid, :amt, :typ, :bb, :ba, :reason, :aid, NOW())"
        ),
        {
            "tid": telegram_id,
            "amt": amount,
            "typ": tx_type,
            "bb": balance_before,
            "ba": balance_after,
            "reason": reason or "",
            "aid": admin_id,
        },
    )
    await db.commit()


@router.post("/add")
async def add_balance(
    request: BalanceChangeRequest,
    admin: AdminUserInfo = Depends(require_admin),
    db: AsyncSession = Depends(get_db),
):
    """Add balance to a user"""
    current_balance = await _get_user_balance(db, request.telegram_id)
    if current_balance is None:
        raise HTTPException(status_code=404, detail="User not found")

    new_balance = current_balance + request.amount
    await _update_user_balance(db, request.telegram_id, new_balance)
    await _record_transaction(
        db,
        request.telegram_id,
        request.amount,
        "credit",
        current_balance,
        new_balance,
        request.reason,
        admin.id,
    )

    await log_admin_action(
        db,
        admin.id,
        admin.username,
        "balance_change",
        entity_type="user",
        entity_id=str(request.telegram_id),
        details=f"Added {request.amount} to user {request.telegram_id}. Balance: {current_balance} -> {new_balance}. Reason: {request.reason or 'N/A'}",
    )

    return BalanceResponse(
        telegram_id=request.telegram_id,
        balance_before=current_balance,
        balance_after=new_balance,
        amount=request.amount,
        operation="add",
    )


@router.post("/deduct")
async def deduct_balance(
    request: BalanceDeductRequest,
    admin: AdminUserInfo = Depends(require_admin),
    db: AsyncSession = Depends(get_db),
):
    """Deduct balance from a user"""
    current_balance = await _get_user_balance(db, request.telegram_id)
    if current_balance is None:
        raise HTTPException(status_code=404, detail="User not found")
    if current_balance < request.amount:
        raise HTTPException(
            status_code=400,
            detail=f"Insufficient balance. Current: {current_balance}, Requested: {request.amount}",
        )

    new_balance = current_balance - request.amount
    await _update_user_balance(db, request.telegram_id, new_balance)
    await _record_transaction(
        db,
        request.telegram_id,
        request.amount,
        "debit",
        current_balance,
        new_balance,
        request.reason,
        admin.id,
    )

    await log_admin_action(
        db,
        admin.id,
        admin.username,
        "balance_change",
        entity_type="user",
        entity_id=str(request.telegram_id),
        details=f"Deducted {request.amount} from user {request.telegram_id}. Balance: {current_balance} -> {new_balance}. Reason: {request.reason or 'N/A'}",
    )

    return BalanceResponse(
        telegram_id=request.telegram_id,
        balance_before=current_balance,
        balance_after=new_balance,
        amount=request.amount,
        operation="deduct",
    )


@router.post("/set")
async def set_balance(
    request: BalanceSetRequest,
    admin: AdminUserInfo = Depends(require_admin),
    db: AsyncSession = Depends(get_db),
):
    """Set exact balance for a user"""
    current_balance = await _get_user_balance(db, request.telegram_id)
    if current_balance is None:
        raise HTTPException(status_code=404, detail="User not found")

    await _update_user_balance(db, request.telegram_id, request.amount)
    difference = request.amount - current_balance
    await _record_transaction(
        db,
        request.telegram_id,
        abs(difference),
        "set" if difference >= 0 else "debit",
        current_balance,
        request.amount,
        request.reason,
        admin.id,
    )

    await log_admin_action(
        db,
        admin.id,
        admin.username,
        "balance_change",
        entity_type="user",
        entity_id=str(request.telegram_id),
        details=f"Set balance to {request.amount} for user {request.telegram_id}. Previous: {current_balance}. Reason: {request.reason or 'N/A'}",
    )

    return BalanceResponse(
        telegram_id=request.telegram_id,
        balance_before=current_balance,
        balance_after=request.amount,
        amount=difference,
        operation="set",
    )


@router.post("/reset")
async def reset_balance(
    request: BalanceResetRequest,
    admin: AdminUserInfo = Depends(require_admin),
    db: AsyncSession = Depends(get_db),
):
    """Reset user balance to zero"""
    current_balance = await _get_user_balance(db, request.telegram_id)
    if current_balance is None:
        raise HTTPException(status_code=404, detail="User not found")

    await _update_user_balance(db, request.telegram_id, 0)
    await _record_transaction(
        db,
        request.telegram_id,
        current_balance,
        "reset",
        current_balance,
        0,
        request.reason,
        admin.id,
    )

    await log_admin_action(
        db,
        admin.id,
        admin.username,
        "balance_change",
        entity_type="user",
        entity_id=str(request.telegram_id),
        details=f"Reset balance to 0 for user {request.telegram_id}. Previous: {current_balance}. Reason: {request.reason or 'N/A'}",
    )

    return BalanceResponse(
        telegram_id=request.telegram_id,
        balance_before=current_balance,
        balance_after=0,
        amount=current_balance,
        operation="reset",
    )


@router.get("/history", response_model=TransactionHistoryResponse)
async def get_balance_history(
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=200),
    telegram_id: int | None = Query(None),
    admin: AdminUserInfo = Depends(require_admin),
    db: AsyncSession = Depends(get_db),
):
    """Get balance change history"""
    # Check if transactions table has data, if not return empty
    result = await db.execute(
        text("SELECT COUNT(*) FROM information_schema.tables WHERE table_name = 'transactions'")
    )
    table_exists = result.scalar() or 0

    if not table_exists:
        return TransactionHistoryResponse(total=0, page=page, page_size=page_size, transactions=[])

    if telegram_id:
        count_result = await db.execute(
            text("SELECT COUNT(*) FROM transactions WHERE telegram_id = :tid"),
            {"tid": telegram_id},
        )
        total = count_result.scalar() or 0

        result = await db.execute(
            text(
                "SELECT id, telegram_id, amount, type, balance_before, balance_after, "
                "reason, admin_id, created_at "
                "FROM transactions WHERE telegram_id = :tid "
                "ORDER BY created_at DESC LIMIT :limit OFFSET :offset"
            ),
            {"tid": telegram_id, "limit": page_size, "offset": (page - 1) * page_size},
        )
    else:
        count_result = await db.execute(text("SELECT COUNT(*) FROM transactions"))
        total = count_result.scalar() or 0

        result = await db.execute(
            text(
                "SELECT id, telegram_id, amount, type, balance_before, balance_after, "
                "reason, admin_id, created_at "
                "FROM transactions ORDER BY created_at DESC "
                "LIMIT :limit OFFSET :offset"
            ),
            {"limit": page_size, "offset": (page - 1) * page_size},
        )

    rows = result.fetchall()
    transactions = []
    for row in rows:
        transactions.append(
            TransactionInfo(
                id=row[0],
                telegram_id=row[1],
                amount=row[2],
                type=row[3],
                balance_before=row[4],
                balance_after=row[5],
                reason=row[6],
                admin_id=row[7],
                created_at=row[8],
            )
        )

    return TransactionHistoryResponse(
        total=total, page=page, page_size=page_size, transactions=transactions
    )
