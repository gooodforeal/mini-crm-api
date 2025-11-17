from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel

from app.models.activity import ActivityType
from app.schemas.common import ORMModel


class ActivityCreate(BaseModel):
    type: ActivityType
    payload: dict


class ActivityOut(ORMModel):
    id: int
    deal_id: int
    author_id: int | None
    type: ActivityType
    payload: dict | None
    created_at: datetime


