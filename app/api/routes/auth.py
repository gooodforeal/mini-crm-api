from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, status

from app.dependencies.services import get_auth_service
from app.schemas.auth import LoginRequest, RegisterRequest, TokenPair
from app.services.auth import AuthService

router = APIRouter()


@router.post("/register", response_model=TokenPair, status_code=status.HTTP_201_CREATED)
async def register(
    payload: RegisterRequest,
    service: AuthService = Depends(get_auth_service),
) -> TokenPair:
    try:
        tokens = await service.register(**payload.model_dump())
    except Exception as exc:
        status_code = getattr(exc, "status_code", status.HTTP_400_BAD_REQUEST)
        raise HTTPException(status_code=status_code, detail=str(exc)) from exc

    return TokenPair(access_token=tokens.access_token, refresh_token=tokens.refresh_token)


@router.post("/login", response_model=TokenPair)
async def login(
    payload: LoginRequest,
    service: AuthService = Depends(get_auth_service),
) -> TokenPair:
    try:
        tokens = await service.login(**payload.model_dump())
    except Exception as exc:
        status_code = getattr(exc, "status_code", status.HTTP_400_BAD_REQUEST)
        raise HTTPException(status_code=status_code, detail=str(exc)) from exc

    return TokenPair(access_token=tokens.access_token, refresh_token=tokens.refresh_token)


