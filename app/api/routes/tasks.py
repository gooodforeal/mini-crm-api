from __future__ import annotations

from datetime import date

from fastapi import APIRouter, Depends, HTTPException, Query, status

from app.api.dependencies.auth import get_current_user, get_organization_context
from app.dependencies.services import get_task_service
from app.models.user import User
from app.schemas.task import TaskCreate, TaskOut
from app.services.organizations import OrganizationContext
from app.services.tasks import TaskService

router = APIRouter()


@router.get("", response_model=list[TaskOut])
async def list_tasks(
    deal_id: int | None = None,
    only_open: bool = False,
    due_before: date | None = None,
    due_after: date | None = None,
    org_context: OrganizationContext = Depends(get_organization_context),
    service: TaskService = Depends(get_task_service),
) -> list[TaskOut]:
    try:
        return await service.list_tasks(
            organization_id=org_context.organization.id,
            deal_id=deal_id,
            only_open=only_open,
            due_before=due_before,
            due_after=due_after,
        )
    except Exception as exc:
        raise HTTPException(status_code=getattr(exc, "status_code", 400), detail=str(exc)) from exc


@router.post("", response_model=TaskOut, status_code=status.HTTP_201_CREATED)
async def create_task(
    payload: TaskCreate,
    current_user: User = Depends(get_current_user),
    org_context: OrganizationContext = Depends(get_organization_context),
    service: TaskService = Depends(get_task_service),
) -> TaskOut:
    try:
        return await service.create_task(
            deal_id=payload.deal_id,
            organization_id=org_context.organization.id,
            actor_id=current_user.id,
            role=org_context.role,
            title=payload.title,
            description=payload.description,
            due_date=payload.due_date,
        )
    except Exception as exc:
        raise HTTPException(status_code=getattr(exc, "status_code", 400), detail=str(exc)) from exc


