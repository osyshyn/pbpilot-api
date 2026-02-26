import logging

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from core import BaseService
from core.pagination import PaginationParams
from dao import InspectorDAO, JobDAO
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
    ProjectPropertyNotFoundException,
)
from exceptions.user import UserNotFoundByIdException
from models import Job
from models.projects import ProjectProperty
from schemas import AssignInspectorRequestSchema, CreateJobRequestSchema

logger = logging.getLogger(__name__)


class JobService(BaseService):
    def __init__(
        self,
        db_session: AsyncSession,
        *,
        job_dao: JobDAO | None = None,
        inspector_dao: InspectorDAO | None = None,
    ):
        super().__init__(db_session)
        self._job_dao = job_dao or JobDAO(db_session)
        self._inspector_dao = inspector_dao or InspectorDAO(db_session)

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
    ) -> tuple[list[JobListItemDTO], int]:
        jobs, total = await self._job_dao.get_by_project_id(
            project_id=project_id,
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
