from __future__ import annotations

from datetime import datetime

from sqlalchemy import func, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class Organization(Base):
    __tablename__ = "organizations"

    name: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    created_at: Mapped[datetime] = mapped_column(server_default=func.now(), nullable=False)

    members = relationship("OrganizationMember", back_populates="organization", cascade="all, delete")
    contacts = relationship("Contact", back_populates="organization")
    deals = relationship("Deal", back_populates="organization")


