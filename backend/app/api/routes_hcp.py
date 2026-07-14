import uuid
from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from app.deps import get_db_session
from app.services import hcp_service, interaction_service
from app.schemas.hcp import HcpRead

router = APIRouter(tags=["hcp"])

@router.get("/hcp", response_model=list[HcpRead])
async def list_hcps(
    query: str | None = Query(None),
    db: AsyncSession = Depends(get_db_session)
):
    return await hcp_service.search_hcps(db, query=query)

@router.get("/hcp/{hcp_id}")
async def get_hcp(
    hcp_id: uuid.UUID,
    db: AsyncSession = Depends(get_db_session)
):
    hcp = await hcp_service.get_hcp_by_id(db, hcp_id)
    if not hcp:
        raise HTTPException(status_code=404, detail="HCP not found")
        
    interactions = await interaction_service.list_interactions(db, hcp_id=hcp_id)
    
    recent = []
    for inter in interactions:
        recent.append({
            "id": str(inter.id),
            "visit_date": str(inter.visit_date),
            "summary": inter.summary,
            "raw_notes": inter.raw_notes,
            "products_discussed": [p.name for p in inter.products],
            "samples_given": inter.samples_given,
            "action_items": inter.action_items,
            "follow_up_date": str(inter.follow_up_date) if inter.follow_up_date else None,
            "source": inter.source
        })

    return {
        "id": str(hcp.id),
        "name": hcp.name,
        "specialty": hcp.specialty,
        "hospital": hcp.hospital,
        "city": hcp.city,
        "prescription_preferences": hcp.prescription_preferences,
        "recent_interactions": recent
    }
