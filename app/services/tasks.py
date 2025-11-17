from __future__ import annotations

from datetime import date

from sqlalchemy.ext.asyncio import AsyncSession

from app.models.deal import Deal
from app.models.organization_member import OrganizationRole
from app.models.task import Task
from app.repositories.deal import DealRepository
from app.repositories.task import TaskRepository
from app.services import exceptions


class TaskService:
    def __init__(
        self,
        session: AsyncSession,
        task_repo: TaskRepository | None = None,
        deal_repo: DealRepository | None = None,
    ) -> None:
        self.session = session
        self.repo = task_repo or TaskRepository(session)
        self.deal_repo = deal_repo or DealRepository(session)

    async def _ensure_deal(self, deal_id: int, organization_id: int) -> Deal:
        deal = await self.deal_repo.get(deal_id)
        if deal is None or deal.organization_id != organization_id:
            raise exceptions.NotFoundError("Сделка не найдена")
        return deal

    def _assert_due_date(self, due_date: date) -> None:
        if due_date < date.today():
            raise exceptions.ServiceError("due_date не может быть в прошлом")

    async def create_task(
        self,
        *,
        deal_id: int,
        organization_id: int,
        actor_id: int,
        role: OrganizationRole,
        title: str,
        description: str | None,
        due_date: date,
    ) -> Task:
        self._assert_due_date(due_date)
        deal = await self._ensure_deal(deal_id, organization_id)
        if role == OrganizationRole.member and deal.owner_id != actor_id:
            raise exceptions.PermissionDeniedError("Нельзя создать задачу для чужой сделки")

        task = await self.repo.create(
            {
                "deal_id": deal_id,
                "owner_id": actor_id,
                "title": title,
                "description": description,
                "due_date": due_date,
            }
        )
        await self.session.commit()
        return task

    async def list_tasks(self, *, organization_id: int, **filters) -> list[Task]:
        return await self.repo.list_filtered(organization_id=organization_id, **filters)


