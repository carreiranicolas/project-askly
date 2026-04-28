"""Password hashing service."""

from werkzeug.security import check_password_hash, generate_password_hash


class PasswordHasher:
    """
    Service for password hashing using Werkzeug.

    Uses pbkdf2:sha256 algorithm by default.
    """

    def __init__(self, method: str = "pbkdf2:sha256", salt_length: int = 16):
        self._method = method
        self._salt_length = salt_length

    def hash(self, password: str) -> str:
        """
        Generate password hash.

        Args:
            password: Plain text password

        Returns:
            Hashed password string
        """
        return generate_password_hash(password, method=self._method, salt_length=self._salt_length)

    def verify(self, plain_password: str, hashed_password: str) -> bool:
        """
        Verify password against hash.

        Args:
            plain_password: Plain text password to verify
            hashed_password: Stored hash to compare against

        Returns:
            True if password matches, False otherwise
        """
        return check_password_hash(hashed_password, plain_password)
