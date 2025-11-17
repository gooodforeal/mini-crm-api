from __future__ import annotations

from app.models.deal import DealStage, DealStatus
from app.schemas.common import ORMModel


class DealsSummaryOut(ORMModel):
    count_by_status: dict[str, int]
    amount_by_status: dict[str, float]
    average_won_amount: float
    new_deals_last_n_days: int


class DealsFunnelOut(ORMModel):
    funnel: dict[str, dict[str, int]]


