"""Shared SQLAlchemy model mixins and base classes."""

from datetime import datetime
import uuid

from sqlalchemy import TIMESTAMP, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from config.database import Base


class BaseIdMixin(Base):
    """Base model mixin for ID primary key.

    Provides a standard integer primary key field for all models.
    This is an abstract base class that should be inherited by other models.

    Attributes:
        id: Integer primary key field.

    """

    __abstract__ = True

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)


class BaseUUIDMixin(Base):
    """Base model mixin for UUID primary key.

    Provides a standard UUID primary key field for models
    that are synchronized with offline clients.
    This is an abstract base class that should be inherited
    by other models.

    Attributes:
        id: UUID primary key field.

    """

    __abstract__ = True

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )


class BaseTimeStampMixin(Base):
    """Base model mixin for timestamp fields.

    Provides standard timestamp fields (created_at, updated_at) for all models.
    This is an abstract base class that should be inherited by other models.

    Attributes:
        created_at: Timestamp when the record was created (auto-set on insert).
        updated_at: Timestamp when the record was last updated (auto-updated).

    """

    __abstract__ = True

    created_at: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True),
        default=func.now(),
    )
    updated_at: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
    )


class SoftDelete(Base):
    """Base model mixin for soft delete functionality.

    Adds soft delete is_active flag and deleted_at timestamp.
    Records are marked as inactive instead of being physically deleted from db.
    This is an abstract base class that should be inherited by other models.

    Attributes:
        is_active: Flag indicating if the record is active or soft-deleted.
        deleted_at: Timestamp when the record was soft-deleted (None if active).

    """

    __abstract__ = True

    is_active: Mapped[bool] = mapped_column(
        nullable=False,
        default=True,
    )
    deleted_at: Mapped[datetime | None] = mapped_column(
        TIMESTAMP(timezone=True),
        nullable=True,
        default=None,
        comment='Indicates if the instance is active',
    )
