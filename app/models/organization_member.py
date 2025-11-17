from __future__ import annotations

import enum
from datetime import datetime

from sqlalchemy import Enum, ForeignKey, UniqueConstraint, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class OrganizationRole(str, enum.Enum):
    owner = "owner"
    admin = "admin"
    manager = "manager"
    member = "member"


class OrganizationMember(Base):
    __tablename__ = "organization_members"

    organization_id: Mapped[int] = mapped_column(
        ForeignKey("organizations.id"), index=True, nullable=False
    )
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), index=True, nullable=False)
    role: Mapped[OrganizationRole] = mapped_column(Enum(OrganizationRole), nullable=False)
    created_at: Mapped[datetime] = mapped_column(server_default=func.now(), nullable=False)

    __table_args__ = (UniqueConstraint("organization_id", "user_id", name="uq_org_user"),)

    organization = relationship("Organization", back_populates="members")
    user = relationship("User", back_populates="memberships")


