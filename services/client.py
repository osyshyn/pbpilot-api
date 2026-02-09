import logging

from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from core import BaseService
from core.pagination import PaginationParams
from dao import ClientDAO
from exceptions import (
    ClientEmailAlreadyRegisteredException,
    ClientNotFoundException,
)
from models import Client
from schemas import CreateClientRequestSchema, UpdateClientRequestSchema

logger = logging.getLogger(__name__)


class ClientService(BaseService):
    def __init__(
        self,
        db_session: AsyncSession,
        *,
        client_dao: ClientDAO | None = None,
    ):
        super().__init__(db_session)
        self._client_dao = client_dao or ClientDAO(db_session)

    async def create_client(
        self, client_data: CreateClientRequestSchema
    ) -> Client:
        try:
            client = await self._client_dao.create(
                name=client_data.name,
                surname=client_data.surname,
                email=client_data.email,
                phone_number=client_data.phone_number,
                business_address=client_data.business_address,
            )
        except IntegrityError:
            raise ClientEmailAlreadyRegisteredException from None
        await self._session.commit()
        return client

    async def get_by_id(self, client_id: int) -> Client:
        client = await self._client_dao.get_by_id(client_id)
        if not client:
            raise ClientNotFoundException
        return client

    async def get_by_email(self, client_email: str) -> Client:
        client = await self._client_dao.get_by_email(client_email)
        if not client:
            raise ClientNotFoundException
        return client

    async def update_client(
        self, client_id: int, client_update_data: UpdateClientRequestSchema
    ) -> Client:
        try:
            client = await self._client_dao.update_by_id(
                client_id=client_id,
                update_data=client_update_data.model_dump(exclude_unset=True),
            )
        except IntegrityError:
            raise ClientEmailAlreadyRegisteredException from None
        if not client:
            raise ClientNotFoundException
        await self._session.commit()
        return client

    async def delete_by_id(self, client_id: int) -> Client:
        client = await self._client_dao.delete_by_id(client_id=client_id)
        if not client:
            raise ClientNotFoundException
        await self._session.commit()
        return client

    async def get_all_clients(
        self,
        pagination: PaginationParams,
    ) -> tuple[list[Client], int]:
        return await self._client_dao.get_all(
            page=pagination.page, limit=pagination.size
        )

