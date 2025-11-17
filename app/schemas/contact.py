from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, EmailStr

from app.schemas.common import ORMModel


class ContactCreate(BaseModel):
    name: str
    email: EmailStr | None = None
    phone: str | None = None


class ContactOut(ORMModel):
    id: int
    organization_id: int
    owner_id: int
    name: str
    email: EmailStr | None
    phone: str | None
    created_at: datetime


