from __future__ import annotations

from fastapi import APIRouter, Depends

from app.api.dependencies.auth import get_current_user
from app.dependencies.services import get_organization_service
from app.models.user import User
from app.schemas.organization import OrganizationOut
from app.services.organizations import OrganizationService

router = APIRouter()


@router.get("/me", response_model=list[OrganizationOut])
async def my_organizations(
    current_user: User = Depends(get_current_user),
    service: OrganizationService = Depends(get_organization_service),
) -> list[OrganizationOut]:
    return await service.get_user_organizations(current_user.id)


