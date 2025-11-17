from __future__ import annotations

from dataclasses import dataclass
from typing import Sequence

from sqlalchemy.ext.asyncio import AsyncSession

from app.models.organization import Organization
from app.models.organization_member import OrganizationMember, OrganizationRole
from app.repositories.organization import OrganizationRepository
from app.repositories.organization_member import OrganizationMemberRepository
from app.services import exceptions


@dataclass
class OrganizationContext:
    organization: Organization
    membership: OrganizationMember

    @property
    def role(self) -> OrganizationRole:
        return self.membership.role

    def can_manage(self) -> bool:
        return self.role in {OrganizationRole.owner, OrganizationRole.admin, OrganizationRole.manager}

    def can_edit_only_own(self) -> bool:
        return self.role == OrganizationRole.member


class OrganizationService:
    def __init__(
        self,
        session: AsyncSession,
        org_repo: OrganizationRepository | None = None,
        member_repo: OrganizationMemberRepository | None = None,
    ) -> None:
        self.session = session
        self.org_repo = org_repo or OrganizationRepository(session)
        self.member_repo = member_repo or OrganizationMemberRepository(session)

    async def get_user_organizations(self, user_id: int) -> Sequence[Organization]:
        memberships = await self.member_repo.list(filters=[OrganizationMember.user_id == user_id])
        organization_ids = [m.organization_id for m in memberships]
        if not organization_ids:
            return []
        return await self.org_repo.list(filters=[Organization.id.in_(organization_ids)])

    async def ensure_membership(self, *, organization_id: int, user_id: int) -> OrganizationContext:
        organization = await self.org_repo.get(organization_id)
        if organization is None:
            raise exceptions.NotFoundError("Организация не найдена")
        membership = await self.member_repo.get_for_user(organization_id=organization_id, user_id=user_id)
        if membership is None:
            raise exceptions.PermissionDeniedError("Нет доступа к организации")
        return OrganizationContext(organization=organization, membership=membership)


