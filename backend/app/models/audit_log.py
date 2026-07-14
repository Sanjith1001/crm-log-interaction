import uuid
from datetime import datetime
from sqlalchemy import DateTime, ForeignKey, String, JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.models import Base

class AuditLog(Base):
    __tablename__ = "audit_log"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    interaction_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("interaction.id", ondelete="SET NULL"), nullable=True)
    actor_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("representative.id", ondelete="CASCADE"), nullable=False)
    tool_used: Mapped[str] = mapped_column(String(255), nullable=False)
    before: Mapped[dict] = mapped_column(JSON, nullable=True)
    after: Mapped[dict] = mapped_column(JSON, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    # Relationships
    interaction = relationship("Interaction", backref="audit_logs")
    actor = relationship("Representative", backref="audit_logs")
