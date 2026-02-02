from sqlalchemy import ForeignKey, Index, String
from sqlalchemy.orm import Mapped, mapped_column

from core.models import BaseIdMixin, BaseTimeStampMixin


class BlacklistToken(BaseIdMixin, BaseTimeStampMixin):
    """Model for storing blacklisted JWT tokens.

    Tokens are stored by their jti (JWT ID) claim to enable efficient
    lookup and prevent reuse of revoked tokens.
    """

    __tablename__ = 'blacklist_tokens'

    jti: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
        unique=True,
        index=True,
        comment='JWT ID claim from the token',
    )
    user_id: Mapped[int] = mapped_column(
        ForeignKey('users.id', ondelete='CASCADE'),
        nullable=False,
        index=True,
        comment='User ID associated with the token',
    )
    expires_at: Mapped[int] = mapped_column(
        nullable=False,
        index=True,
        comment='Token expiration timestamp (Unix time)',
    )

    __table_args__ = (
        Index(
            'ix_blacklist_tokens_user_id_expires_at', 'user_id', 'expires_at'
        ),
    )

    def __repr__(self) -> str:
        """Return a string representation of the BlacklistToken instance."""
        return (
            f'<BlacklistToken(id={self.id}, jti={self.jti}, '
            f'user_id={self.user_id}, expires_at={self.expires_at})>'
        )
