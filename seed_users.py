"""
Sun'iy test foydalanuvchilarni yaratish
3234 ta user + TOP 10 uchun turli xil referral sonlari
"""

import asyncio
import random
from datetime import datetime, timedelta

from sqlalchemy import delete
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker

from database import Base, User, DATABASE_URL

# Fake names
UZBEK_NAMES = [
    "Jasur", "Sardor", "Bekzod", "Aziz", "Dilshod", "Shoxrux", "Mirjalol", "Bobur",
    "Jahongir", "Rustam", "Alisher", "Nodir", "Farhod", "Ulugbek", "Ravshan", "Botir",
    "Akbar", "Sherzod", "Javohir", "Islom", "Baxtiyor", "Kamol", "Sanjar", "Temur",
    "Nilufar", "Gulnora", "Dilfuza", "Mohira", "Zarina", "Sabina", "Nodira", "Feruza"
]

UZBEK_SURNAMES = [
    "Karimov", "Toshmatov", "Saidov", "Rahimov", "Yusupov", "Alimov", "Xolmatov",
    "Ergashev", "Mirzayev", "Normatov", "Qodirov", "Berdiyev", "Umarov", "Sharipov"
]

RUSSIAN_NAMES = [
    "Alexander", "Dmitry", "Maxim", "Ivan", "Sergey", "Andrey", "Nikolay", "Pavel",
    "Vladimir", "Alexey", "Maria", "Anna", "Elena", "Olga", "Tatiana", "Natalia"
]

RUSSIAN_SURNAMES = [
    "Ivanov", "Petrov", "Sidorov", "Smirnov", "Kuznetsov", "Popov", "Sokolov"
]

# Avatar styles for DiceBear API
AVATAR_STYLES = ["avataaars", "bottts", "micah", "notionists", "open-peeps", "personas"]

def random_avatar(user_id):
    style = random.choice(AVATAR_STYLES)
    return f"https://api.dicebear.com/7.x/{style}/svg?seed={user_id}"


def random_uzbek_name():
    return f"{random.choice(UZBEK_NAMES)} {random.choice(UZBEK_SURNAMES)}"


def random_russian_name():
    return f"{random.choice(RUSSIAN_NAMES)} {random.choice(RUSSIAN_SURNAMES)}"


def random_username(user_id):
    prefixes = ["user", "tg", "crypto", "nft", "eagle", "storm", "winner", "lucky", "top", "best"]
    if random.random() > 0.3:  # 70% have username
        return f"{random.choice(prefixes)}{user_id}"
    return None


def random_phone():
    if random.random() > 0.4:  # 60% have phone
        return f"+998{random.randint(90, 99)}{random.randint(1000000, 9999999)}"
    return None


def random_date_in_last_days(days=30):
    now = datetime.utcnow()
    delta = timedelta(days=random.randint(0, days), hours=random.randint(0, 23), minutes=random.randint(0, 59))
    return now - delta


async def create_fake_users():
    engine = create_async_engine(DATABASE_URL, pool_size=20, max_overflow=50)
    
    # Create tables
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    
    async with async_session() as session:
        # Delete existing users
        print("Deleting existing users...")
        await session.execute(delete(User))
        await session.commit()
        
        users = []
        total_users = 3234
        
        # First, create TOP 10 users with high referrals
        top_10_referrals = [847, 623, 512, 489, 401, 356, 298, 245, 201, 178]
        
        for i, referrals in enumerate(top_10_referrals):
            user_id = 1000000000 + i
            is_uzbek = random.random() > 0.2  # 80% uzbek in top 10
            
            user = User(
                user_id=user_id,
                fullname=random_uzbek_name() if is_uzbek else random_russian_name(),
                username=f"top{i+1}_winner" if random.random() > 0.3 else None,
                ref_id=str(1000000000) if i > 0 else None,  # Top 1 has no ref, others refer to top 1
                is_activated=True,
                phone=random_phone(),
                is_uzb=is_uzbek,
                activated_referrals=referrals,
                repeat_activations=random.randint(0, referrals // 3),
                is_premium=random.random() > 0.5,
                profile_image=random_avatar(user_id),
                stars_balance=random.uniform(0, referrals * 2),
                created_at=random_date_in_last_days(30),
                updated_at=random_date_in_last_days(7)
            )
            users.append(user)
        
        print(f"Created TOP 10 users with referrals: {top_10_referrals}")
        
        # Create remaining users
        remaining = total_users - 10
        
        for i in range(remaining):
            user_id = 1000000010 + i
            is_uzbek = random.random() > 0.15  # 85% uzbek
            is_activated = random.random() > 0.2  # 80% activated
            
            # Random ref_id - some refer to top users, some to each other
            if random.random() > 0.3:
                if random.random() > 0.5:
                    ref_id = str(1000000000 + random.randint(0, 9))  # Refer to top 10
                else:
                    ref_id = str(1000000010 + random.randint(0, max(0, i - 1)))  # Refer to previous users
            else:
                ref_id = None  # No referrer
            
            user = User(
                user_id=user_id,
                fullname=random_uzbek_name() if is_uzbek else random_russian_name(),
                username=random_username(user_id),
                ref_id=ref_id,
                is_activated=is_activated,
                phone=random_phone() if is_activated else None,
                is_uzb=is_uzbek,
                activated_referrals=random.randint(0, 50) if is_activated else 0,
                repeat_activations=random.randint(0, 10),
                is_premium=random.random() > 0.85,  # 15% premium
                profile_image=random_avatar(user_id),
                is_ban=random.random() > 0.98,  # 2% banned
                is_blocked=random.random() > 0.97,  # 3% blocked
                stars_balance=random.uniform(0, 100) if is_activated else 0,
                created_at=random_date_in_last_days(60),
                updated_at=random_date_in_last_days(14)
            )
            users.append(user)
            
            if (i + 1) % 500 == 0:
                print(f"Generated {i + 1}/{remaining} users...")
        
        # Bulk insert
        print(f"Inserting {len(users)} users into database...")
        session.add_all(users)
        await session.commit()
        
        print(f"✅ Successfully created {len(users)} fake users!")
        print(f"   - TOP 10 with referrals: {top_10_referrals}")
        print(f"   - Total: {total_users}")


if __name__ == "__main__":
    asyncio.run(create_fake_users())
