from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, status

from app.api.dependencies.auth import get_current_user, get_organization_context
from app.dependencies.services import get_activity_service
from app.models.activity import ActivityType
from app.models.user import User
from app.schemas.activity import ActivityCreate, ActivityOut
from app.services.activities import ActivityService
from app.services.organizations import OrganizationContext

router = APIRouter()


@router.get("", response_model=list[ActivityOut])
async def list_activities(
    deal_id: int,
    org_context: OrganizationContext = Depends(get_organization_context),
    service: ActivityService = Depends(get_activity_service),
) -> list[ActivityOut]:
    try:
        return await service.list_for_deal(deal_id=deal_id, organization_id=org_context.organization.id)
    except Exception as exc:
        raise HTTPException(status_code=getattr(exc, "status_code", 400), detail=str(exc)) from exc


@router.post("", response_model=ActivityOut, status_code=status.HTTP_201_CREATED)
async def add_activity(
    deal_id: int,
    payload: ActivityCreate,
    current_user: User = Depends(get_current_user),
    org_context: OrganizationContext = Depends(get_organization_context),
    service: ActivityService = Depends(get_activity_service),
) -> ActivityOut:
    if payload.type != ActivityType.comment:
        raise HTTPException(status_code=400, detail="Можно создавать только комментарии")
    try:
        return await service.add_comment(
            deal_id=deal_id,
            organization_id=org_context.organization.id,
            author_id=current_user.id,
            payload=payload.payload,
        )
    except Exception as exc:
        raise HTTPException(status_code=getattr(exc, "status_code", 400), detail=str(exc)) from exc


