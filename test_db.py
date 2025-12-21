import asyncio
from database import async_session
from sqlalchemy import text

async def test():
    async with async_session() as session:
        result = await session.execute(
            text("SELECT user_id, username, fullname, activated_referrals FROM users WHERE is_activated = true ORDER BY activated_referrals DESC LIMIT 5")
        )
        for row in result.fetchall():
            print(f"user_id={row[0]}, username={row[1]}, fullname={row[2]}, referrals={row[3]}")

asyncio.run(test())
