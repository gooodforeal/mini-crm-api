from __future__ import annotations

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import get_password_hash
from app.models.organization import Organization
from app.models.organization_member import OrganizationMember, OrganizationRole
from app.models.user import User


async def init_db(session: AsyncSession) -> None:
    from sqlalchemy import select

    exists = await session.scalar(select(User).limit(1))
    if exists:
        return

    user = User(
        email="owner@example.com",
        hashed_password=get_password_hash("Owner123"),
        name="Default Owner",
    )
    organization = Organization(name="Default Org")
    session.add_all([user, organization])
    await session.flush()
    member = OrganizationMember(
        organization_id=organization.id,
        user_id=user.id,
        role=OrganizationRole.owner,
    )
    session.add(member)
    await session.commit()


