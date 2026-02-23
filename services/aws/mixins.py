import mimetypes

from core.constants import (
    FILE_TYPE_TO_CATEGORY,
    MAX_FILE_SIZES,
    SUPPORTED_FILE_TYPES,
)
from exceptions import IncorrectFileSizeException, UnknownFiletypeException


class FileActionMixin:
    """Mixin class providing file type determination and validation methods.

    This mixin provides static methods for:
    - Determining file types from filenames or declared MIME types
    - Validating file sizes against configured limits
    - Getting category prefixes for file organization

    """

    @staticmethod
    def determine_file_type(
        file_name: str,
        declared_type: str | None = None,
    ) -> tuple[str, str]:
        """Determine file MIME type and category.

        First checks the declared content type, then attempts to guess
        from the filename if declared type is not available or not supported.

        Args:
            file_name: The filename of the file.
            declared_type: Optional declared MIME type from the upload.

        Returns:
            Tuple of (MIME type, category) for the file.

        Raises:
            UnknownFiletypeException: If file type cannot be determined
                or is not in the supported types list.

        """
        if declared_type and declared_type in FILE_TYPE_TO_CATEGORY:
            return declared_type, FILE_TYPE_TO_CATEGORY[declared_type]
        guessed_type, _ = mimetypes.guess_type(file_name)
        if guessed_type and guessed_type in FILE_TYPE_TO_CATEGORY:
            return guessed_type, FILE_TYPE_TO_CATEGORY[guessed_type]
        raise UnknownFiletypeException

    @staticmethod
    def validate_file_size(size: int, file_type: str) -> None:
        """Validate file size against maximum allowed size for the file type.

        Args:
            size: File size in bytes.
            file_type: MIME type of the file.

        Raises:
            UnknownFiletypeException: If file type is not supported.
            IncorrectFileSizeException: If file size exceeds the maximum
                allowed size for the file type.

        """
        max_file_size = MAX_FILE_SIZES.get(file_type)
        if not max_file_size:
            raise UnknownFiletypeException
        if not 0 <= size <= max_file_size:
            raise IncorrectFileSizeException

    @staticmethod
    def get_category_prefix(category: str) -> str:
        """Get storage prefix for a file category.

        Args:
            category: File category name (e.g., 'drawings', 'images').

        Returns:
            Category name as storage prefix.

        Raises:
            UnknownFiletypeException: If category is not supported.

        """
        if category not in SUPPORTED_FILE_TYPES:
            raise UnknownFiletypeException
        return category
