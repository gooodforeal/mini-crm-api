from __future__ import annotations

from datetime import datetime, timedelta, timezone
from decimal import Decimal
from typing import Sequence

from sqlalchemy import Select, and_, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.deal import Deal, DealStage, DealStatus
from app.repositories.base import BaseRepository


class DealRepository(BaseRepository[Deal]):
    def __init__(self, session: AsyncSession):
        super().__init__(session, Deal)

    def base_query(self) -> Select[tuple[Deal]]:
        return select(Deal)

    async def list_for_org(
        self,
        organization_id: int,
        *,
        status: Sequence[DealStatus] | None = None,
        min_amount: Decimal | None = None,
        max_amount: Decimal | None = None,
        stage: DealStage | None = None,
        owner_id: int | None = None,
        order_by: str = "created_at",
        order: str = "desc",
        limit: int = 20,
        offset: int = 0,
    ) -> list[Deal]:
        stmt = self.base_query().where(Deal.organization_id == organization_id)
        if status:
            stmt = stmt.where(Deal.status.in_(status))
        if min_amount is not None:
            stmt = stmt.where(Deal.amount >= min_amount)
        if max_amount is not None:
            stmt = stmt.where(Deal.amount <= max_amount)
        if stage is not None:
            stmt = stmt.where(Deal.stage == stage)
        if owner_id is not None:
            stmt = stmt.where(Deal.owner_id == owner_id)

        order_column = getattr(Deal, order_by, Deal.created_at)
        if order == "desc":
            order_column = order_column.desc()
        else:
            order_column = order_column.asc()

        stmt = stmt.order_by(order_column).limit(limit).offset(offset)
        result = await self.session.execute(stmt)
        return list(result.scalars().unique().all())

    async def count_by_status(self, organization_id: int) -> dict[DealStatus, int]:
        stmt = (
            select(Deal.status, func.count())
            .where(Deal.organization_id == organization_id)
            .group_by(Deal.status)
        )
        rows = await self.session.execute(stmt)
        return {DealStatus(row[0]): row[1] for row in rows.all()}

    async def amount_stats_by_status(self, organization_id: int) -> dict[DealStatus, dict[str, Decimal]]:
        stmt = (
            select(Deal.status, func.sum(Deal.amount), func.avg(Deal.amount))
            .where(Deal.organization_id == organization_id)
            .group_by(Deal.status)
        )
        rows = await self.session.execute(stmt)
        data: dict[DealStatus, dict[str, Decimal]] = {}
        for status, total, avg in rows.all():
            data[DealStatus(status)] = {"total": total or Decimal("0"), "avg": avg or Decimal("0")}
        return data

    async def count_newer_than(self, organization_id: int, days: int) -> int:
        cutoff = datetime.now(timezone.utc) - timedelta(days=days)
        stmt = select(func.count()).where(Deal.organization_id == organization_id, Deal.created_at >= cutoff)
        result = await self.session.execute(stmt)
        return int(result.scalar_one())

    async def funnel(self, organization_id: int) -> list[tuple[DealStage, DealStatus, int]]:
        stmt = (
            select(Deal.stage, Deal.status, func.count())
            .where(Deal.organization_id == organization_id)
            .group_by(Deal.stage, Deal.status)
        )
        result = await self.session.execute(stmt)
        return list(result.all())

    async def has_contact_deals(self, contact_id: int) -> bool:
        stmt = select(func.count()).where(Deal.contact_id == contact_id)
        result = await self.session.execute(stmt)
        return result.scalar_one() > 0

    async def has_cross_org(self, deal_id: int, organization_id: int) -> bool:
        stmt = select(func.count()).where(
            and_(Deal.id == deal_id, Deal.organization_id != organization_id)
        )
        result = await self.session.execute(stmt)
        return result.scalar_one() > 0


