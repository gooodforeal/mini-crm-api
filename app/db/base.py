from __future__ import annotations

from typing import Any

from sqlalchemy.orm import DeclarativeBase, declared_attr, Mapped, mapped_column


class Base(DeclarativeBase):
    @declared_attr.directive
    def __tablename__(cls) -> str:  # type: ignore[misc]
        return cls.__name__.lower()

    id: Mapped[int] = mapped_column(primary_key=True, index=True)


class OrganizationScopedBase(Base):
    __abstract__ = True

    organization_id: Mapped[int] = mapped_column(index=True)


def as_dict(instance: Base) -> dict[str, Any]:
    return {c.key: getattr(instance, c.key) for c in instance.__table__.columns}


