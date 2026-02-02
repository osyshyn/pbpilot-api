import uuid
from calendar import timegm
from datetime import UTC, datetime, timedelta

from jose import JWTError, jwt

from config.settings import Settings
from dto import AccessTokenDTO
from exceptions import (
    AccessTokenExpiredException,
    RefreshTokenException,
    WrongCredentialsException,
)

settings = Settings.load()


class TokenManager:
    """Manager for creating, decoding, and validating JWT tokens."""

    @staticmethod
    def _get_expiration_delta() -> datetime:
        return datetime.now(UTC) + timedelta(
            minutes=settings.token_settings.ACCESS_TOKEN_EXPIRE_MINUTES
        )

    @classmethod
    def generate_access_token(cls, author_id: int) -> str:
        """Generate a JWT access token for the given author ID.

        Args:
            author_id (int): The ID of the author for whom the token.

        Returns:
            str: Encoded JWT access token.

        """
        to_encode = AccessTokenDTO(
            sub=str(author_id), exp=cls._get_expiration_delta()
        )
        encoded_jwt: str = jwt.encode(
            to_encode.to_dict(),
            settings.token_settings.SECRET_KEY,
            algorithm=settings.token_settings.ALGORITHM,
        )
        return encoded_jwt

    @classmethod
    def _get_refresh_expiration_delta(cls) -> datetime:
        """Get expiration datetime for refresh token.

        Returns:
            datetime: Expiration datetime in UTC.

        """
        return datetime.now(UTC) + timedelta(
            days=settings.token_settings.REFRESH_TOKEN_EXPIRE_DAYS
        )

    @classmethod
    def generate_refresh_token(cls, author_id: int) -> str:
        """Generate a JWT refresh token for the given author ID.

        Args:
            author_id (int): The ID of the author for whom the token.

        Returns:
            str: Encoded JWT refresh token.

        """
        jti = str(uuid.uuid4())
        exp = cls._get_refresh_expiration_delta()
        to_encode = {
            'sub': str(author_id),
            'exp': exp,
            'jti': jti,
            'type': 'refresh',
        }
        encoded_jwt: str = jwt.encode(
            to_encode,
            settings.token_settings.SECRET_KEY,
            algorithm=settings.token_settings.ALGORITHM,
        )
        return encoded_jwt

    @classmethod
    def decode_access_token(cls, token: str) -> dict[str, str | int]:
        """Decode a JWT access token to retrieve its payload.

        Args:
            token (str): JWT access token.

        Returns:
            dict[str, str | int]: Decoded token payload.

        Raises:
            WrongCredentialsException: If a token is invalid can't be decoded.

        """
        try:
            decoded_jwt: dict[str, str | int] = jwt.decode(
                token=token,
                key=settings.token_settings.SECRET_KEY,
                algorithms=settings.token_settings.ALGORITHM,
            )
        except JWTError:
            raise WrongCredentialsException from None
        return decoded_jwt

    @classmethod
    def validate_access_token_expired(
        cls, decoded: dict[str, str | int]
    ) -> None:
        """Validate whether a decoded JWT access token has expired.

        Args:
            decoded (dict[str, str | int]): Decoded JWT token payload.

        Raises:
            AccessTokenExpiredException: If the token is expired.

        """
        jwt_exp_date: int = int(decoded.get('exp', 0))
        current_time: int = timegm(datetime.now(UTC).utctimetuple())
        if not jwt_exp_date or current_time >= jwt_exp_date:
            raise AccessTokenExpiredException

    @classmethod
    def decode_refresh_token(cls, token: str) -> dict[str, str | int]:
        """Decode a JWT refresh token to retrieve its payload.

        Args:
            token (str): JWT refresh token.

        Returns:
            dict[str, str | int]: Decoded token payload.

        Raises:
            WrongCredentialsException: If a token is invalid can't be decoded.

        """
        try:
            decoded_jwt: dict[str, str | int] = jwt.decode(
                token=token,
                key=settings.token_settings.SECRET_KEY,
                algorithms=settings.token_settings.ALGORITHM,
            )
        except JWTError:
            raise WrongCredentialsException from None
        return decoded_jwt

    @classmethod
    def validate_refresh_token_expired(
        cls, decoded: dict[str, str | int]
    ) -> None:
        """Validate whether a decoded JWT refresh token has expired.

        Args:
            decoded (dict[str, str | int]): Decoded JWT token payload.

        Raises:
            RefreshTokenException: If the token is expired.

        """
        jwt_exp_date: int = int(decoded.get('exp', 0))
        current_time: int = timegm(datetime.now(UTC).utctimetuple())
        if not jwt_exp_date or current_time >= jwt_exp_date:
            raise RefreshTokenException

    @classmethod
    def get_jti_from_token(cls, decoded: dict[str, str | int]) -> str:
        """Extract JWT ID (jti) from decoded token.

        Args:
            decoded (dict[str, str | int]): Decoded JWT token payload.

        Returns:
            str: JWT ID claim.

        Raises:
            RefreshTokenException: If jti is missing or invalid.

        """
        jti: str | int | None = decoded.get('jti')
        if not jti or not isinstance(jti, str):
            raise RefreshTokenException
        return jti
