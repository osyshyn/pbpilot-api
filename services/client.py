import logging

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError

from exceptions import ClientEmailAlreadyRegisteredException
from schemas import CreateClientRequestSchema
from core import BaseService
from dao import ClientDAO
from models import PricingPlan, Client

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


    async def create_client(self, client_data:CreateClientRequestSchema) -> Client:
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


