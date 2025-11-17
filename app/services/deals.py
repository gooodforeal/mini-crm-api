from __future__ import annotations

from decimal import Decimal

from sqlalchemy.ext.asyncio import AsyncSession

from app.models.activity import ActivityType
from app.models.contact import Contact
from app.models.deal import Deal, DealStage, DealStatus
from app.models.organization_member import OrganizationRole
from app.repositories.activity import ActivityRepository
from app.repositories.contact import ContactRepository
from app.repositories.deal import DealRepository
from app.services import exceptions


class DealService:
    stage_order = [
        DealStage.qualification,
        DealStage.proposal,
        DealStage.negotiation,
        DealStage.closed,
    ]

    def __init__(
        self,
        session: AsyncSession,
        deal_repo: DealRepository | None = None,
        contact_repo: ContactRepository | None = None,
        activity_repo: ActivityRepository | None = None,
    ) -> None:
        self.session = session
        self.repo = deal_repo or DealRepository(session)
        self.contact_repo = contact_repo or ContactRepository(session)
        self.activity_repo = activity_repo or ActivityRepository(session)

    async def list_deals(
        self,
        *,
        organization_id: int,
        status: list[DealStatus] | None,
        min_amount: Decimal | None,
        max_amount: Decimal | None,
        stage: DealStage | None,
        owner_id: int | None,
        order_by: str,
        order: str,
        limit: int,
        offset: int,
    ) -> list[Deal]:
        return await self.repo.list_for_org(
            organization_id=organization_id,
            status=status,
            min_amount=min_amount,
            max_amount=max_amount,
            stage=stage,
            owner_id=owner_id,
            order_by=order_by,
            order=order,
            limit=limit,
            offset=offset,
        )

    async def _ensure_contact(self, contact_id: int, organization_id: int) -> Contact:
        contact = await self.contact_repo.get(contact_id)
        if contact is None or contact.organization_id != organization_id:
            raise exceptions.NotFoundError("Контакт не найден в организации")
        return contact

    def _ensure_can_assign_owner(self, *, role: OrganizationRole, owner_id: int, actor_id: int) -> None:
        if role == OrganizationRole.member and owner_id != actor_id:
            raise exceptions.PermissionDeniedError("Участник member может работать только со своими сделками")

    async def create_deal(
        self,
        *,
        organization_id: int,
        contact_id: int,
        owner_id: int,
        actor_id: int,
        role: OrganizationRole,
        title: str,
        amount: Decimal,
        currency: str,
    ) -> Deal:
        await self._ensure_contact(contact_id, organization_id)
        self._ensure_can_assign_owner(role=role, owner_id=owner_id, actor_id=actor_id)
        deal = await self.repo.create(
            {
                "organization_id": organization_id,
                "contact_id": contact_id,
                "owner_id": owner_id,
                "title": title,
                "amount": amount,
                "currency": currency,
            }
        )
        await self.session.commit()
        return deal

    def _check_status_rules(self, *, status: DealStatus | None, amount: Decimal | None) -> None:
        if status == DealStatus.won and (amount is None or amount <= 0):
            raise exceptions.ServiceError("Нельзя закрыть сделку со статусом won и amount <= 0")

    def _stage_index(self, stage: DealStage) -> int:
        return self.stage_order.index(stage)

    def _check_stage_transition(
        self,
        *,
        current: DealStage,
        new_stage: DealStage,
        role: OrganizationRole,
    ) -> None:
        if self._stage_index(new_stage) >= self._stage_index(current):
            return
        if role not in (OrganizationRole.owner, OrganizationRole.admin):
            raise exceptions.ServiceError("Откат стадии запрещен для вашей роли", status_code=403)

    async def update_deal(
        self,
        *,
        deal_id: int,
        organization_id: int,
        actor_id: int,
        role: OrganizationRole,
        data: dict[str, object],
    ) -> Deal:
        deal = await self.repo.get(deal_id)
        if deal is None or deal.organization_id != organization_id:
            raise exceptions.NotFoundError("Сделка не найдена")
        if role == OrganizationRole.member and deal.owner_id != actor_id:
            raise exceptions.PermissionDeniedError("Нельзя изменять чужие сделки")

        new_status = data.get("status")
        new_stage = data.get("stage")
        new_amount = data.get("amount")

        self._check_status_rules(status=new_status or deal.status, amount=new_amount or deal.amount)
        if new_stage:
            self._check_stage_transition(current=deal.stage, new_stage=new_stage, role=role)

        updated = await self.repo.update(deal_id, data)
        if updated is None:
            raise exceptions.NotFoundError("Сделка не найдена")

        if new_status and new_status != deal.status:
            await self.activity_repo.create(
                {
                    "deal_id": deal_id,
                    "author_id": actor_id,
                    "type": ActivityType.status_changed,
                    "payload": {
                        "old_status": deal.status,
                        "new_status": new_status,
                    },
                }
            )
        if new_stage and new_stage != deal.stage:
            await self.activity_repo.create(
                {
                    "deal_id": deal_id,
                    "author_id": actor_id,
                    "type": ActivityType.stage_changed,
                    "payload": {
                        "old_stage": deal.stage,
                        "new_stage": new_stage,
                    },
                }
            )

        await self.session.commit()
        return updated


