from __future__ import annotations

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.repositories.activity import ActivityRepository
from app.repositories.contact import ContactRepository
from app.repositories.deal import DealRepository
from app.repositories.organization import OrganizationRepository
from app.repositories.organization_member import OrganizationMemberRepository
from app.repositories.task import TaskRepository
from app.repositories.user import UserRepository


def get_user_repository(session: AsyncSession = Depends(get_db)) -> UserRepository:
    return UserRepository(session)


def get_organization_repository(session: AsyncSession = Depends(get_db)) -> OrganizationRepository:
    return OrganizationRepository(session)


def get_organization_member_repository(
    session: AsyncSession = Depends(get_db),
) -> OrganizationMemberRepository:
    return OrganizationMemberRepository(session)


def get_contact_repository(session: AsyncSession = Depends(get_db)) -> ContactRepository:
    return ContactRepository(session)


def get_deal_repository(session: AsyncSession = Depends(get_db)) -> DealRepository:
    return DealRepository(session)


def get_task_repository(session: AsyncSession = Depends(get_db)) -> TaskRepository:
    return TaskRepository(session)


def get_activity_repository(session: AsyncSession = Depends(get_db)) -> ActivityRepository:
    return ActivityRepository(session)


