import uuid
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.audit_log import AuditLog

async def create_audit_log(
    db: AsyncSession,
    actor_id: uuid.UUID,
    tool_used: str,
    interaction_id: uuid.UUID | None = None,
    before: dict | None = None,
    after: dict | None = None
) -> AuditLog:
    log_entry = AuditLog(
        actor_id=actor_id,
        tool_used=tool_used,
        interaction_id=interaction_id,
        before=before,
        after=after
    )
    db.add(log_entry)
    await db.commit()
    await db.refresh(log_entry)
    return log_entry
