from __future__ import annotations

import enum
from datetime import datetime
from decimal import Decimal

from sqlalchemy import DECIMAL, Enum, ForeignKey, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class DealStatus(str, enum.Enum):
    new = "new"
    in_progress = "in_progress"
    won = "won"
    lost = "lost"


class DealStage(str, enum.Enum):
    qualification = "qualification"
    proposal = "proposal"
    negotiation = "negotiation"
    closed = "closed"


class Deal(Base):
    __tablename__ = "deals"

    organization_id: Mapped[int] = mapped_column(ForeignKey("organizations.id"), nullable=False)
    contact_id: Mapped[int] = mapped_column(ForeignKey("contacts.id"), nullable=False)
    owner_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    amount: Mapped[Decimal] = mapped_column(DECIMAL(12, 2), nullable=False, default=0)
    currency: Mapped[str] = mapped_column(String(10), default="USD", nullable=False)
    status: Mapped[DealStatus] = mapped_column(Enum(DealStatus), default=DealStatus.new, nullable=False)
    stage: Mapped[DealStage] = mapped_column(Enum(DealStage), default=DealStage.qualification, nullable=False)
    created_at: Mapped[datetime] = mapped_column(server_default=func.now(), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(server_default=func.now(), onupdate=func.now(), nullable=False)

    organization = relationship("Organization", back_populates="deals")
    contact = relationship("Contact", back_populates="deals")
    owner = relationship("User", back_populates="deals")
    tasks = relationship("Task", back_populates="deal", cascade="all, delete")
    activities = relationship("Activity", back_populates="deal", cascade="all, delete")


