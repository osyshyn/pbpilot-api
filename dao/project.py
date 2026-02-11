from sqlalchemy import select
from sqlalchemy.orm import selectinload

from core.dao import BaseDAO
from models import Project, ProjectProperty, PropertyStructure
from schemas.projects import CreatePropertyRequestSchema


class ProjectDAO(BaseDAO):
    """DAO for Project model."""

    async def create_with_properties(
        self,
        *,
        client_id: int,
        project_name: str,
        property_manager_name: str | None = None,
        properties_data: list[CreatePropertyRequestSchema],
    ) -> Project:
        """Create a project with properties and structures."""
        project = Project(
            client_id=client_id,
            project_name=project_name,
            property_manager_name=property_manager_name,
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
                selectinload(Project.properties).selectinload(ProjectProperty.structures),
            )
        )
        result = await self._session.execute(stmt)
        return result.scalar_one_or_none()
