from __future__ import annotations

from sqlalchemy.ext.asyncio import AsyncSession

from app.models.contact import Contact
from app.models.organization_member import OrganizationRole
from app.repositories.contact import ContactRepository
from app.repositories.deal import DealRepository
from app.services import exceptions


class ContactService:
    def __init__(
        self,
        session: AsyncSession,
        contact_repo: ContactRepository | None = None,
        deal_repo: DealRepository | None = None,
    ) -> None:
        self.session = session
        self.repo = contact_repo or ContactRepository(session)
        self.deal_repo = deal_repo or DealRepository(session)

    async def list_contacts(
        self,
        *,
        organization_id: int,
        role: OrganizationRole,
        owner_id: int | None,
        search: str | None,
        page: int,
        page_size: int,
    ) -> list[Contact]:
        offset = (page - 1) * page_size
        return await self.repo.list_for_org(
            organization_id,
            owner_id=owner_id,
            search=search,
            limit=page_size,
            offset=offset,
        )

    async def create_contact(
        self,
        *,
        organization_id: int,
        owner_id: int,
        name: str,
        email: str | None,
        phone: str | None,
    ) -> Contact:
        contact = await self.repo.create(
            {
                "organization_id": organization_id,
                "owner_id": owner_id,
                "name": name,
                "email": email,
                "phone": phone,
            }
        )
        await self.session.commit()
        return contact

    async def delete_contact(
        self,
        *,
        contact_id: int,
        organization_id: int,
        requesting_user_id: int,
        role: OrganizationRole,
    ) -> None:
        contact = await self.repo.get(contact_id)
        if contact is None or contact.organization_id != organization_id:
            raise exceptions.NotFoundError("Контакт не найден")

        if role == OrganizationRole.member and contact.owner_id != requesting_user_id:
            raise exceptions.PermissionDeniedError("Нельзя удалить чужой контакт")

        if await self.deal_repo.has_contact_deals(contact_id):
            raise exceptions.ConflictError("Нельзя удалить контакт с активными сделками")

        await self.repo.delete(contact_id)
        await self.session.commit()


