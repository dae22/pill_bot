from sqlalchemy import String, Time, Date, DateTime
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from datetime import time, date, datetime
from typing import Optional


engine = create_async_engine("sqlite+aiosqlite:///pills.db")
AsyncSessionLocal = async_sessionmaker(engine, expire_on_commit=False)


class Base(DeclarativeBase):
    pass

class PillOrm(Base):
    __tablename__ = "pills"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(nullable=False)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    time: Mapped[time] = mapped_column(Time, nullable=False)
    last_taken: Mapped[Optional[date]] = mapped_column(Date)
    last_notified: Mapped[Optional[datetime]] = mapped_column(DateTime)

async def create_table():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)