from __future__ import annotations

from dataclasses import dataclass

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.cache import TTLCache
from app.core.config import settings
from app.models.deal import DealStage, DealStatus
from app.repositories.deal import DealRepository


cache = TTLCache(ttl_seconds=settings.cache_ttl_seconds)


@dataclass
class DealSummary:
    count_by_status: dict[str, int]
    amount_by_status: dict[str, float]
    average_won_amount: float
    new_deals_last_n_days: int


class AnalyticsService:
    def __init__(self, session: AsyncSession, deal_repo: DealRepository | None = None) -> None:
        self.session = session
        self.repo = deal_repo or DealRepository(session)

    async def deals_summary(self, organization_id: int, *, last_days: int = 30) -> DealSummary:
        cache_key = (organization_id, last_days)
        cached = cache.get(cache_key)
        if cached:
            return cached
        count_by_status = await self.repo.count_by_status(organization_id)
        amount_stats = await self.repo.amount_stats_by_status(organization_id)
        amount_by_status = {status.value: float(stats["total"]) for status, stats in amount_stats.items()}
        won_stats = amount_stats.get(DealStatus.won)
        average_won_amount = float(won_stats["avg"]) if won_stats else 0.0
        new_deals = await self.repo.count_newer_than(organization_id, last_days)
        summary = DealSummary(
            count_by_status={status.value: count for status, count in count_by_status.items()},
            amount_by_status=amount_by_status,
            average_won_amount=average_won_amount,
            new_deals_last_n_days=new_deals,
        )
        cache.set(cache_key, summary)
        return summary

    async def deals_funnel(self, organization_id: int) -> dict[str, dict[str, int]]:
        rows = await self.repo.funnel(organization_id)
        funnel: dict[str, dict[str, int]] = {}
        for stage, status, count in rows:
            funnel.setdefault(stage.value if isinstance(stage, DealStage) else stage, {})[
                status.value if isinstance(status, DealStatus) else status
            ] = count
        return funnel


