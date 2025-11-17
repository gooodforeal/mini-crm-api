from __future__ import annotations

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.contact import Contact
from app.models.deal import Deal, DealStage, DealStatus
from app.models.organization import Organization
from app.models.organization_member import OrganizationMember, OrganizationRole
from app.models.user import User
from app.services.deals import DealService
from app.services.exceptions import ServiceError


@pytest.mark.asyncio
async def test_stage_revert_forbidden_for_manager(session: AsyncSession):
    owner = User(email="owner@example.com", hashed_password="hashed", name="Owner")
    org = Organization(name="Test Org")
    contact = Contact(organization=org, owner=owner, name="Contact", email=None, phone=None)
    session.add_all([owner, org, contact])
    await session.flush()
    member = OrganizationMember(organization_id=org.id, user_id=owner.id, role=OrganizationRole.manager)
    deal = Deal(
        organization_id=org.id,
        contact_id=contact.id,
        owner_id=owner.id,
        title="Deal",
        amount=100,
        currency="USD",
        status=DealStatus.in_progress,
        stage=DealStage.proposal,
    )
    session.add_all([member, deal])
    await session.commit()

    service = DealService(session)

    with pytest.raises(ServiceError):
        await service.update_deal(
            deal_id=deal.id,
            organization_id=org.id,
            actor_id=owner.id,
            role=OrganizationRole.manager,
            data={"stage": DealStage.qualification},
        )


