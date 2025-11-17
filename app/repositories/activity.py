from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.activity import Activity
from app.repositories.base import BaseRepository


class ActivityRepository(BaseRepository[Activity]):
    def __init__(self, session: AsyncSession):
        super().__init__(session, Activity)

    async def list_for_deal(self, deal_id: int) -> list[Activity]:
        stmt = select(Activity).where(Activity.deal_id == deal_id).order_by(Activity.created_at.desc())
        result = await self.session.execute(stmt)
        return list(result.scalars().all())


