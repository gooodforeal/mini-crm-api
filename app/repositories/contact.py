from __future__ import annotations

from sqlalchemy import Select, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.contact import Contact
from app.repositories.base import BaseRepository


class ContactRepository(BaseRepository[Contact]):
    def __init__(self, session: AsyncSession):
        super().__init__(session, Contact)

    def base_query(self) -> Select[tuple[Contact]]:
        return select(Contact)

    async def list_for_org(
        self,
        organization_id: int,
        *,
        owner_id: int | None = None,
        search: str | None = None,
        limit: int = 20,
        offset: int = 0,
    ) -> list[Contact]:
        stmt = self.base_query().where(Contact.organization_id == organization_id)
        if owner_id is not None:
            stmt = stmt.where(Contact.owner_id == owner_id)
        if search:
            stmt = stmt.where(
                (Contact.name.ilike(f"%{search}%"))
                | (Contact.email.ilike(f"%{search}%"))
                | (Contact.phone.ilike(f"%{search}%"))
            )
        stmt = stmt.limit(limit).offset(offset)
        result = await self.session.execute(stmt)
        return list(result.scalars().all())


