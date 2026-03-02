import logging

from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from core import BaseService, SchemaMapper
from core.constants import INSPECTOR_FIELD_LICENSE_IMAGE_KEYS
from core.pagination import PaginationParams
from dao import InspectorDAO
from dto import CreateInspectorDTO, InspectorDashboardDTO, UploadFileDTO
from exceptions import (
    EmailAlreadyRegisteredException,
    LicenseFileIndexOutOfRangeException,
)
from exceptions.user import UserNotFoundByIdException
from models import Inspector
from schemas import (
    CreateInspectorRequestSchema,
    UpdateInspectorRequestSchema,
)
from services.aws import FileUploadService

logger = logging.getLogger(__name__)


class InspectorService(BaseService):
    def __init__(
        self,
        db_session: AsyncSession,
        *,
        inspector_dao: InspectorDAO | None = None,
    ):
        super().__init__(db_session)
        self._inspector_dao = inspector_dao or InspectorDAO(db_session)

    async def create_new_inspector(
        self,
        inspector_schema: CreateInspectorRequestSchema,
        license_files: list[UploadFileDTO],
    ) -> Inspector:
        if not license_files:
            raise ValueError('At least one license file is required')
        license_image_keys = [f.key for f in license_files]
        try:
            inspector_data: CreateInspectorDTO = SchemaMapper.to_dto(
                CreateInspectorDTO,
                inspector_schema,
                license_image_keys=license_image_keys,
            )
            inspector: Inspector = await self._inspector_dao.create(
                inspector_data=inspector_data
            )
        except IntegrityError:
            raise EmailAlreadyRegisteredException from None
        await self._session.commit()
        return inspector

    async def get_inspector_by_id(self, inspector_id: int) -> Inspector:
        inspector: Inspector | None = await self._inspector_dao.get_by_id(
            inspector_id
        )
        if not inspector or not inspector.is_active:
            raise UserNotFoundByIdException
        return inspector

    async def update_inspector(
        self,
        inspector_id: int,
        inspector_update_data: UpdateInspectorRequestSchema,
    ) -> Inspector:
        try:
            inspector = await self._inspector_dao.update_by_id(
                inspector_id=inspector_id,
                update_data=inspector_update_data.model_dump(
                    exclude_unset=True
                ),
            )
        except IntegrityError:
            raise EmailAlreadyRegisteredException from None
        if not inspector:
            raise UserNotFoundByIdException
        await self._session.commit()
        return inspector

    async def get_all_inspectors(
        self, pagination: PaginationParams
    ) -> tuple[list[Inspector], int]:
        return await self._inspector_dao.get_all(
            page=pagination.page, limit=pagination.size
        )

    async def get_inspectors_dashboard(
        self,
        user_id: int,
    ) -> InspectorDashboardDTO:
        return await self._inspector_dao.get_inspectors_dashboard(
            user_id=user_id
        )

    async def delete_license_file(
        self,
        inspector_id: int,
        file_index: int,
        file_upload_service: FileUploadService,
    ) -> Inspector:
        """Remove one license file by index: delete from S3 and update DB."""
        inspector = await self.get_inspector_by_id(inspector_id)
        keys: list[str] = list(inspector.license_image_keys or [])
        if file_index < 0 or file_index >= len(keys):
            raise LicenseFileIndexOutOfRangeException()
        key_to_delete = keys[file_index]
        file_upload_service.delete_file(key_to_delete)
        new_keys = [k for i, k in enumerate(keys) if i != file_index]
        updated = await self._inspector_dao.update_by_id(
            inspector_id,
            update_data={INSPECTOR_FIELD_LICENSE_IMAGE_KEYS: new_keys or None},
        )
        await self._session.commit()
        if updated:
            await self._session.refresh(updated)
            return updated
        return inspector
