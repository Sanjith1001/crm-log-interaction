import uuid
from datetime import date, datetime
from sqlalchemy import Column, Date, DateTime, ForeignKey, String, Table, Text, JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.models import Base

interaction_product = Table(
    "interaction_product",
    Base.metadata,
    Column("interaction_id", ForeignKey("interaction.id", ondelete="CASCADE"), primary_key=True),
    Column("product_id", ForeignKey("product.id", ondelete="CASCADE"), primary_key=True),
)

class Interaction(Base):
    __tablename__ = "interaction"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    hcp_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("hcp.id", ondelete="CASCADE"), nullable=False)
    representative_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("representative.id", ondelete="CASCADE"), nullable=False)
    visit_date: Mapped[date] = mapped_column(Date, nullable=False, default=date.today)
    summary: Mapped[str] = mapped_column(Text, nullable=True)
    raw_notes: Mapped[str] = mapped_column(Text, nullable=False)
    extracted_entities: Mapped[dict] = mapped_column(JSON, nullable=True, default=dict)
    samples_given: Mapped[list] = mapped_column(JSON, nullable=True, default=list)
    action_items: Mapped[list] = mapped_column(JSON, nullable=True, default=list)
    follow_up_date: Mapped[date] = mapped_column(Date, nullable=True)
    source: Mapped[str] = mapped_column(String(50), nullable=False)  # 'form' or 'chat'
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    hcp = relationship("Hcp", backref="interactions")
    representative = relationship("Representative", backref="interactions")
    products = relationship("Product", secondary=interaction_product, backref="interactions")
