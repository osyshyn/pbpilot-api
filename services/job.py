import logging
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from core import BaseService
from core.pagination import PaginationParams
from dao import (
    COCFormDAO,
    InspectorDAO,
    JobDAO,
    ObservationDAO,
    PhotoDAO,
    RoomDAO,
    SampleDAO,
    SamplePhotoDAO,
    UnitDAO,
)
from dto import (
    JobDetailsDTO,
    JobInfoDTO,
    JobInspectionProgressDTO,
    JobListItemDTO,
    JobPropertyDetailsDTO,
)
from exceptions import (
    ClientNotFoundException,
    JobNotFoundException,
    JobSyncInspectionTypeMismatchException,
    JobSyncNotAllowedForTypeException,
    ProjectPropertyNotFoundException,
)
from exceptions.user import UserNotFoundByIdException
from models import Job
from models.jobs import InspectionTypeEnum, JobStatusEnum
from models.projects import ProjectProperty
from schemas import (
    AssignInspectorRequestSchema,
    CreateJobRequestSchema,
    JobListFiltersSchema,
    JobSyncRequestSchema,
)
from schemas.job_sync import COCFormSyncSchema

logger = logging.getLogger(__name__)


class JobService(BaseService):
    def __init__(
        self,
        db_session: AsyncSession,
        *,
        job_dao: JobDAO | None = None,
        inspector_dao: InspectorDAO | None = None,
        unit_dao: UnitDAO | None = None,
        room_dao: RoomDAO | None = None,
        observation_dao: ObservationDAO | None = None,
        coc_form_dao: COCFormDAO | None = None,
        sample_dao: SampleDAO | None = None,
        sample_photo_dao: SamplePhotoDAO | None = None,
        photo_dao: PhotoDAO | None = None,
    ):
        super().__init__(db_session)
        self._job_dao = job_dao or JobDAO(db_session)
        self._inspector_dao = inspector_dao or InspectorDAO(db_session)
        self._unit_dao = unit_dao or UnitDAO(db_session)
        self._room_dao = room_dao or RoomDAO(db_session)
        self._observation_dao = observation_dao or ObservationDAO(db_session)
        self._coc_form_dao = coc_form_dao or COCFormDAO(db_session)
        self._sample_dao = sample_dao or SampleDAO(db_session)
        self._sample_photo_dao = sample_photo_dao or SamplePhotoDAO(db_session)
        self._photo_dao = photo_dao or PhotoDAO(db_session)

    async def sync_offline_inspection(
        self,
        job_id: int,
        payload: JobSyncRequestSchema,
    ) -> Job:
        """Sync full offline inspection tree from mobile client."""
        job = await self._job_dao.get_by_id(job_id)
        if not job:
            raise JobNotFoundException

        if job.inspection_type in {
            InspectionTypeEnum.PERSONAL_BUSINESS_METING,
            InspectionTypeEnum.CONSULTATION,
        }:
            raise JobSyncNotAllowedForTypeException(
                inspection_type=job.inspection_type,
            )

        if job.inspection_type is not payload.inspection_type:
            logger.warning(
                'Job %s inspection_type mismatch: db=%s, payload=%s',
                job_id,
                job.inspection_type,
                payload.inspection_type,
            )
            raise JobSyncInspectionTypeMismatchException(
                job_id=job_id,
                db_type=str(job.inspection_type),
                payload_type=str(payload.inspection_type),
            )

        await self._clear_existing_inspection_data(job_id=job_id)

        flat_data = self._flatten_payload_for_bulk_insert(
            job_id=job_id,
            payload=payload,
        )

        if flat_data['units']:
            await self._unit_dao.bulk_create(units_data=flat_data['units'])
        if flat_data['rooms']:
            await self._room_dao.bulk_create(rooms_data=flat_data['rooms'])
        if flat_data['observations']:
            await self._observation_dao.bulk_create(
                observations_data=flat_data['observations'],
            )
        if flat_data['photos']:
            await self._photo_dao.bulk_create(
                photos_data=flat_data['photos'],
            )
        if flat_data['coc_forms']:
            await self._coc_form_dao.bulk_create(
                forms_data=flat_data['coc_forms'],
            )
        if flat_data['samples']:
            await self._sample_dao.bulk_create(
                samples_data=flat_data['samples'],
            )
        if flat_data['sample_photos']:
            await self._sample_photo_dao.bulk_create(
                sample_photos_data=flat_data['sample_photos'],
            )

        job.status = JobStatusEnum.AWAITING_RESULTS
        job.notes = payload.notes
        await self._session.flush()
        await self._session.commit()
        return job

    async def _clear_existing_inspection_data(self, job_id: int) -> None:
        """Remove existing tree data for a job before full replace."""
        await self._unit_dao.delete_by_job_id(job_id)
        await self._observation_dao.delete_exterior_by_job_id(job_id)
        await self._coc_form_dao.delete_by_job_id(job_id)
        await self._session.flush()

    def _flatten_payload_for_bulk_insert(
        self,
        *,
        job_id: int,
        payload: JobSyncRequestSchema,
    ) -> dict[str, list[dict]]:
        data: dict[str, list[dict]] = {
            'units': [],
            'rooms': [],
            'observations': [],
            'photos': [],
            'coc_forms': [],
            'samples': [],
            'sample_photos': [],
        }

        for obs in payload.exterior_observations:
            obs_dict = obs.model_dump(
                exclude={'photos'},
                exclude_none=True,
            )
            obs_dict['job_id'] = job_id
            obs_dict['room_id'] = None
            obs_dict['is_exterior'] = True
            data['observations'].append(obs_dict)

            for photo in obs.photos:
                photo_dict = photo.model_dump(exclude_none=True)
                photo_dict['observation_id'] = obs.id
                data['photos'].append(photo_dict)

        for unit in payload.units:
            unit_dict = unit.model_dump(
                exclude={'rooms', 'coc_forms'},
                exclude_none=True,
            )
            unit_dict['job_id'] = job_id
            data['units'].append(unit_dict)

            for room in unit.rooms:
                room_dict = room.model_dump(
                    exclude={'observations'},
                    exclude_none=True,
                )
                room_dict['unit_id'] = unit.id
                data['rooms'].append(room_dict)

                for obs in room.observations:
                    obs_dict = obs.model_dump(
                        exclude={'photos'},
                        exclude_none=True,
                    )
                    obs_dict['job_id'] = job_id
                    obs_dict['room_id'] = room.id
                    obs_dict['is_exterior'] = False
                    data['observations'].append(obs_dict)

                    for photo in obs.photos:
                        photo_dict = photo.model_dump(exclude_none=True)
                        photo_dict['observation_id'] = obs.id
                        data['photos'].append(photo_dict)

            for form in unit.coc_forms:
                self._flatten_coc_form(
                    form=form,
                    job_id=job_id,
                    unit_id=unit.id,
                    data_dict=data,
                )

        for form in payload.exterior_coc_forms:
            self._flatten_coc_form(
                form=form,
                job_id=job_id,
                unit_id=None,
                data_dict=data,
            )

        return data

    def _flatten_coc_form(
        self,
        *,
        form: COCFormSyncSchema,
        job_id: int,
        unit_id: UUID | None,
        data_dict: dict[str, list[dict]],
    ) -> None:
        form_dict = form.model_dump(
            exclude={'samples'},
            exclude_none=True,
        )
        form_dict['job_id'] = job_id
        form_dict['unit_id'] = unit_id
        data_dict['coc_forms'].append(form_dict)

        for sample in form.samples:
            sample_dict = sample.model_dump(
                exclude={'photos'},
                exclude_none=True,
            )
            sample_dict['coc_form_id'] = form.id
            if sample.photos:
                sample_dict['photo_s3_key'] = sample.photos[0].s3_key
            data_dict['samples'].append(sample_dict)

            for photo in sample.photos:
                photo_dict = photo.model_dump(exclude_none=True)
                photo_dict['sample_id'] = sample.id
                data_dict['sample_photos'].append(photo_dict)

    async def create_job(self, data: CreateJobRequestSchema) -> Job:
        property_stmt = select(ProjectProperty).where(
            ProjectProperty.id == data.property_id,
            ProjectProperty.is_active == True,  # noqa: E712
        )
        result = await self._session.execute(property_stmt)
        project_property = result.scalar_one_or_none()
        if not project_property:
            raise ProjectPropertyNotFoundException

        if data.inspector_id is not None:
            inspector = await self._inspector_dao.get_by_id(data.inspector_id)
            if not inspector or not inspector.is_active:
                raise UserNotFoundByIdException

        job = await self._job_dao.create(
            property_id=data.property_id,
            inspector_id=data.inspector_id,
            inspection_type=data.inspection_type.value,
            notes=data.notes,
        )
        await self._session.commit()
        return job

    async def assign_inspector(
        self,
        job_id: int,
        inspector_data: AssignInspectorRequestSchema,
    ) -> Job:
        job = await self._job_dao.get_by_id(job_id)
        if not job:
            raise JobNotFoundException

        inspector_id = inspector_data.inspector_id

        if inspector_id is not None:
            inspector = await self._inspector_dao.get_by_id(inspector_id)
            if not inspector or not inspector.is_active:
                raise UserNotFoundByIdException

        job = await self._job_dao.update_by_id(
            job_id=job_id,
            update_data={'inspector_id': inspector_id},
        )
        if not job:
            raise JobNotFoundException

        await self._session.commit()
        return job

    async def get_job_by_id(self, job_id: int) -> Job:
        job = await self._job_dao.get_by_id(job_id)
        if not job:
            raise JobNotFoundException
        return job

    async def delete_job_by_id(self, job_id: int) -> Job:
        job = await self._job_dao.delete_by_id(job_id)
        if not job:
            raise JobNotFoundException
        await self._session.commit()
        return job

    async def get_all_jobs(
        self,
        pagination: PaginationParams,
    ) -> tuple[list[Job], int]:
        return await self._job_dao.get_all(
            page=pagination.page,
            limit=pagination.size,
        )

    async def get_job_details(self, job_id: int) -> JobDetailsDTO:
        job = await self._job_dao.get_by_id_with_relations(job_id)
        if not job:
            raise JobNotFoundException

        project_property = job.property
        if not project_property:
            raise ProjectPropertyNotFoundException

        project = project_property.project
        if not project:
            raise ProjectPropertyNotFoundException

        client = project.client
        if not client:
            raise ClientNotFoundException

        inspector = job.inspector

        inspector_name = inspector.full_name if inspector else None

        job_created = True
        inspection_scheduled = False
        inspection_completed = False
        lab_results_received = False
        invoice_sent_to_client = False
        report_generated = False
        report_sent_to_client = False

        steps = [
            job_created,
            inspection_scheduled,
            inspection_completed,
            lab_results_received,
            invoice_sent_to_client,
            report_generated,
            report_sent_to_client,
        ]
        completed_steps = sum(1 for step in steps if step)
        progress_percent = int(completed_steps / len(steps) * 100)

        job_info = JobInfoDTO(
            job_type=job.inspection_type,
            owner_name=client.full_name,
            property_manager=project.property_manager_name,
            owner_business_address=client.business_address,
            owner_email=client.email,
            owner_phone_number=client.phone_number,
            status=project.status,
            inspector=inspector_name,
            created_at=job.created_at,
            scheduled_time=None,
            progress_percent=progress_percent,
        )

        property_details = JobPropertyDetailsDTO(
            property_address=project_property.address,
            structure_type=project_property.type,
            number_of_units=project_property.number_of_units,
            inspection_date=job.created_at,
            owner_lcc_name=project_property.owner_lcc_name,
            year_of_construction=project_property.year_of_construction,
            parcel_number=project_property.parcel_number,
            rental_registration_number=project_property.rental_registration_number,
        )

        inspection_progress = JobInspectionProgressDTO(
            job_created=job_created,
            inspection_scheduled=inspection_scheduled,
            inspection_completed=inspection_completed,
            lab_results_received=lab_results_received,
            invoice_sent_to_client=invoice_sent_to_client,
            report_generated=report_generated,
            report_sent_to_client=report_sent_to_client,
        )

        return JobDetailsDTO(
            job=job_info,
            property=property_details,
            progress=inspection_progress,
            notes=job.notes,
        )

    async def get_jobs_by_project(
        self,
        project_id: int,
        pagination: PaginationParams,
        filters: JobListFiltersSchema,
    ) -> tuple[list[JobListItemDTO], int]:
        jobs, total = await self._job_dao.get_by_project_id(
            project_id=project_id,
            page=pagination.page,
            limit=pagination.size,
            status=filters.status,
            inspector_id=filters.inspector_id,
            created_on_date=filters.date,
        )

        items: list[JobListItemDTO] = []
        for job in jobs:
            project_property = job.property
            if not project_property:
                continue
            project = project_property.project
            if not project:
                continue

            inspector = job.inspector
            inspector_name = inspector.full_name if inspector else None

            job_created = True
            inspection_scheduled = False
            inspection_completed = False
            lab_results_received = False
            invoice_sent_to_client = False
            report_generated = False
            report_sent_to_client = False

            steps = [
                job_created,
                inspection_scheduled,
                inspection_completed,
                lab_results_received,
                invoice_sent_to_client,
                report_generated,
                report_sent_to_client,
            ]
            completed_steps = sum(1 for step in steps if step)
            progress_percent = int(completed_steps / len(steps) * 100)

            items.append(
                JobListItemDTO(
                    property_address=project_property.address,
                    status=project.status,
                    job_type=job.inspection_type,
                    inspector=inspector_name,
                    units=project_property.number_of_units,
                    progress=progress_percent,
                    date_created=job.created_at,
                )
            )

        return items, total

    async def get_jobs_by_inspector(
        self,
        inspector_id: int,
        pagination: PaginationParams,
    ) -> tuple[list[JobListItemDTO], int]:
        jobs, total = await self._job_dao.get_by_inspector_id_paginated(
            inspector_id=inspector_id,
            page=pagination.page,
            limit=pagination.size,
        )

        items: list[JobListItemDTO] = []
        for job in jobs:
            project_property = job.property
            if not project_property:
                continue
            project = project_property.project
            if not project:
                continue

            inspector = job.inspector
            inspector_name = inspector.full_name if inspector else None

            job_created = True
            inspection_scheduled = False
            inspection_completed = False
            lab_results_received = False
            invoice_sent_to_client = False
            report_generated = False
            report_sent_to_client = False

            steps = [
                job_created,
                inspection_scheduled,
                inspection_completed,
                lab_results_received,
                invoice_sent_to_client,
                report_generated,
                report_sent_to_client,
            ]
            completed_steps = sum(1 for step in steps if step)
            progress_percent = int(completed_steps / len(steps) * 100)

            items.append(
                JobListItemDTO(
                    property_address=project_property.address,
                    status=project.status,
                    job_type=job.inspection_type,
                    inspector=inspector_name,
                    units=project_property.number_of_units,
                    progress=progress_percent,
                    date_created=job.created_at,
                )
            )

        return items, total
