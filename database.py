from datetime import datetime
import pytz

from sqlalchemy import Column, String, Boolean, DateTime, BigInteger, Float
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# Database config
DB_USER = "postgres"
DB_PASS = "1"
DB_HOST = "localhost"
DB_NAME = "stormeagle"

DATABASE_URL = f"postgresql+asyncpg://{DB_USER}:{DB_PASS}@{DB_HOST}/{DB_NAME}"

# Toshkent timezone
toshkent_tz = pytz.timezone('Asia/Tashkent')

def toshkent_now():
    return datetime.now(toshkent_tz)

# Engine and session
engine = create_async_engine(DATABASE_URL, pool_size=20, max_overflow=100)
async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

Base = declarative_base()


class User(Base):
    __tablename__ = 'users'

    id = Column(BigInteger, primary_key=True)
    user_id = Column(BigInteger, unique=True)
    fullname = Column(String)
    username = Column(String)

    ref_id = Column(String, nullable=True)

    is_activated = Column(Boolean, nullable=False, default=False)
    phone = Column(String, nullable=True)
    is_voice_activated = Column(Boolean, default=False)
    is_uzb = Column(Boolean, nullable=False, default=True)

    stars_balance = Column(Float, nullable=False, default=0.0)

    is_entity_ready = Column(Boolean, default=False)
    is_ban = Column(Boolean, default=False)

    activated_referrals = Column(BigInteger, nullable=False, default=0)
    repeat_activations = Column(BigInteger, nullable=False, default=0)
    captcha_value = Column(String, nullable=True)
    is_blocked = Column(Boolean, nullable=False, default=False)
    is_premium = Column(Boolean, nullable=False, default=False)
    profile_image = Column(String, nullable=True)  # Avatar URL for TOP display

    updated_at = Column(DateTime, default=toshkent_now, onupdate=toshkent_now)
    created_at = Column(DateTime, default=toshkent_now)


class WithdrawRequest(Base):
    __tablename__ = "withdraw_requests"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    user_id = Column(BigInteger, nullable=False)
    stars = Column(BigInteger, nullable=False)
    gift_id = Column(BigInteger, nullable=False)
    emoji = Column(String(10), nullable=False)
    status = Column(String(20), default="pending")
    created_at = Column(DateTime, default=toshkent_now)


async def get_db():
    async with async_session() as session:
        yield session
