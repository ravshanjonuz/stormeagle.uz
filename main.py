"""
STORM EAGLE - NFT Giveaway Landing Page
FastAPI Backend with Real-time Stats
"""

from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import FileResponse
from sqlalchemy import select, func
import os

from database import async_session, User

app = FastAPI(
    title="STORM EAGLE",
    description="Telegram NFT Giveaway Landing Page",
    version="1.0.0"
)

# Get base directory
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Mount static files
app.mount("/static", StaticFiles(directory=os.path.join(BASE_DIR, "static")), name="static")

# Templates
templates = Jinja2Templates(directory=os.path.join(BASE_DIR, "templates"))


@app.get("/")
async def home(request: Request):
    """Serve the main landing page"""
    return templates.TemplateResponse("index.html", {"request": request})


@app.get("/api/stats")
async def get_stats():
    """Get real-time statistics from database"""
    try:
        async with async_session() as session:
            # Total participants count
            result = await session.execute(
                select(func.count(User.id))
            )
            total_participants = result.scalar() or 0
            
            # TOP 20 by activated_referrals (TOP 10 = winners, 11-20 = runners-up)
            result = await session.execute(
                select(User.user_id, User.username, User.fullname, User.activated_referrals, User.profile_image)
                .where(User.is_activated == True)
                .order_by(User.activated_referrals.desc())
                .limit(20)
            )
            top_20 = [
                {
                    "user_id": row.user_id,
                    "username": row.username or "Anonymous",
                    "fullname": row.fullname or "Foydalanuvchi",
                    "referrals": row.activated_referrals,
                    "profile_image": row.profile_image or f"https://api.dicebear.com/7.x/avataaars/svg?seed={row.user_id}"
                }
                for row in result.fetchall()
            ]
            
            return {
                "success": True,
                "participants": total_participants,
                "top_prizes": 10,
                "random_prizes": 20,
                "total_prizes": 30,
                "top_20": top_20
            }
    except Exception as e:
        # If database is not available, return default values
        return {
            "success": False,
            "participants": 500,
            "top_prizes": 10,
            "random_prizes": 20,
            "total_prizes": 30,
            "top_20": [],
            "error": str(e)
        }


@app.get("/favicon.ico")
async def favicon():
    """Serve favicon"""
    favicon_path = os.path.join(BASE_DIR, "static", "favicon.ico")
    if os.path.exists(favicon_path):
        return FileResponse(favicon_path)
    return FileResponse(os.path.join(BASE_DIR, "static", "images", "eagle.png"))


@app.get("/health")
async def health():
    return {"status": "ok", "service": "storm-eagle"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
