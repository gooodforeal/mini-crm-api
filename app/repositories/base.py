from __future__ import annotations

from typing import Any, Generic, Iterable, Sequence, TypeVar

from sqlalchemy import delete, select, update
from sqlalchemy.ext.asyncio import AsyncSession

ModelType = TypeVar("ModelType")


class BaseRepository(Generic[ModelType]):
    def __init__(self, session: AsyncSession, model: type[ModelType]):
        self.session = session
        self.model = model

    async def get(self, object_id: int) -> ModelType | None:
        return await self.session.get(self.model, object_id)

    async def list(self, *, filters: Iterable[Any] = (), limit: int | None = None) -> Sequence[ModelType]:
        stmt = select(self.model)
        for condition in filters:
            stmt = stmt.where(condition)
        if limit:
            stmt = stmt.limit(limit)
        result = await self.session.execute(stmt)
        return result.scalars().all()

    async def create(self, obj_in: dict[str, Any]) -> ModelType:
        instance = self.model(**obj_in)
        self.session.add(instance)
        await self.session.flush()
        return instance

    async def update(self, object_id: int, obj_in: dict[str, Any]) -> ModelType | None:
        stmt = (
            update(self.model)
            .where(self.model.id == object_id)
            .values(**obj_in)
            .returning(self.model)  # type: ignore[arg-type]
        )
        result = await self.session.execute(stmt)
        instance = result.scalar_one_or_none()
        return instance

    async def delete(self, object_id: int) -> None:
        stmt = delete(self.model).where(self.model.id == object_id)
        await self.session.execute(stmt)


