from sqlalchemy.ext.asyncio.session import AsyncSession

from core import BaseService
from dao import BlacklistTokenDAO, UserDAO
from exceptions import (
    RefreshTokenException,
    UserIsNotActiveException,
    WrongCredentialsException,
)
from models import User
from models.user import UserRoleEnum
from services.jwt.hasher import Hasher
from services.jwt.token import TokenManager


class AuthService(BaseService):
    """Service responsible for author authentication and JWT management."""

    def __init__(
        self,
        db_session: AsyncSession,
        *,
        user_dao: UserDAO | None = None,
        blacklist_token_dao: BlacklistTokenDAO | None = None,
        hash_service: Hasher | None = None,
        token_manager_service: Hasher | None = None,
    ) -> None:
        """Initialize AuthService."""
        super().__init__(
            db_session,
        )
        self._user_dao = user_dao or UserDAO(db_session)
        self._blacklist_token_dao = blacklist_token_dao or BlacklistTokenDAO(
            db_session
        )
        self._hash_service = hash_service or Hasher()
        self._token_manager_service = token_manager_service or TokenManager()

    @staticmethod
    def _verify_user_password(author_password: str, password: str) -> None:
        """Verify that the provided password matches the stored password.

        Args:
            author_password (str): Hashed password from the database.
            password (str): Plain password provided by user.

        Raises:
            WrongCredentialsException: If password does not match.

        """
        if not author_password or not Hasher.verify_password(
            password, author_password
        ):
            raise WrongCredentialsException

    async def auth_user(self, email: str, password: str) -> User:
        """Authenticate an author using email and password.

        Args:
            email (str): Author's email.
            password (str): Plain text password.

        Returns:
            dict[str, Any]: Author data from the database.

        Raises:
            WrongCredentialsException: If email or password are invalid.

        """
        user = await self._user_dao.get_by_email(email=email)
        if not user:
            raise WrongCredentialsException
        if not user.is_active:
            raise UserIsNotActiveException
        self._verify_user_password(user.password, password)
        # Update last login timestamp
        await self._session.commit()
        await self._session.refresh(user)
        return user

    async def create_token(
        self,
        author_id: int,
    ) -> tuple[str, str]:
        """Generate access and refresh tokens for an author.

        Args:
            author_id (int): ID of the author.

        Returns:
            TokenResponseSchemas: Access and refresh tokens with token type.

        """
        access_token: str = TokenManager.generate_access_token(
            author_id=author_id
        )
        refresh_token: str = TokenManager.generate_refresh_token(
            author_id=author_id
        )
        return access_token, refresh_token

    async def refresh_token(
        self, refresh_token: str
    ) -> tuple[str, str, UserRoleEnum]:
        """Refresh access and refresh tokens using a valid refresh token.

        Args:
            refresh_token (str): Existing JWT refresh token.

        Returns:
            TokenResponseSchemas: New access and refresh tokens.

        Raises:
            RefreshTokenException: If a token is invalid, expired, or blocked.

        """
        decoded = TokenManager.decode_refresh_token(refresh_token)
        TokenManager.validate_refresh_token_expired(decoded)

        jti = TokenManager.get_jti_from_token(decoded)
        is_blacklisted = await self._blacklist_token_dao.is_blacklisted(jti)
        if is_blacklisted:
            raise RefreshTokenException

        user_id_str = self._get_user_id_from_jwt(decoded)
        user_id = int(user_id_str)
        user = await self._user_dao.get_by_id(user_id=user_id)
        if not user or not user.is_active:
            raise RefreshTokenException

        access_token: str = TokenManager.generate_access_token(
            author_id=user_id
        )
        new_refresh_token: str = TokenManager.generate_refresh_token(
            author_id=user_id
        )

        # Blacklist old refresh token to prevent reuse
        expires_at = int(decoded.get('exp', 0))
        if expires_at:
            await self._blacklist_token_dao.create(
                jti=jti,
                user_id=user_id,
                expires_at=expires_at,
            )
            await self._session.commit()
        return access_token, new_refresh_token, user.role

    async def logout_user(
        self,
        refresh_token: str | None,
    ) -> None:
        """Logout a user by adding their refresh token to blacklist.

        Args:
            refresh_token (str | None): JWT refresh token to blacklist.

        Raises:
            RefreshTokenException: If token is invalid or missing.

        """
        if not refresh_token:
            raise RefreshTokenException

        try:
            decoded = TokenManager.decode_refresh_token(refresh_token)
            TokenManager.validate_refresh_token_expired(decoded)

            jti = TokenManager.get_jti_from_token(decoded)
            user_id_str = self._get_user_id_from_jwt(decoded)
            user_id = int(user_id_str)

            expires_at = int(decoded.get('exp', 0))
            if not expires_at:
                raise RefreshTokenException

            is_blacklisted = await self._blacklist_token_dao.is_blacklisted(jti)
            if not is_blacklisted:
                await self._blacklist_token_dao.create(
                    jti=jti,
                    user_id=user_id,
                    expires_at=expires_at,
                )
                await self._session.commit()
        except (WrongCredentialsException, RefreshTokenException):
            raise RefreshTokenException from None

    @staticmethod
    def _get_user_id_from_jwt(decoded_jwt: dict[str, str | int]) -> str:
        """Extract the user ID from a decoded JWT payload.

        Args:
            decoded_jwt (dict[str, str | int]): Decoded JWT token.

        Returns:
            str: User ID from JWT.

        Raises:
            WrongCredentialsException: If user ID is missing or invalid.

        """
        user_id: int | str | None = decoded_jwt.get('sub')
        if not user_id or isinstance(user_id, int):
            raise WrongCredentialsException
        return user_id

    async def validate_token_for_user(self, user_jwt_token: str) -> int:
        """Validate an access token and extract the user ID.

        Args:
            user_jwt_token (str): JWT access token.

        Returns:
            int | str: User ID extracted from the token.

        Raises:
            WrongCredentialsException: If token is invalid or expired.

        """
        decoded_jwt: dict[str, str | int] = TokenManager.decode_access_token(
            token=user_jwt_token,
        )
        TokenManager.validate_access_token_expired(decoded_jwt)
        user_id: int | str = self._get_user_id_from_jwt(decoded_jwt)
        if not user_id:
            raise WrongCredentialsException
        return int(user_id) if isinstance(user_id, str) else user_id
