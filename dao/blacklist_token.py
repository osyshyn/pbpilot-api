from sqlalchemy import select

from core.dao import BaseDAO
from models import BlacklistToken


class BlacklistTokenDAO(BaseDAO):
    """DAO for BlacklistToken model."""

    async def get_by_jti(self, jti: str) -> BlacklistToken | None:
        """Get blacklist token by jti.

        Args:
            jti: JWT ID claim.

        Returns:
            BlacklistToken | None: Blacklist token instance or None.

        """
        stmt = select(BlacklistToken).where(BlacklistToken.jti == jti)
        result = await self._session.execute(stmt)
        return result.scalar_one_or_none()

    async def create(
        self,
        *,
        jti: str,
        user_id: int,
        expires_at: int,
    ) -> BlacklistToken:
        """Create a new blacklist token entry.

        Args:
            jti: JWT ID claim.
            user_id: User ID.
            expires_at: Token expiration timestamp (Unix time).

        Returns:
            BlacklistToken: Created blacklist token instance.

        """
        token = BlacklistToken(
            jti=jti,
            user_id=user_id,
            expires_at=expires_at,
        )
        self._session.add(token)
        await self._session.flush()
        await self._session.refresh(token)
        return token

    async def is_blacklisted(self, jti: str) -> bool:
        """Check if token is blacklisted.

        Args:
            jti: JWT ID claim.

        Returns:
            bool: True if token is blacklisted, False otherwise.

        """
        token = await self.get_by_jti(jti)
        return token is not None
