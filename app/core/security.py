from __future__ import annotations

from datetime import datetime, timedelta, timezone
from typing import Any, Dict, Optional

from jose import JWTError, jwt
from passlib.context import CryptContext

from app.core.config import settings

try:  # pragma: no cover - защитный код от предупреждений passlib
    import bcrypt  # type: ignore
    from types import SimpleNamespace

    if not hasattr(bcrypt, "__about__") and hasattr(bcrypt, "__version__"):
        bcrypt.__about__ = SimpleNamespace(__version__=bcrypt.__version__)
except Exception:  # noqa: BLE001
    pass

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


def create_token(subject: str, expires_delta: timedelta, token_type: str) -> str:
    now = datetime.now(tz=timezone.utc)
    payload: Dict[str, Any] = {
        "sub": subject,
        "type": token_type,
        "iat": now,
        "exp": now + expires_delta,
    }
    return jwt.encode(payload, settings.secret_key, algorithm=settings.algorithm)


def create_access_token(subject: str) -> str:
    return create_token(
        subject,
        expires_delta=timedelta(minutes=settings.access_token_expire_minutes),
        token_type="access",
    )


def create_refresh_token(subject: str) -> str:
    return create_token(
        subject,
        expires_delta=timedelta(minutes=settings.refresh_token_expire_minutes),
        token_type="refresh",
    )


class TokenError(Exception):
    pass


def decode_token(token: str, expected_type: str = "access") -> Dict[str, Any]:
    try:
        payload = jwt.decode(token, settings.secret_key, algorithms=[settings.algorithm])
    except JWTError as exc:
        raise TokenError("Невалидный токен") from exc

    token_type = payload.get("type")
    if token_type != expected_type:
        raise TokenError("Неверный тип токена")
    return payload


def get_subject(token: str, expected_type: str = "access") -> str:
    payload = decode_token(token, expected_type=expected_type)
    subject: Optional[str] = payload.get("sub")
    if not subject:
        raise TokenError("Токен без пользователя")
    return subject


