from __future__ import annotations

from sqlalchemy.ext.asyncio import AsyncSession

from app.models.activity import Activity, ActivityType
from app.repositories.activity import ActivityRepository
from app.repositories.deal import DealRepository
from app.services import exceptions


class ActivityService:
    def __init__(
        self,
        session: AsyncSession,
        activity_repo: ActivityRepository | None = None,
        deal_repo: DealRepository | None = None,
    ) -> None:
        self.session = session
        self.repo = activity_repo or ActivityRepository(session)
        self.deal_repo = deal_repo or DealRepository(session)

    async def list_for_deal(self, *, deal_id: int, organization_id: int) -> list[Activity]:
        deal = await self.deal_repo.get(deal_id)
        if deal is None or deal.organization_id != organization_id:
            raise exceptions.NotFoundError("Сделка не найдена")
        return await self.repo.list_for_deal(deal_id)

    async def add_comment(
        self,
        *,
        deal_id: int,
        organization_id: int,
        author_id: int,
        payload: dict,
    ) -> Activity:
        deal = await self.deal_repo.get(deal_id)
        if deal is None or deal.organization_id != organization_id:
            raise exceptions.NotFoundError("Сделка не найдена")

        activity = await self.repo.create(
            {
                "deal_id": deal_id,
                "author_id": author_id,
                "type": ActivityType.comment,
                "payload": payload,
            }
        )
        await self.session.commit()
        return activity


