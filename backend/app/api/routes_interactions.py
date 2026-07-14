import uuid
from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from app.deps import get_db_session, current_rep, CurrentRep
from app.services import interaction_service
from app.schemas.interaction import InteractionRead

router = APIRouter(tags=["interactions"])

@router.get("/interactions", response_model=list[InteractionRead])
async def list_interactions(
    query: str | None = Query(None),
    hcp_id: uuid.UUID | None = Query(None),
    db: AsyncSession = Depends(get_db_session),
    rep: CurrentRep = Depends(current_rep)
):
    interactions = await interaction_service.list_interactions(
        db, representative_id=uuid.UUID(rep.id), hcp_id=hcp_id, query=query
    )
    
    res = []
    for inter in interactions:
        res.append(InteractionRead(
            id=inter.id,
            hcp_id=inter.hcp_id,
            hcp_name=inter.hcp.name if inter.hcp else None,
            hcp_specialty=inter.hcp.specialty if inter.hcp else None,
            hcp_hospital=inter.hcp.hospital if inter.hcp else None,
            representative_id=inter.representative_id,
            visit_date=inter.visit_date,
            summary=inter.summary,
            raw_notes=inter.raw_notes,
            extracted_entities=inter.extracted_entities,
            samples_given=inter.samples_given,
            action_items=inter.action_items,
            follow_up_date=inter.follow_up_date,
            source=inter.source,
            products_discussed=[p.name for p in inter.products],
            created_at=inter.created_at,
            updated_at=inter.updated_at
        ))
    return res

@router.get("/interactions/{interaction_id}", response_model=InteractionRead)
async def get_interaction(
    interaction_id: uuid.UUID,
    db: AsyncSession = Depends(get_db_session)
):
    inter = await interaction_service.get_interaction_by_id(db, interaction_id)
    if not inter:
        raise HTTPException(status_code=404, detail="Interaction not found")
        
    return InteractionRead(
        id=inter.id,
        hcp_id=inter.hcp_id,
        hcp_name=inter.hcp.name if inter.hcp else None,
        hcp_specialty=inter.hcp.specialty if inter.hcp else None,
        hcp_hospital=inter.hcp.hospital if inter.hcp else None,
        representative_id=inter.representative_id,
        visit_date=inter.visit_date,
        summary=inter.summary,
        raw_notes=inter.raw_notes,
        extracted_entities=inter.extracted_entities,
        samples_given=inter.samples_given,
        action_items=inter.action_items,
        follow_up_date=inter.follow_up_date,
        source=inter.source,
        products_discussed=[p.name for p in inter.products],
        created_at=inter.created_at,
        updated_at=inter.updated_at
    )
