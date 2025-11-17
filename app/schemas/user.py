from __future__ import annotations

from datetime import datetime

from pydantic import EmailStr

from app.schemas.common import ORMModel


class UserOut(ORMModel):
    id: int
    email: EmailStr
    name: str
    created_at: datetime


