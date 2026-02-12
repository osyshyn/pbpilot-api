from datetime import UTC, datetime

from sqlalchemy import select, update

from core.dao import BaseDAO
from models import User
from models.user import MarketingSourceEnum, UserRoleEnum


class UserDAO(BaseDAO):
    """DAO for User model."""

    async def create(
        self,
        *,
        name: str,
        surname: str,
        email: str,
        password: str,
        role: UserRoleEnum,
        phone_number: str | None = None,
        free_reports_count: int = 5,
        marketing_source: MarketingSourceEnum,
        marketing_source_details: str | None = None,
        is_active: bool = True,
    ) -> User:
        """Create a new user.

        Args:
            name: User name.
            surname: User surname.
            email: User email.
            password: User password.
            role: User role.
            phone_number: User phone number (optional).
            free_reports_count: Number of free reports available for the user.
            marketing_source: Marketing source of the user.
            marketing_source_details: Additional marketing source details.
            is_active: Is created user will be active?.

        Returns:
            User: User instance.

        """
        user = User(
            name=name,
            surname=surname,
            email=email,
            password=password,
            role=role,
            phone_number=phone_number,
            free_reports_count=free_reports_count,
            is_active=is_active,
            marketing_source=marketing_source,
            marketing_source_details=marketing_source_details,
        )
        self._session.add(user)
        await self._session.flush()
        await self._session.refresh(user)
        return user

    async def get_by_id(self, user_id: int) -> User | None:
        """Get user by id.

        Args:
            user_id: User ID.

        Returns:
            User | None: User instance or None if not found.

        """
        stmt = select(User).where(User.id == user_id)
        result = await self._session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_by_email(self, email: str) -> User | None:
        """Get user by email.

        Args:
            email: User email address.

        Returns:
            User | None: User instance or None if not found.

        """
        stmt = select(User).where(User.email == email)
        result = await self._session.execute(stmt)
        return result.scalar_one_or_none()

    async def delete_by_id(self, user_id: int) -> User | None:
        """Delete user by id.

        Args:
            user_id: User ID.

        Returns:
            User | None: Deleted user instance or None if not found.

        """
        stmt = (
            update(User)
            .where(User.id == user_id)
            .values(is_active=False, deleted_at=datetime.now(UTC))
            .returning(User)
        )

        result = await self._session.execute(stmt)
        return result.scalar_one_or_none()

    async def activate_user_by_id(self, user_id: int) -> User | None:
        stmt = (
            update(User)
            .where(User.id == user_id)
            .values(is_active=True, deleted_at=None)
            .returning(User)
        )
        result = await self._session.execute(stmt)
        return result.scalar_one_or_none()

    async def activate_user_by_email(self, email: str) -> User | None:
        stmt = (
            update(User)
            .where(User.email == email)
            .values(is_active=True, deleted_at=None)
            .returning(User)
        )
        result = await self._session.execute(stmt)
        return result.scalar_one_or_none()
