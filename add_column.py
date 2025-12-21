import asyncio
from database import async_session
from sqlalchemy import text

async def add_column():
    async with async_session() as session:
        await session.execute(
            text("ALTER TABLE users ADD COLUMN IF NOT EXISTS profile_image VARCHAR(500)")
        )
        await session.commit()
        print("profile_image column added successfully!")

asyncio.run(add_column())
