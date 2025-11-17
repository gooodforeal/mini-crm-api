from __future__ import annotations

from dataclasses import dataclass

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import create_access_token, create_refresh_token, get_password_hash, verify_password
from app.models.organization_member import OrganizationRole
from app.repositories.organization import OrganizationRepository
from app.repositories.organization_member import OrganizationMemberRepository
from app.repositories.user import UserRepository
from app.services import exceptions


@dataclass
class AuthResult:
    access_token: str
    refresh_token: str


class AuthService:
    def __init__(
        self,
        session: AsyncSession,
        user_repo: UserRepository | None = None,
        org_repo: OrganizationRepository | None = None,
        member_repo: OrganizationMemberRepository | None = None,
    ) -> None:
        self.session = session
        self.user_repo = user_repo or UserRepository(session)
        self.org_repo = org_repo or OrganizationRepository(session)
        self.member_repo = member_repo or OrganizationMemberRepository(session)

    async def register(
        self, *, email: str, password: str, name: str, organization_name: str
    ) -> AuthResult:
        if await self.user_repo.get_by_email(email):
            raise exceptions.ConflictError("Пользователь с таким email уже существует")
        if await self.org_repo.get_by_name(organization_name):
            raise exceptions.ConflictError("Организация с таким именем уже существует")

        user = await self.user_repo.create(
            {
                "email": email,
                "hashed_password": get_password_hash(password),
                "name": name,
            }
        )

        organization = await self.org_repo.create({"name": organization_name})
        await self.member_repo.create(
            {
                "organization_id": organization.id,
                "user_id": user.id,
                "role": OrganizationRole.owner,
            }
        )
        await self.session.commit()
        return AuthResult(
            access_token=create_access_token(str(user.id)),
            refresh_token=create_refresh_token(str(user.id)),
        )

    async def login(self, *, email: str, password: str) -> AuthResult:
        user = await self.user_repo.get_by_email(email)
        if user is None or not verify_password(password, user.hashed_password):
            raise exceptions.ServiceError("Неверные учетные данные", status_code=401)

        return AuthResult(
            access_token=create_access_token(str(user.id)),
            refresh_token=create_refresh_token(str(user.id)),
        )


