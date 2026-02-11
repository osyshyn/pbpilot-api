from sqlalchemy import String, Enum, CheckConstraint
from sqlalchemy.orm import Mapped, mapped_column

from core.models import BaseIdMixin, BaseTimeStampMixin, SoftDelete

from enum import StrEnum

class BuildingTypeEnum(StrEnum):
    SINGLE_FAMILY = "SINGLE_FAMILY_HOUSE"
    DUPLEX = "DUPLEX"
    SINGLE_STRUCTURE_MULTI_FAMILY = "SINGLE_STRUCTURE_MULTI_FAMILY"
    MULTI_STRUCTURE = "MULTI_STRUCTURE"
    COMMERCIAL = "COMMERCIAL"


class Project(BaseIdMixin, BaseTimeStampMixin, SoftDelete):
    __tablename__ = 'projects'
    # TODO: Add client ID relation

    # General information
    project_name: Mapped[str] = mapped_column(
        String(255),
        nullable=False
    )
    property_manager_name: Mapped[str] = mapped_column(
        String(255),
        nullable=True,
        blank=True
    ) # Property manager is optional for a project

    def __repr__(self) -> str:
        return f'<Project {self.project_name}>'

class ProjectProperty(BaseIdMixin, BaseTimeStampMixin, SoftDelete):
    __tablename__ = 'project_properties'
    # ====
    # TODO: Add project ID relation
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

class PropertyStructure(BaseIdMixin, BaseTimeStampMixin, SoftDelete):
    __tablename__ = 'property_structures'
    __table_args__ = (
        CheckConstraint(
            "type != 'MULTI_STRUCTURE'",
            name="ck_project_property_no_multi_structure"
        ),
    )
    address: Mapped[str] = mapped_column(
        String(255),
        nullable=False
    )
    type: Mapped[BuildingTypeEnum] = mapped_column(
        Enum(BuildingTypeEnum, name='property_type_enum', create_type=False),
        nullable=False
    ) # Structure cannot have type MULTI_STRUCTURE
    number_of_units: Mapped[int] = mapped_column(
        nullable=False
    )