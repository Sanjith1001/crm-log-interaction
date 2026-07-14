import uuid
from sqlalchemy import select, or_
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.hcp import Hcp
from app.schemas.hcp import HcpCreate

async def get_hcp_by_id(db: AsyncSession, hcp_id: uuid.UUID) -> Hcp | None:
    result = await db.execute(select(Hcp).where(Hcp.id == hcp_id))
    return result.scalar_one_or_none()

async def search_hcps(db: AsyncSession, query: str | None = None) -> list[Hcp]:
    stmt = select(Hcp)
    if query:
        clean_query = query.strip()
        # Clean common doctor prefixes for fuzzy search
        for prefix in ["dr.", "dr ", "doctor.", "doctor "]:
            if clean_query.lower().startswith(prefix):
                clean_query = clean_query[len(prefix):].strip()
                
        stmt = stmt.where(
            or_(
                Hcp.name.ilike(f"%{clean_query}%"),
                Hcp.specialty.ilike(f"%{query}%"),
                Hcp.hospital.ilike(f"%{query}%"),
                Hcp.city.ilike(f"%{query}%")
            )
        )
    result = await db.execute(stmt)
    return list(result.scalars().all())

async def create_hcp(db: AsyncSession, hcp_in: HcpCreate) -> Hcp:
    hcp = Hcp(**hcp_in.model_dump())
    db.add(hcp)
    await db.commit()
    await db.refresh(hcp)
    return hcp
