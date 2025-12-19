"""
Migration script: Add profile_image column to users table
Run this once to add the new column
"""

import asyncio
from sqlalchemy import text
from database import engine


async def migrate():
    async with engine.begin() as conn:
        # Add profile_image column if not exists
        await conn.execute(text("""
            ALTER TABLE users 
            ADD COLUMN IF NOT EXISTS profile_image VARCHAR;
        """))
        print("✅ Migration complete: profile_image column added!")


if __name__ == "__main__":
    asyncio.run(migrate())
