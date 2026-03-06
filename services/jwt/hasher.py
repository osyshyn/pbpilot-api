import bcrypt


class Hasher:
    """Utility class for password hashing and verification.

    This class provides methods for securely hashing passwords and verifying
    hashed passwords using bcrypt algorithm.

    Methods:
        hash_password: Creates a secure hash from a plain text password.
        verify_password: Verifies if a plain text password matches its hash.

    """

    @classmethod
    def hash_password(cls: type['Hasher'], unhashed_password: str) -> str:
        """Return a hash of password.

        :param unhashed_password: A password to hash
        :return: hashed password
        """
        salt = bcrypt.gensalt()
        return bcrypt.hashpw(unhashed_password.encode('utf-8'), salt).decode(
            'utf-8'
        )

    @classmethod
    def verify_password(
        cls: type['Hasher'],
        unhashed_password: str,
        hashed_password: str,
    ) -> bool:
        """Check if raw password equal to hashed password.

        :param unhashed_password: Raw password
        :param hashed_password: Hashed password
        :return: True if hashed password identical to raw, false otherwise
        """
        return bcrypt.checkpw(
            unhashed_password.encode('utf-8'), hashed_password.encode('utf-8')
        )
