from __future__ import annotations

import enum
from datetime import datetime

from sqlalchemy import Enum, ForeignKey, JSON, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class ActivityType(str, enum.Enum):
    comment = "comment"
    status_changed = "status_changed"
    stage_changed = "stage_changed"
    task_created = "task_created"
    system = "system"


class Activity(Base):
    __tablename__ = "activities"

    deal_id: Mapped[int] = mapped_column(ForeignKey("deals.id"), nullable=False, index=True)
    author_id: Mapped[int | None] = mapped_column(ForeignKey("users.id"), nullable=True)
    type: Mapped[ActivityType] = mapped_column(Enum(ActivityType), default=ActivityType.system, nullable=False)
    payload: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    created_at: Mapped[datetime] = mapped_column(server_default=func.now(), nullable=False)

    deal = relationship("Deal", back_populates="activities")


