from __future__ import annotations

from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, Field

from app.models.deal import DealStage, DealStatus
from app.schemas.common import ORMModel


class DealCreate(BaseModel):
    contact_id: int
    owner_id: int | None = None
    title: str
    amount: Decimal = Field(ge=0)
    currency: str = "USD"


class DealUpdate(BaseModel):
    title: str | None = None
    amount: Decimal | None = Field(default=None, ge=0)
    currency: str | None = None
    status: DealStatus | None = None
    stage: DealStage | None = None


class DealOut(ORMModel):
    id: int
    organization_id: int
    contact_id: int
    owner_id: int
    title: str
    amount: Decimal
    currency: str
    status: DealStatus
    stage: DealStage
    created_at: datetime
    updated_at: datetime


