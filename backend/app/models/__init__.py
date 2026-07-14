from sqlalchemy.orm import DeclarativeBase

class Base(DeclarativeBase):
    pass

from app.models.representative import Representative
from app.models.hcp import Hcp
from app.models.product import Product
from app.models.interaction import Interaction, interaction_product
from app.models.audit_log import AuditLog

__all__ = [
    "Base",
    "Representative",
    "Hcp",
    "Product",
    "Interaction",
    "interaction_product",
    "AuditLog"
]
