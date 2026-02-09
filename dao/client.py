from typing import Any

from sqlalchemy import select

from core.dao import BaseDAO
from models import Client


class ClientDAO(BaseDAO):
    """DAO for Client model."""

    async def create(
            self,
            *,
            name: str,
            surname: str,
            email: str,
            business_address: str,
            phone_number: str | None = None,
    ) -> Client:
        """Create a new user.

        Args:
            name: User name.
            surname: User surname.
            email: User email.
            business_address: User business address.
            phone_number: User phone number (optional).

        Returns:
            User: User instance.

        """
        client = Client(
            name=name,
            surname=surname,
            email=email,
            phone_number=phone_number,
            business_address=business_address,
        )
        self._session.add(client)
        await self._session.flush()
        await self._session.refresh(client)
        return client

    async def get_by_email(self, email: str) -> Client | None:
        """Get user by email.

        Args:
            email: Client email address.

        Returns:
            Client | None: User instance or None if not found.

        """
        stmt = select(Client).where(Client.email == email, is_active=True)
        result = await self._session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_by_id(self, client_id: int) -> Client | None:
        """Get user by email.

        Args:
            client_id: Client id.

        Returns:
            Client | None: User instance or None if not found.

        """
        stmt = select(Client).where(Client.id == client_id, is_active=True)
        result = await self._session.execute(stmt)
        return result.scalar_one_or_none()

    async def update_by_id(
            self,
            client_id: int,
            update_data: dict[str, Any],
    ) -> Client | None:
        """Update user by id."""
        client = await self.get_by_id(client_id)
        if not client:
            return None
        for key, value in update_data.items():
            if hasattr(client, key):
                setattr(client, key, value)
        await self._session.flush()
        await self._session.refresh(client)
        return client
