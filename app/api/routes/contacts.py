from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Query, status

from app.api.dependencies.auth import get_current_user, get_organization_context
from app.dependencies.services import get_contact_service
from app.models.organization_member import OrganizationRole
from app.models.user import User
from app.schemas.contact import ContactCreate, ContactOut
from app.services.contacts import ContactService
from app.services.organizations import OrganizationContext

router = APIRouter()


@router.get("", response_model=list[ContactOut])
async def list_contacts(
    search: str | None = None,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, le=100),
    owner_id: int | None = None,
    current_user: User = Depends(get_current_user),
    org_context: OrganizationContext = Depends(get_organization_context),
    service: ContactService = Depends(get_contact_service),
) -> list[ContactOut]:
    if org_context.role == OrganizationRole.member:
        owner_id = current_user.id
    try:
        return await service.list_contacts(
            organization_id=org_context.organization.id,
            role=org_context.role,
            owner_id=owner_id,
            search=search,
            page=page,
            page_size=page_size,
        )
    except Exception as exc:
        raise HTTPException(status_code=getattr(exc, "status_code", 400), detail=str(exc)) from exc


@router.post("", response_model=ContactOut, status_code=status.HTTP_201_CREATED)
async def create_contact(
    payload: ContactCreate,
    current_user: User = Depends(get_current_user),
    org_context: OrganizationContext = Depends(get_organization_context),
    service: ContactService = Depends(get_contact_service),
) -> ContactOut:
    try:
        return await service.create_contact(
            organization_id=org_context.organization.id,
            owner_id=current_user.id,
            **payload.model_dump(),
        )
    except Exception as exc:
        raise HTTPException(status_code=getattr(exc, "status_code", 400), detail=str(exc)) from exc


@router.delete("/{contact_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_contact(
    contact_id: int,
    current_user: User = Depends(get_current_user),
    org_context: OrganizationContext = Depends(get_organization_context),
    service: ContactService = Depends(get_contact_service),
) -> None:
    try:
        await service.delete_contact(
            contact_id=contact_id,
            organization_id=org_context.organization.id,
            requesting_user_id=current_user.id,
            role=org_context.role,
        )
    except Exception as exc:
        raise HTTPException(status_code=getattr(exc, "status_code", 400), detail=str(exc)) from exc


