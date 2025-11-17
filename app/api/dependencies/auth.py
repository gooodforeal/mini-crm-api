from __future__ import annotations

from fastapi import Depends, Header, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from app.core.security import TokenError, get_subject
from app.dependencies.repositories import get_user_repository
from app.dependencies.services import get_organization_service
from app.models.user import User
from app.repositories.user import UserRepository
from app.services.organizations import OrganizationContext, OrganizationService

bearer_scheme = HTTPBearer()


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme),
    user_repo: UserRepository = Depends(get_user_repository),
) -> User:
    if credentials is None or credentials.scheme.lower() != "bearer":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Требуется Bearer токен",
        )
    try:
        user_id = int(get_subject(credentials.credentials))
    except TokenError as exc:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(exc)) from exc

    user = await user_repo.get(user_id)
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Пользователь не найден")
    return user


async def get_organization_context(
    current_user: User = Depends(get_current_user),
    organization_id: int | None = Header(None, alias="X-Organization-Id"),
    service: OrganizationService = Depends(get_organization_service),
) -> OrganizationContext:
    if organization_id is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Необходимо указать заголовок X-Organization-Id",
        )
    try:
        return await service.ensure_membership(organization_id=organization_id, user_id=current_user.id)
    except Exception as exc:
        if hasattr(exc, "status_code"):
            raise HTTPException(status_code=exc.status_code, detail=str(exc)) from exc
        raise


