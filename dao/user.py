from core.dao import BaseDAO
from models import User
from models.user import UserRoleEnum
from sqlalchemy import select, update
from datetime import UTC, datetime


class UserDAO(BaseDAO):
    async def create(
            self,
            *,
            name: str,
            surname: str,
            email: str,
            password: str,
            role: UserRoleEnum,
            phone_number: str | None = None,
    ) -> User:
        user = User(
            name=name,
            surname=surname,
            email=email,
            password=password,
            role=role,
            phone_number=phone_number,
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

