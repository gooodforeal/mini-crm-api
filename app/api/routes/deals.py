from __future__ import annotations

from decimal import Decimal

from fastapi import APIRouter, Depends, HTTPException, Query, status

from app.api.dependencies.auth import get_current_user, get_organization_context
from app.dependencies.services import get_deal_service
from app.models.deal import DealStage, DealStatus
from app.models.organization_member import OrganizationRole
from app.models.user import User
from app.schemas.deal import DealCreate, DealOut, DealUpdate
from app.services.deals import DealService
from app.services.organizations import OrganizationContext

router = APIRouter()


@router.get("", response_model=list[DealOut])
async def list_deals(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, le=100),
    status: list[DealStatus] | None = Query(None),
    min_amount: Decimal | None = None,
    max_amount: Decimal | None = None,
    stage: DealStage | None = None,
    owner_id: int | None = None,
    order_by: str = "created_at",
    order: str = Query("desc", pattern="^(asc|desc)$"),
    current_user: User = Depends(get_current_user),
    org_context: OrganizationContext = Depends(get_organization_context),
    service: DealService = Depends(get_deal_service),
) -> list[DealOut]:
    if org_context.role == OrganizationRole.member:
        owner_id = current_user.id
    try:
        return await service.list_deals(
            organization_id=org_context.organization.id,
            status=status,
            min_amount=min_amount,
            max_amount=max_amount,
            stage=stage,
            owner_id=owner_id,
            order_by=order_by,
            order=order,
            limit=page_size,
            offset=(page - 1) * page_size,
        )
    except Exception as exc:
        raise HTTPException(status_code=getattr(exc, "status_code", 400), detail=str(exc)) from exc


@router.post("", response_model=DealOut, status_code=status.HTTP_201_CREATED)
async def create_deal(
    payload: DealCreate,
    current_user: User = Depends(get_current_user),
    org_context: OrganizationContext = Depends(get_organization_context),
    service: DealService = Depends(get_deal_service),
) -> DealOut:
    owner_id = payload.owner_id or current_user.id
    if org_context.role == OrganizationRole.member:
        owner_id = current_user.id
    try:
        return await service.create_deal(
            organization_id=org_context.organization.id,
            contact_id=payload.contact_id,
            owner_id=owner_id,
            actor_id=current_user.id,
            role=org_context.role,
            title=payload.title,
            amount=payload.amount,
            currency=payload.currency,
        )
    except Exception as exc:
        raise HTTPException(status_code=getattr(exc, "status_code", 400), detail=str(exc)) from exc


@router.patch("/{deal_id}", response_model=DealOut)
async def update_deal(
    deal_id: int,
    payload: DealUpdate,
    current_user: User = Depends(get_current_user),
    org_context: OrganizationContext = Depends(get_organization_context),
    service: DealService = Depends(get_deal_service),
) -> DealOut:
    try:
        return await service.update_deal(
            deal_id=deal_id,
            organization_id=org_context.organization.id,
            actor_id=current_user.id,
            role=org_context.role,
            data={k: v for k, v in payload.model_dump(exclude_unset=True).items()},
        )
    except Exception as exc:
        raise HTTPException(status_code=getattr(exc, "status_code", 400), detail=str(exc)) from exc


