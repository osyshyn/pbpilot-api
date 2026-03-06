import logging

from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from core import BaseService, SchemaMapper
from core.constants import INSPECTOR_FIELD_LICENSE_IMAGE_KEYS
from core.pagination import PaginationParams
from dao import EquipmentDAO, InspectorDAO, JobDAO
from dto import CreateInspectorDTO, InspectorDashboardDTO, UploadFileDTO
from exceptions import (
    EmailAlreadyRegisteredException,
    LicenseFileIndexOutOfRangeException,
)
from exceptions.user import UserNotFoundByIdException
from models import Inspector
from models.jobs import JobStatusEnum
from schemas import (
    CreateInspectorRequestSchema,
    InspectorDetailsInspectorSchema,
    InspectorDetailsResponseSchema,
    InspectorEquipmentItemSchema,
    InspectorLicenseSchema,
    UpdateInspectorLicenseRequestSchema,
    UpdateInspectorRequestSchema,
)
from services.aws import FileUploadService, S3Actions

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
        self._job_dao = JobDAO(db_session)
        self._equipment_dao = EquipmentDAO(db_session)

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

    async def update_inspector_license(
        self,
        inspector_id: int,
        license_data: UpdateInspectorLicenseRequestSchema,
    ) -> Inspector:
        update_data = license_data.model_dump(exclude_unset=True)
        if not update_data:
            from exceptions import NoUpdateDataException

            raise NoUpdateDataException
        inspector = await self._inspector_dao.update_by_id(
            inspector_id=inspector_id,
            update_data=update_data,
        )
        if not inspector:
            raise UserNotFoundByIdException
        await self._session.commit()
        return inspector

    async def get_inspector_details(
        self,
        inspector_id: int,
    ) -> InspectorDetailsResponseSchema:
        inspector = await self.get_inspector_by_id(inspector_id)

        jobs = await self._job_dao.get_all_by_inspector_id(inspector_id)
        total_jobs = len(jobs)
        active_jobs = sum(
            1 for job in jobs if job.status != JobStatusEnum.COMPLETED
        )

        equipments = await self._equipment_dao.get_all_by_inspector_id(
            inspector_id
        )

        s3 = S3Actions()
        license_keys = inspector.license_image_keys or []
        files = [
            s3.get_presigned_url(key=key, require_object=False)
            for key in license_keys
        ]

        inspector_block = InspectorDetailsInspectorSchema(
            full_name=inspector.full_name,
            email=inspector.email,
            phone_number=inspector.phone_number,
            total_jobs=total_jobs,
            active_jobs=active_jobs,
        )

        license_block = InspectorLicenseSchema(
            license_number=inspector.license_number,
            license_type=inspector.licence_type,
            issue_date=inspector.issue_date,
            expiration_date=inspector.expiration_date,
        )

        equipments_block = [
            InspectorEquipmentItemSchema(
                name=e.name,
                manufacturer=e.manufacturer,
                model=e.model,
                serial_number=e.serial_number,
                mode_of_operation=e.mode,
                radioactive_source_date=e.date_of_radioactive_source,
            )
            for e in equipments
        ]

        return InspectorDetailsResponseSchema(
            inspector=inspector_block,
            licenses=license_block,
            equipments=equipments_block,
            files=files,
        )
