from collections.abc import AsyncIterator
from dataclasses import dataclass
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from app.config import settings

engine = create_async_engine(settings.database_url, future=True)
async_session_maker = async_sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)

@dataclass(frozen=True)
class CurrentRep:
    id: str
    name: str = "Demo Rep"

async def get_db_session() -> AsyncIterator[AsyncSession]:
    async with async_session_maker() as session:
        try:
            yield session
        except Exception:
            await session.rollback()
            raise

async def current_rep() -> CurrentRep:
    # Use a fixed UUID for the demo representative
    return CurrentRep(id="e0a6d45e-4c07-4228-b9a5-1ffef76e330e", name="Demo Rep")
