from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException

from app.api.dependencies.auth import get_organization_context
from app.dependencies.services import get_analytics_service
from app.schemas.analytics import DealsFunnelOut, DealsSummaryOut
from app.services.analytics import AnalyticsService
from app.services.organizations import OrganizationContext

router = APIRouter()


@router.get("/deals/summary", response_model=DealsSummaryOut)
async def deals_summary(
    org_context: OrganizationContext = Depends(get_organization_context),
    service: AnalyticsService = Depends(get_analytics_service),
) -> DealsSummaryOut:
    try:
        summary = await service.deals_summary(org_context.organization.id)
        return DealsSummaryOut(**summary.__dict__)
    except Exception as exc:
        raise HTTPException(status_code=getattr(exc, "status_code", 400), detail=str(exc)) from exc


@router.get("/deals/funnel", response_model=DealsFunnelOut)
async def deals_funnel(
    org_context: OrganizationContext = Depends(get_organization_context),
    service: AnalyticsService = Depends(get_analytics_service),
) -> DealsFunnelOut:
    try:
        funnel = await service.deals_funnel(org_context.organization.id)
        return DealsFunnelOut(funnel=funnel)
    except Exception as exc:
        raise HTTPException(status_code=getattr(exc, "status_code", 400), detail=str(exc)) from exc


