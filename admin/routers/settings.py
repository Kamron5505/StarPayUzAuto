"""Settings management router"""
import logging

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from admin.database import get_db
from admin.models.setting import AppSetting
from admin.routers.auth import require_admin
from admin.schemas.auth import AdminUserInfo
from admin.schemas.settings import SettingInfo, SettingUpdate, SettingsListResponse
from admin.services.log_service import log_admin_action

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/admin/settings", tags=["settings"])


@router.get("", response_model=SettingsListResponse)
async def get_settings(
    admin: AdminUserInfo = Depends(require_admin),
    db: AsyncSession = Depends(get_db),
):
    """Get all settings"""
    result = await db.execute(select(AppSetting).order_by(AppSetting.category, AppSetting.key))
    settings = result.scalars().all()

    return SettingsListResponse(
        settings=[
            SettingInfo(
                id=s.id,
                key=s.key,
                value=s.value,
                description=s.description,
                category=s.category,
                updated_at=s.updated_at,
                updated_by=s.updated_by,
            )
            for s in settings
        ]
    )


@router.get("/{key}", response_model=SettingInfo)
async def get_setting(
    key: str,
    admin: AdminUserInfo = Depends(require_admin),
    db: AsyncSession = Depends(get_db),
):
    """Get a single setting by key"""
    result = await db.execute(
        select(AppSetting).where(AppSetting.key == key)
    )
    setting = result.scalar_one_or_none()
    if not setting:
        raise HTTPException(status_code=404, detail="Setting not found")

    return SettingInfo(
        id=setting.id,
        key=setting.key,
        value=setting.value,
        description=setting.description,
        category=setting.category,
        updated_at=setting.updated_at,
        updated_by=setting.updated_by,
    )


@router.put("/{key}", response_model=SettingInfo)
async def update_setting(
    key: str,
    request: SettingUpdate,
    admin: AdminUserInfo = Depends(require_admin),
    db: AsyncSession = Depends(get_db),
):
    """Update a setting value"""
    result = await db.execute(
        select(AppSetting).where(AppSetting.key == key)
    )
    setting = result.scalar_one_or_none()

    if not setting:
        raise HTTPException(status_code=404, detail="Setting not found")

    old_value = setting.value
    setting.value = request.value
    setting.updated_by = admin.id
    await db.commit()
    await db.refresh(setting)

    await log_admin_action(
        db,
        admin.id,
        admin.username,
        "settings_change",
        entity_type="settings",
        entity_id=key,
        details=f"Updated setting '{key}': '{old_value[:50]}' -> '{request.value[:50]}'",
    )

    return SettingInfo(
        id=setting.id,
        key=setting.key,
        value=setting.value,
        description=setting.description,
        category=setting.category,
        updated_at=setting.updated_at,
        updated_by=setting.updated_by,
    )


@router.post("/init")
async def initialize_default_settings(
    admin: AdminUserInfo = Depends(require_admin),
    db: AsyncSession = Depends(get_db),
):
    """Initialize default settings if they don't exist"""
    default_settings = {
        # Service prices
        "stars_price_per_unit": {"value": "200", "description": "Price per 1 Star (in UZS)", "category": "prices"},
        "premium_3_months_price": {"value": "160000", "description": "Premium 3 months price (UZS)", "category": "prices"},
        "premium_6_months_price": {"value": "225000", "description": "Premium 6 months price (UZS)", "category": "prices"},
        "premium_12_months_price": {"value": "380000", "description": "Premium 12 months price (UZS)", "category": "prices"},
        "phone_number_price": {"value": "50000", "description": "Virtual phone number price (UZS)", "category": "prices"},
        
        # Commissions
        "referral_bonus": {"value": "5000", "description": "Referral bonus amount (UZS)", "category": "commissions"},
        "admin_commission_percent": {"value": "5", "description": "Admin commission percentage", "category": "commissions"},
        
        # Limits
        "min_topup_amount": {"value": "10000", "description": "Minimum top-up amount (UZS)", "category": "limits"},
        "max_topup_amount": {"value": "10000000", "description": "Maximum top-up amount (UZS)", "category": "limits"},
        "min_stars_amount": {"value": "50", "description": "Minimum stars purchase amount", "category": "limits"},
        "max_stars_amount": {"value": "1000000", "description": "Maximum stars purchase amount", "category": "limits"},
        
        # General
        "support_username": {"value": "StarPayUzAdmin", "description": "Support Telegram username", "category": "general"},
        "support_channel": {"value": "StarPayUzNews", "description": "Channel username", "category": "general"},
        "support_group": {"value": "StarPayUz_Chat", "description": "Group username", "category": "general"},
        "maintenance_mode": {"value": "false", "description": "Enable maintenance mode", "category": "general"},
    }

    created = []
    for key, cfg in default_settings.items():
        result = await db.execute(
            select(AppSetting).where(AppSetting.key == key)
        )
        if not result.scalar_one_or_none():
            setting = AppSetting(
                key=key,
                value=cfg["value"],
                description=cfg["description"],
                category=cfg["category"],
                updated_by=admin.id,
            )
            db.add(setting)
            created.append(key)

    await db.commit()

    await log_admin_action(
        db,
        admin.id,
        admin.username,
        "settings_init",
        entity_type="settings",
        details=f"Initialized {len(created)} default settings: {', '.join(created)}",
    )

    return {"ok": True, "created": len(created), "keys": created}
