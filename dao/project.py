from datetime import UTC, datetime
from typing import Any

from sqlalchemy import select, update
from sqlalchemy.orm import selectinload

from core.dao import BaseDAO
from dto import (
    NeedScheduledDTO,
    OngoingProjectDTO,
    ProjectDashboardDTO,
    ReadyToFinalizeDTO,
    UnassignedJobsDTO,
)
from models import Project, ProjectProperty, PropertyStructure
from models.projects import ProjectStatusEnum
from schemas.projects import CreatePropertyRequestSchema


class ProjectDAO(BaseDAO):
    """DAO for Project model."""

    _PROJECT_SEARCH_LIMIT = 15

    async def create_with_properties(
        self,
        *,
        client_id: int,
        project_name: str,
        property_manager_name: str | None = None,
        status: ProjectStatusEnum,
        properties_data: list[CreatePropertyRequestSchema],
    ) -> Project:
        """Create a project with properties and structures."""
        project = Project(  # TODO: Rewrite optimize this
            client_id=client_id,
            project_name=project_name,
            property_manager_name=property_manager_name,
            status=status,
        )
        self._session.add(project)
        await self._session.flush()

        for prop_data in properties_data:
            prop = ProjectProperty(
                project_id=project.id,
                address=prop_data.address,
                type=prop_data.type,
                number_of_units=prop_data.number_of_units,
                owner_lcc_name=prop_data.owner_lcc_name,
                year_of_construction=prop_data.year_of_construction,
                parcel_number=prop_data.parcel_number,
                rental_registration_number=prop_data.registration_number,
            )
            self._session.add(prop)
            await self._session.flush()
            for struct_data in prop_data.structures:
                struct = PropertyStructure(
                    property_id=prop.id,
                    address=struct_data.structure_address,
                    type=struct_data.structure_type,
                    number_of_units=struct_data.number_of_units,
                )
                self._session.add(struct)
        await self._session.flush()
        await self._session.refresh(project)
        return project

    async def get_by_id_with_relations(self, project_id: int) -> Project | None:
        """Get project by id with properties and structures loaded."""
        stmt = (
            select(Project)
            .where(Project.id == project_id, Project.deleted_at.is_(None))
            .options(
                selectinload(Project.properties).selectinload(
                    ProjectProperty.structures
                ),
            )
        )
        result = await self._session.execute(stmt)
        return result.scalar_one_or_none()

    async def update_by_id(
        self,
        project_id: int,
        update_data: dict[str, Any],
    ) -> Project | None:
        """Update project by id."""
        project = await self.get_by_id_with_relations(project_id)
        if not project:
            return None
        for key, value in update_data.items():
            if hasattr(project, key):
                setattr(project, key, value)
        await self._session.flush()
        await self._session.refresh(project)
        return project

    async def delete_by_id(self, project_id: int) -> Project | None:
        """Soft delete project by id."""
        stmt = (
            update(Project)
            .where(Project.id == project_id, Project.is_active == True)  # noqa: E712
            .values(is_active=False, deleted_at=datetime.now(UTC))
            .returning(Project)
        )
        result = await self._session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_all(
        self,
        page: int,
        limit: int,
    ) -> tuple[list[Project], int]:
        """Get all active projects with pagination."""
        stmt = (
            select(Project)
            .where(Project.is_active == True)  # noqa: E712
            .options(
                selectinload(Project.properties).selectinload(
                    ProjectProperty.structures
                ),
            )
        )
        return await self.paginate(query=stmt, page=page, limit=limit)

    async def get_projects_dashboard(self, user_id: int) -> ProjectDashboardDTO:
        # TODO: Add actual quesry right here, and make it per user

        # now = datetime.now(timezone.utc)
        # week_ago = now - timedelta(days=7)
        # stats_stmt = select(
        #     func.count(Project.id).label("ongoing"),
        #     func.count(Project.id)
        #     .filter(Project.scheduled_at.isnot(None))
        #     .label("scheduled"),
        #     func.count(Project.id)
        #     .filter(Project.scheduled_at.is_(None))
        #     .label("unscheduled"),
        #     func.count(Project.id)
        #     .filter(Project.assigned_at.is_(None))
        #     .label("unassigned"),
        #     func.count(Project.id)
        #     .filter(
        #         Project.completed_at.isnot(None),
        #         Project.completed_at >= week_ago,
        #     )
        #     .label("completed_last_week"),
        #     func.count(Project.id)
        #     .filter(
        #         Project.completed_at.isnot(None),
        #         Project.scheduled_at.isnot(None),
        #     )
        #     .label("ready_to_finalize"),
        # ).where(
        #     Project.is_active == True
        # )
        #
        # stats_result = await self.session.execute(stats_stmt)
        # stats = stats_result.one()
        #
        # names_stmt = select(
        #     Project.name,
        #     Project.scheduled_at,
        #     Project.assigned_at,
        #     Project.completed_at,
        # ).where(
        #     Project.is_active == True
        # )
        #
        # names_result = await self.session.execute(names_stmt)
        # projects = names_result.all()
        #
        # need_scheduling_names = []
        # unassigned_names = []
        # ready_to_finalize_names = []
        #
        # for name, scheduled_at, assigned_at, completed_at in projects:
        #     if scheduled_at is None:
        #         need_scheduling_names.append(name)
        #     if assigned_at is None:
        #         unassigned_names.append(name)
        #     if completed_at is not None and scheduled_at is not None:
        #         ready_to_finalize_names.append(name)

        # return ProjectDashboardDTO(
        #     ongoing_project=OngoingProjectDTO(
        #         amount=stats.ongoing_project,
        #         scheduled=stats.scheduled,
        #         need_scheduled=stats.unscheduled,
        #         completed_this_week=stats.completed_last_week,
        #     ),
        #     need_scheduling=NeedScheduledDTO(
        #         amount=stats.unscheduled,
        #         project_names=need_scheduling_names,
        #     ),
        #     unassigned_jobs=UnassignedJobsDTO(
        #         amount=stats.unassigned_jobs,
        #         project_names=unassigned_names,
        #     ),
        #     ready_for_finalize=ReadyToFinalizeDTO(
        #         amount=stats.ready_for_finalize,
        #         project_names=ready_to_finalize_names,
        #     )
        # )

        return ProjectDashboardDTO(
            ongoing_project=OngoingProjectDTO(
                amount=5,
                scheduled=4,
                need_scheduled=3,
                completed_this_week=2,
            ),
            need_scheduling=NeedScheduledDTO(
                amount=7,
                project_names=['Project 2', 'Project 4'],
            ),
            unassigned_jobs=UnassignedJobsDTO(
                amount=5,
                project_names=['Project 5', 'Project 6'],
            ),
            ready_for_finalize=ReadyToFinalizeDTO(
                amount=5,
                project_names=['Project 7', 'Project 8'],
            ),
        )

    async def search_by_name(self, project_name: str) -> list[Project]:
        _SEARCH_PATTERN = f'%{project_name}%'
        stmt = (
            select(Project)
            .where(
                Project.is_active == True,  # noqa: E712
                Project.project_name.ilike(_SEARCH_PATTERN),
            )
            .options(
                selectinload(Project.properties).selectinload(
                    ProjectProperty.structures
                ),
            )
        )

        stmt = stmt.order_by(
            Project.created_at.desc(), Project.id.desc()
        ).limit(ProjectDAO._PROJECT_SEARCH_LIMIT)
        result = await self._session.execute(stmt)
        return list(result.scalars().all())
