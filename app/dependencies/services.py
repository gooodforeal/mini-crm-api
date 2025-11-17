from __future__ import annotations

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.dependencies.repositories import (
    get_activity_repository,
    get_contact_repository,
    get_deal_repository,
    get_organization_member_repository,
    get_organization_repository,
    get_task_repository,
    get_user_repository,
)
from app.repositories.activity import ActivityRepository
from app.repositories.contact import ContactRepository
from app.repositories.deal import DealRepository
from app.repositories.organization import OrganizationRepository
from app.repositories.organization_member import OrganizationMemberRepository
from app.repositories.task import TaskRepository
from app.repositories.user import UserRepository
from app.services.activities import ActivityService
from app.services.analytics import AnalyticsService
from app.services.auth import AuthService
from app.services.contacts import ContactService
from app.services.deals import DealService
from app.services.organizations import OrganizationService
from app.services.tasks import TaskService


def get_auth_service(
    session: AsyncSession = Depends(get_db),
    user_repo: UserRepository = Depends(get_user_repository),
    org_repo: OrganizationRepository = Depends(get_organization_repository),
    member_repo: OrganizationMemberRepository = Depends(get_organization_member_repository),
) -> AuthService:
    return AuthService(
        session=session,
        user_repo=user_repo,
        org_repo=org_repo,
        member_repo=member_repo,
    )


def get_organization_service(
    session: AsyncSession = Depends(get_db),
    org_repo: OrganizationRepository = Depends(get_organization_repository),
    member_repo: OrganizationMemberRepository = Depends(get_organization_member_repository),
) -> OrganizationService:
    return OrganizationService(session=session, org_repo=org_repo, member_repo=member_repo)


def get_contact_service(
    session: AsyncSession = Depends(get_db),
    contact_repo: ContactRepository = Depends(get_contact_repository),
    deal_repo: DealRepository = Depends(get_deal_repository),
) -> ContactService:
    return ContactService(session=session, contact_repo=contact_repo, deal_repo=deal_repo)


def get_deal_service(
    session: AsyncSession = Depends(get_db),
    deal_repo: DealRepository = Depends(get_deal_repository),
    contact_repo: ContactRepository = Depends(get_contact_repository),
    activity_repo: ActivityRepository = Depends(get_activity_repository),
) -> DealService:
    return DealService(
        session=session,
        deal_repo=deal_repo,
        contact_repo=contact_repo,
        activity_repo=activity_repo,
    )


def get_task_service(
    session: AsyncSession = Depends(get_db),
    task_repo: TaskRepository = Depends(get_task_repository),
    deal_repo: DealRepository = Depends(get_deal_repository),
) -> TaskService:
    return TaskService(session=session, task_repo=task_repo, deal_repo=deal_repo)


def get_activity_service(
    session: AsyncSession = Depends(get_db),
    activity_repo: ActivityRepository = Depends(get_activity_repository),
    deal_repo: DealRepository = Depends(get_deal_repository),
) -> ActivityService:
    return ActivityService(session=session, activity_repo=activity_repo, deal_repo=deal_repo)


def get_analytics_service(
    session: AsyncSession = Depends(get_db),
    deal_repo: DealRepository = Depends(get_deal_repository),
) -> AnalyticsService:
    return AnalyticsService(session=session, deal_repo=deal_repo)


