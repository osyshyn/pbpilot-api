from datetime import UTC, datetime

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

