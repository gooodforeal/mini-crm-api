from __future__ import annotations

from datetime import datetime

from app.models.organization_member import OrganizationRole
from app.schemas.common import ORMModel


class OrganizationOut(ORMModel):
    id: int
    name: str
    created_at: datetime


class OrganizationMemberOut(ORMModel):
    id: int
    organization_id: int
    user_id: int
    role: OrganizationRole
    created_at: datetime


