"""Constants for file validation and processing."""

# Size constants
KB = 1024  # Kilobyte size constant(1024 byes)
MB = 1024 * KB  # Megabyte size constant(1024 KB)
MAX_FILE_SIZE = 10 * MB  # Max file size from API (10MB for medical documents)
MAX_AVATAR_SIZE = 5 * MB  # 5MB
ALLOWED_EXTENSIONS = {'.pdf', '.doc', '.docx', '.xls', '.xlsx'}
MIME_TYPES: dict[str, str] = {
    '.pdf': 'application/pdf',
    '.doc': 'application/msword',
    '.docx': 'application/vnd.openxmlformats-officedocument.'
    'wordprocessingml.document',
    '.xls': 'application/vnd.ms-excel',
    '.xlsx': 'application/vnd.openxmlformats-officedocument.'
    'spreadsheetml.sheet',
}
SUPPORTED_MIME_TYPES = set(
    MIME_TYPES.values()
)  # Supported MIME types (for validation)
# Maximum file sizes by MIME type
MAX_FILE_SIZES: dict[str, int] = dict.fromkeys(
    SUPPORTED_MIME_TYPES, MAX_FILE_SIZE
)

# File category (for S3 organization)
DOCUMENTS = 'documents'

SUPPORTED_FILE_TYPES: dict[str, list[str]] = {
    DOCUMENTS: list(SUPPORTED_MIME_TYPES),
}

FILE_TYPE_TO_CATEGORY: dict[str, str] = dict.fromkeys(
    SUPPORTED_MIME_TYPES, DOCUMENTS
)

# Reverse mapping: MIME type to file extension
MIME_TO_EXTENSION: dict[str, str] = {
    mime_type: extension for extension, mime_type in MIME_TYPES.items()
}
# <---------------->
# Keys for S3
INSPECTOR_LICENSE_PREFIX: str = 'inspectors/licenses'

# <---------------->