from __future__ import annotations

from datetime import date

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.task import Task
from app.repositories.base import BaseRepository


class TaskRepository(BaseRepository[Task]):
    def __init__(self, session: AsyncSession):
        super().__init__(session, Task)

    async def list_filtered(
        self,
        *,
        organization_id: int,
        deal_id: int | None = None,
        only_open: bool = False,
        due_before: date | None = None,
        due_after: date | None = None,
    ) -> list[Task]:
        from app.models.deal import Deal  # local import to avoid circular

        stmt = select(Task).join(Deal).where(Deal.organization_id == organization_id)
        if deal_id is not None:
            stmt = stmt.where(Task.deal_id == deal_id)
        if only_open:
            stmt = stmt.where(Task.is_done.is_(False))
        if due_before is not None:
            stmt = stmt.where(Task.due_date <= due_before)
        if due_after is not None:
            stmt = stmt.where(Task.due_date >= due_after)

        result = await self.session.execute(stmt.order_by(Task.due_date))
        return list(result.scalars().all())


