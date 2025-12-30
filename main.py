"""
STORM EAGLE - NFT Giveaway Landing Page
FastAPI Backend with Real-time Stats
"""

from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import FileResponse
from sqlalchemy import select, func, text
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
            result_all = await session.execute(text("SELECT COUNT(*) FROM users"))
            # RANDOM uchun yaroqli ishtirokchilar
            # Shartlar: phone mavjud, is_uzb=true, ref orqali kelganlar is_activated bo'lishi kerak, ban va block bo'lmagan
            result = await session.execute(
                text("""
                    SELECT COUNT(*) FROM users 
                    WHERE phone IS NOT NULL 
                      AND is_uzb = true 
                      AND (ref_id IS NULL OR is_activated = true)
                      AND is_ban = false 
                      AND is_blocked = false
                      AND created_at < '2025-12-31 00:00:00'
                """)
            )
            total_users = result_all.scalar() or 0
            total_participants = result.scalar() or 0
            
            # TOP 20 by activated_referrals (TOP 10 = winners, 11-20 = runners-up)
            result = await session.execute(
                text("""
                    SELECT user_id, username, fullname, activated_referrals, profile_image 
                    FROM users 
                    WHERE activated_referrals > 0 
                      AND is_ban = false 
                      AND is_uzb = true 
                      AND created_at < '2025-12-31 00:00:00'
                    ORDER BY activated_referrals DESC
                    LIMIT 20
                """)
            )
            users = result.fetchall()
            top_20 = [
                {
                    "user_id": row[0],
                    "username": row[1] or "Anonymous",
                    "fullname": row[2] or "Foydalanuvchi",
                    "referrals": row[3],
                    "profile_image": row[4] or f"https://api.dicebear.com/7.x/avataaars/svg?seed={row[0]}"
                }
                for row in users
            ]
            
            return {
                "success": True,
                "participants": total_participants,
                "users": total_users,
                "top_prizes": 10,
                "random_prizes": 20,
                "total_prizes": 30,
                "top_20": top_20
            }
    except Exception as e:
        # If there's an error, try to at least get participant count
        try:
            async with async_session() as session:
                result = await session.execute(
                    text("SELECT COUNT(*) FROM users")
                )
                total_participants = result.scalar() or 0
        except:
            total_participants = 0
        
        return {
            "success": False,
            "participants": total_participants,
            "users": total_participants,
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
