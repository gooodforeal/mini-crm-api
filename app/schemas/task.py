from __future__ import annotations

from datetime import date, datetime

from pydantic import BaseModel

from app.schemas.common import ORMModel


class TaskCreate(BaseModel):
    deal_id: int
    title: str
    description: str | None = None
    due_date: date


class TaskOut(ORMModel):
    id: int
    deal_id: int
    owner_id: int
    title: str
    description: str | None
    due_date: date
    is_done: bool
    created_at: datetime


