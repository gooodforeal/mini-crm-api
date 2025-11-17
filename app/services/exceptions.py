from __future__ import annotations


class ServiceError(Exception):
    status_code: int = 400

    def __init__(self, message: str, *, status_code: int | None = None) -> None:
        super().__init__(message)
        if status_code:
            self.status_code = status_code
        self.message = message

    def to_dict(self) -> dict[str, str]:
        return {"detail": self.message}


class NotFoundError(ServiceError):
    status_code = 404


class PermissionDeniedError(ServiceError):
    status_code = 403


class ConflictError(ServiceError):
    status_code = 409


