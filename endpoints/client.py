import logging
from typing import Annotated

from fastapi import APIRouter, Depends

from core import get_service, service
from dependencies import get_admin_user_from_token
from schemas import ClientResponseSchema, CreateClientRequestSchema
from services.client import ClientService

logger = logging.getLogger(__name__)

client_router = APIRouter()


@client_router.post(
    path='/',
    summary='Create new client',
    dependencies=[Depends(get_admin_user_from_token)],
)
async def create_client(
        client_data: CreateClientRequestSchema,
        service: Annotated[
            ClientService, Depends(get_service(ClientService))],
) -> ClientResponseSchema:
    return ClientResponseSchema.model_validate(
        await service.create_client(client_data=client_data)
    )

@client_router.patch(
    path='/{client_id}',
    summary='Update client',
    dependencies=[Depends(get_admin_user_from_token)],
)
async def update_client(
        client_id: int,
) -> ClientResponseSchema:
    return ClientResponseSchema.model_validate(
        await service.update_client(client_id=client_id)
    )