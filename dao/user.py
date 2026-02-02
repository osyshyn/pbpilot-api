from core.dao import BaseDAO
from models import User
from models.user import UserRoleEnum


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