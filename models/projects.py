from sqlalchemy import String, Enum, CheckConstraint, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from core.models import BaseIdMixin, BaseTimeStampMixin, SoftDelete
from enum import StrEnum
from typing import TYPE_CHECKING
from sqlalchemy import Index, text

if TYPE_CHECKING:
    from models.client import Client


class BuildingTypeEnum(StrEnum):
    SINGLE_FAMILY = "SINGLE_FAMILY_HOUSE"
    DUPLEX = "DUPLEX"
    SINGLE_STRUCTURE_MULTI_FAMILY = "SINGLE_STRUCTURE_MULTI_FAMILY"
    MULTI_STRUCTURE = "MULTI_STRUCTURE"
    COMMERCIAL = "COMMERCIAL"


class Project(BaseIdMixin, BaseTimeStampMixin, SoftDelete):
    __tablename__ = 'projects'

    __table_args__ = (
        Index(
            "ix_projects_client_not_deleted",
            "client_id",
            postgresql_where=text("deleted_at IS NULL"),
        ),
    )

    client_id: Mapped[int] = mapped_column(
        ForeignKey("clients.id", ondelete="CASCADE"),
        nullable=False,
    )

    # General information
    project_name: Mapped[str] = mapped_column(
        String(255),
        nullable=False
    )
    property_manager_name: Mapped[str] = mapped_column(
        String(255),
        nullable=True,
        blank=True
    )  # Property manager is optional for a project

    client: Mapped["Client"] = relationship(
        back_populates="projects"
    )

    properties: Mapped[list["ProjectProperty"]] = relationship(
        back_populates="project",
        cascade="all, delete-orphan",
    )

    def __repr__(self) -> str:
        return f'<Project {self.project_name}>'


class ProjectProperty(BaseIdMixin, BaseTimeStampMixin, SoftDelete):
    __tablename__ = 'project_properties'

    __table_args__ = (
        Index(
            "ix_project_properties_project_not_deleted",
            "project_id",
            postgresql_where=text("deleted_at IS NULL"),
        ),
    )

    address: Mapped[str] = mapped_column(
        String(255),
        nullable=False
    )
    type: Mapped[BuildingTypeEnum] = mapped_column(
        Enum(BuildingTypeEnum, name='property_type_enum', create_type=False),
        nullable=False
    )
    number_of_units: Mapped[int] = mapped_column(
        nullable=False
    )
    owner_lcc_name: Mapped[str] = mapped_column(
        String(255),
        nullable=True,
        blank=True
    )
    year_of_construction: Mapped[int] = mapped_column(
        nullable=True,
        blank=True
    )
    parcel_number: Mapped[str] = mapped_column(
        String(255),
        nullable=True,
        blank=True
    )
    rental_registration_number: Mapped[str] = mapped_column(
        String(255),
        nullable=True,
        blank=True
    )

    project_id: Mapped[int] = mapped_column(
        ForeignKey("projects.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )

    project: Mapped["Project"] = relationship(
        back_populates="properties"
    )

    structures: Mapped[list["PropertyStructure"]] = relationship(
        back_populates="property",
        cascade="all, delete-orphan",
    )

    def __repr__(self) -> str:
        return f'<ProjectProperty {self.address}>'


class PropertyStructure(BaseIdMixin, BaseTimeStampMixin, SoftDelete):
    __tablename__ = 'property_structures'
    __table_args__ = (
        CheckConstraint(
            "type != 'MULTI_STRUCTURE'",
            name="ck_project_property_no_multi_structure"
        ),
        Index(
            "ix_property_structures_property_not_deleted",
            "property_id",
            postgresql_where=text("deleted_at IS NULL"),
        ),
    )
    address: Mapped[str] = mapped_column(
        String(255),
        nullable=False
    )
    type: Mapped[BuildingTypeEnum] = mapped_column(
        Enum(BuildingTypeEnum, name='property_type_enum', create_type=False),
        nullable=False
    )  # Structure cannot have type MULTI_STRUCTURE
    number_of_units: Mapped[int] = mapped_column(
        nullable=False
    )

    property_id: Mapped[int] = mapped_column(
        ForeignKey("project_properties.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )

    property: Mapped["ProjectProperty"] = relationship(
        back_populates="structures"
    )

    def __repr__(self) -> str:
        return f'<PropertyStructure {self.address}>'
