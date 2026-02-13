import enum
from datetime import time
from typing import List, Optional

from sqlalchemy import String, Integer, Time, ForeignKey, Boolean
from sqlalchemy.orm import Mapped, mapped_column, relationship

from core.models import BaseIdMixin, BaseTimeStampMixin


class WeekdayEnum(enum.IntEnum):
    MONDAY = 0
    TUESDAY = 1
    WEDNESDAY = 2
    THURSDAY = 3
    FRIDAY = 4
    SATURDAY = 5
    SUNDAY = 6


class Company(BaseIdMixin, BaseTimeStampMixin):
    __tablename__ = 'companies'

    company_name: Mapped[str] = mapped_column(
        String(255),
        nullable=False
    )

    phone_number: Mapped[Optional[str]] = mapped_column(
        String(16),
        nullable=True,
        comment='Phone number of the company'
    )

    address: Mapped[str] = mapped_column(
        String(255),
        nullable=False
    )

    # Save string like "Europe/London"
    timezone: Mapped[str] = mapped_column(
        String(50),
        default="UTC"
    )

    schedule: Mapped[List["CompanySchedule"]] = relationship(
        back_populates="company",
        cascade="all, delete-orphan",
        order_by="CompanySchedule.day_of_week",
    )

    logo_key: Mapped[str | None] = mapped_column(
        String(512),
        nullable=True,
        comment='S3 key for image',
    )
    tax_state: Mapped[str] = mapped_column(
        String(32),
        nullable=False
    )
    tax_percentage: Mapped[float] = mapped_column(
        nullable=False
    )

    # TODO: Implement taxes per state, STATE - TAX in %, add tax behaviour to the project
    def __repr__(self) -> str:
        return f"<Company(id={self.id}, name={self.company_name})>"


class CompanySchedule(BaseIdMixin):
    __tablename__ = 'company_schedules'

    company_id: Mapped[int] = mapped_column(
        ForeignKey("companies.id", ondelete="CASCADE"),
        nullable=False
    )

    # Store is an integer
    day_of_week: Mapped[int] = mapped_column(
        Integer,
        nullable=False
    )

    start_time: Mapped[Optional[time]] = mapped_column(
        Time,
        nullable=True
    )
    end_time: Mapped[Optional[time]] = mapped_column(
        Time,
        nullable=True
    )

    is_day_off: Mapped[bool] = mapped_column(
        Boolean,
        default=False
    )

    company: Mapped["Company"] = relationship(
        back_populates="schedule"
    )

    def _get_status(self) -> str:
        return "Off" if self.is_day_off else f"{self.start_time}-{self.end_time}"

    def __repr__(self) -> str:
        return f"<Schedule(company={self.company_id}, day={self.day_of_week}, {self._get_status()})>"
