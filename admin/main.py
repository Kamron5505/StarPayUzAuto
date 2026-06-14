"""Admin Panel — FastAPI application entry point"""
import logging
import os
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from admin.config import ADMIN_IDS, CORS_ORIGINS, DEFAULT_ADMIN_PASSWORD, DEFAULT_ADMIN_USERNAME, STATIC_DIR
from admin.database import async_session_factory, init_models
from admin.models.admin_user import AdminUser
from admin.routers import auth, balance, broadcasts, dashboard, logs, orders, settings as settings_router, users, ws
from admin.services.auth_service import hash_password

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan: startup and shutdown"""
    # Startup
    logger.info("Starting admin panel...")
    await init_models()
    await _ensure_default_admin()
    await _init_redis()
    logger.info("Admin panel startup complete")
    yield
    # Shutdown
    from admin.database import dispose_engine
    await dispose_engine()
    logger.info("Admin panel shutdown complete")


async def _init_redis():
    """Initialize Redis connection on startup"""
    try:
        from admin.services.cache import get_redis
        r = await get_redis()
        if r:
            logger.info("Redis cache initialized successfully")
        else:
            logger.warning("Redis not available - caching disabled")
    except Exception as e:
        logger.warning(f"Redis initialization skipped: {e}")


async def _ensure_default_admin():
    """Create default admin user if none exists"""
    async with async_session_factory() as db:
        from sqlalchemy import select
        result = await db.execute(select(AdminUser).limit(1))
        existing = result.scalar_one_or_none()
        if not existing:
            admin = AdminUser(
                username=DEFAULT_ADMIN_USERNAME,
                password_hash=hash_password(DEFAULT_ADMIN_PASSWORD),
                role="superadmin",
                is_active=True,
            )
            # Also link telegram admins if ADMIN_IDS are set
            db.add(admin)
            await db.commit()
            logger.info(f"Default admin created: {DEFAULT_ADMIN_USERNAME} / {DEFAULT_ADMIN_PASSWORD}")

        # Ensure admins from ADMIN_IDS env exist
        for tid in ADMIN_IDS:
            result = await db.execute(
                select(AdminUser).where(AdminUser.telegram_id == tid)
            )
            admin = result.scalar_one_or_none()
            if not admin:
                admin = AdminUser(
                    telegram_id=tid,
                    username=f"admin_{tid}",
                    password_hash=hash_password(f"admin_{tid}"),
                    role="admin",
                    is_active=True,
                )
                db.add(admin)
                await db.commit()
                logger.info(f"Admin created from ADMIN_IDS: telegram_id={tid}")
            elif not admin.telegram_id:
                admin.telegram_id = tid
                await db.commit()


def create_app() -> FastAPI:
    """Create and configure the FastAPI application"""
    app = FastAPI(
        title="StarPayUz Admin Panel",
        description="Professional admin panel for StarPayUz Telegram bot",
        version="1.0.0",
        lifespan=lifespan,
    )

    # CORS
    app.add_middleware(
        CORSMiddleware,
        allow_origins=CORS_ORIGINS,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Include routers
    app.include_router(auth.router)
    app.include_router(dashboard.router)
    app.include_router(users.router)
    app.include_router(balance.router)
    app.include_router(broadcasts.router)
    app.include_router(settings_router.router)
    app.include_router(logs.router)
    app.include_router(orders.router)
    app.include_router(ws.router)

    # Serve static files (SPA frontend)
    if STATIC_DIR.exists():
        app.mount("/", StaticFiles(directory=str(STATIC_DIR), html=True), name="static")

    # Health check
    @app.get("/health")
    async def health():
        return {"ok": True, "service": "StarPayUz Admin Panel", "version": "1.0.0"}

    return app


app = create_app()


def main():
    """Run the admin panel server"""
    import uvicorn

    host = os.environ.get("ADMIN_HOST", "0.0.0.0")
    port = int(os.environ.get("ADMIN_PORT", "8000"))
    log_level = os.environ.get("LOG_LEVEL", "info").lower()

    uvicorn.run(
        "admin.main:app",
        host=host,
        port=port,
        reload=False,
        log_level=log_level,
    )


if __name__ == "__main__":
    main()
