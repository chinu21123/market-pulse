import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI
from sqlalchemy import text
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.core.database import init_db, SessionLocal
from app.core.security import hash_password
from app.core.health import health_registry
from app.models.user import User
from app.models.watchlist import WatchlistItem
from app.services.memory_service import MarketMemoryService
from app.api.v1 import auth, watchlist, memory, feed, stocks, explain

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("market_pulse")

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: Initialize tables
    logger.info("Initializing database...")
    init_db()
    
    # Auto-seed standard starter account if not present
    db = SessionLocal()
    try:
        demo_user = db.query(User).filter(User.email == "demo@marketpulse.com").first()
        if demo_user and "Judge" in (demo_user.full_name or ""):
            demo_user.full_name = "Alex Mercer"
            db.commit()
        elif not demo_user:
            logger.info("Initializing starter user (demo@marketpulse.com)...")
            demo_user = User(
                email="demo@marketpulse.com",
                hashed_password=hash_password("demo1234"),
                full_name="Alex Mercer",
                persona_level="intermediate",
                preferred_language="en",
                sensitivity_threshold=60,
                sensitivity_tier="balanced"
            )
            db.add(demo_user)
            db.commit()
            db.refresh(demo_user)

            # Add default diversified watchlist
            default_stocks = [
                ("NVDA", "NVIDIA Corporation", "NASDAQ"),
                ("AAPL", "Apple Inc.", "NASDAQ"),
                ("TSLA", "Tesla, Inc.", "NASDAQ"),
                ("MSFT", "Microsoft Corporation", "NASDAQ"),
                ("AMD", "Advanced Micro Devices, Inc.", "NASDAQ"),
                ("AMZN", "Amazon.com, Inc.", "NASDAQ"),
                ("SPY", "SPDR S&P 500 ETF Trust", "NYSE Arca")
            ]
            for sym, comp, ex in default_stocks:
                db.add(WatchlistItem(user_id=demo_user.id, symbol=sym, company_name=comp, exchange=ex))
            db.commit()

            # Create default 4h simulated away baseline snapshot
            logger.info("Generating demo simulated time-away snapshot (4h 23m)...")
            MarketMemoryService.simulate_away(
                user_id=demo_user.id,
                db=db,
                minutes_away=263,
                scenario="tech_divergence"
            )
    except Exception as e:
        logger.error(f"Error seeding demo user: {e}")
    finally:
        db.close()

    yield
    logger.info("Market Pulse backend shutting down.")

app = FastAPI(
    title=settings.PROJECT_NAME,
    description="Smart market watchlist with Market Memory and Meaningful Change Engine for CODE 2026.",
    version="1.0.0",
    lifespan=lifespan
)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Open for hackathon dev simplicity
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount API Routers
app.include_router(auth.router, prefix=settings.API_V1_STR)
app.include_router(watchlist.router, prefix=settings.API_V1_STR)
app.include_router(memory.router, prefix=settings.API_V1_STR)
app.include_router(feed.router, prefix=settings.API_V1_STR)
app.include_router(stocks.router, prefix=settings.API_V1_STR)
app.include_router(explain.router, prefix=settings.API_V1_STR)

@app.get("/health")
def health_check():
    return {
        "status": "healthy",
        "app": settings.PROJECT_NAME,
        "version": "1.0.0",
        "gemini_ready": bool(settings.GEMINI_API_KEY)
    }

@app.get("/health/dependencies")
def dependency_health_check():
    db = SessionLocal()
    try:
        db.execute(text("SELECT 1"))
        health_registry.mark("database", "HEALTHY")
    except Exception:
        health_registry.mark("database", "UNAVAILABLE", "Database check failed")
    finally:
        db.close()

    dependencies = health_registry.snapshot()
    overall = "HEALTHY" if all(item["status"] == "HEALTHY" for item in dependencies.values()) else "DEGRADED"
    return {"status": overall, "dependencies": dependencies}
