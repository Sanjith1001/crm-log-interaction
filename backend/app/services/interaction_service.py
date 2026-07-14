import uuid
from datetime import date
from sqlalchemy import select, or_
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.interaction import Interaction
from app.models.product import Product
from app.schemas.interaction import InteractionCreate
from app.services.audit_service import create_audit_log

async def get_interaction_by_id(db: AsyncSession, interaction_id: uuid.UUID) -> Interaction | None:
    stmt = (
        select(Interaction)
        .options(selectinload(Interaction.hcp), selectinload(Interaction.products))
        .where(Interaction.id == interaction_id)
    )
    result = await db.execute(stmt)
    return result.scalar_one_or_none()

async def list_interactions(
    db: AsyncSession,
    representative_id: uuid.UUID | None = None,
    hcp_id: uuid.UUID | None = None,
    query: str | None = None,
) -> list[Interaction]:
    stmt = (
        select(Interaction)
        .options(selectinload(Interaction.hcp), selectinload(Interaction.products))
        .order_by(Interaction.visit_date.desc(), Interaction.created_at.desc())
    )
    if representative_id:
        stmt = stmt.where(Interaction.representative_id == representative_id)
    if hcp_id:
        stmt = stmt.where(Interaction.hcp_id == hcp_id)
    if query:
        from app.models.hcp import Hcp
        stmt = stmt.join(Interaction.hcp).where(
            or_(
                Interaction.raw_notes.ilike(f"%{query}%"),
                Interaction.summary.ilike(f"%{query}%"),
                Hcp.name.ilike(f"%{query}%"),
            )
        )
    result = await db.execute(stmt)
    return list(result.scalars().all())

async def create_interaction(
    db: AsyncSession,
    interaction_in: InteractionCreate,
    representative_id: uuid.UUID
) -> Interaction:
    products = []
    if interaction_in.products_discussed:
        prod_stmt = select(Product).where(Product.id.in_(interaction_in.products_discussed))
        prod_res = await db.execute(prod_stmt)
        products = list(prod_res.scalars().all())

    db_obj = Interaction(
        hcp_id=interaction_in.hcp_id,
        representative_id=representative_id,
        visit_date=interaction_in.visit_date,
        raw_notes=interaction_in.raw_notes,
        summary=interaction_in.summary,
        extracted_entities=interaction_in.extracted_entities or {},
        samples_given=interaction_in.samples_given or [],
        action_items=interaction_in.action_items or [],
        follow_up_date=interaction_in.follow_up_date,
        source=interaction_in.source,
        products=products
    )
    db.add(db_obj)
    await db.commit()

    interaction = await get_interaction_by_id(db, db_obj.id)

    after_state = {
        "hcp_id": str(interaction.hcp_id),
        "visit_date": str(interaction.visit_date),
        "raw_notes": interaction.raw_notes,
        "summary": interaction.summary,
        "samples_given": interaction.samples_given,
        "action_items": interaction.action_items,
        "follow_up_date": str(interaction.follow_up_date) if interaction.follow_up_date else None,
        "products": [p.name for p in interaction.products]
    }
    await create_audit_log(
        db=db,
        actor_id=representative_id,
        tool_used="log_interaction",
        interaction_id=interaction.id,
        before=None,
        after=after_state
    )

    return interaction

async def update_interaction(
    db: AsyncSession,
    interaction_id: uuid.UUID,
    data: dict,
    representative_id: uuid.UUID
) -> Interaction | None:
    interaction = await get_interaction_by_id(db, interaction_id)
    if not interaction:
        return None

    before_state = {
        "hcp_id": str(interaction.hcp_id),
        "visit_date": str(interaction.visit_date),
        "raw_notes": interaction.raw_notes,
        "summary": interaction.summary,
        "samples_given": interaction.samples_given,
        "action_items": interaction.action_items,
        "follow_up_date": str(interaction.follow_up_date) if interaction.follow_up_date else None,
        "products": [p.name for p in interaction.products]
    }

    for field in ["visit_date", "raw_notes", "summary", "extracted_entities", "samples_given", "action_items", "follow_up_date"]:
        if field in data:
            val = data[field]
            if field in ["visit_date", "follow_up_date"] and isinstance(val, str) and val:
                val = date.fromisoformat(val)
            setattr(interaction, field, val)

    if "products_discussed" in data:
        prod_stmt = select(Product).where(Product.id.in_(data["products_discussed"]))
        prod_res = await db.execute(prod_stmt)
        interaction.products = list(prod_res.scalars().all())

    await db.commit()

    updated_interaction = await get_interaction_by_id(db, interaction.id)

    after_state = {
        "hcp_id": str(updated_interaction.hcp_id),
        "visit_date": str(updated_interaction.visit_date),
        "raw_notes": updated_interaction.raw_notes,
        "summary": updated_interaction.summary,
        "samples_given": updated_interaction.samples_given,
        "action_items": updated_interaction.action_items,
        "follow_up_date": str(updated_interaction.follow_up_date) if updated_interaction.follow_up_date else None,
        "products": [p.name for p in updated_interaction.products]
    }

    await create_audit_log(
        db=db,
        actor_id=representative_id,
        tool_used="edit_interaction",
        interaction_id=updated_interaction.id,
        before=before_state,
        after=after_state
    )

    return updated_interaction
