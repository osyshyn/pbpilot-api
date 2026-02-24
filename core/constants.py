"""Constants for file validation and processing."""

# Size constants
KB = 1024
MB = 1024 * KB

MAX_FILE_SIZE = 10 * MB
MAX_IMAGE_SIZE = 5 * MB

# File categories
DOCUMENTS = 'documents'
IMAGES = 'images'

# MIME types by category
DOCUMENT_MIME_TYPES: dict[str, str] = {
    '.pdf': 'application/pdf',
    '.doc': 'application/msword',
    '.docx': 'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
    '.xls': 'application/vnd.ms-excel',
    '.xlsx': 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
}

IMAGE_MIME_TYPES: dict[str, str] = {
    '.jpg': 'image/jpeg',
    '.jpeg': 'image/jpeg',
    '.png': 'image/png',
    '.webp': 'image/webp',
    '.heic': 'image/heic',
}

MIME_TYPES: dict[str, str] = {
    **DOCUMENT_MIME_TYPES,
    **IMAGE_MIME_TYPES,
}

# Supported MIME type sets
SUPPORTED_DOCUMENT_MIME_TYPES: set[str] = set(DOCUMENT_MIME_TYPES.values())
SUPPORTED_IMAGE_MIME_TYPES: set[str] = set(IMAGE_MIME_TYPES.values())
SUPPORTED_MIME_TYPES: set[str] = SUPPORTED_DOCUMENT_MIME_TYPES | SUPPORTED_IMAGE_MIME_TYPES

# Max sizes per MIME type
MAX_FILE_SIZES: dict[str, int] = {
    **dict.fromkeys(SUPPORTED_DOCUMENT_MIME_TYPES, MAX_FILE_SIZE),
    **dict.fromkeys(SUPPORTED_IMAGE_MIME_TYPES, MAX_IMAGE_SIZE),
}

# File type → category mapping
FILE_TYPE_TO_CATEGORY: dict[str, str] = {
    **dict.fromkeys(SUPPORTED_DOCUMENT_MIME_TYPES, DOCUMENTS),
    **dict.fromkeys(SUPPORTED_IMAGE_MIME_TYPES, IMAGES),
}

# Category → supported MIME types
SUPPORTED_FILE_TYPES: dict[str, list[str]] = {
    DOCUMENTS: list(SUPPORTED_DOCUMENT_MIME_TYPES),
    IMAGES: list(SUPPORTED_IMAGE_MIME_TYPES),
}

# Reverse mapping: MIME type → extension
MIME_TO_EXTENSION: dict[str, str] = {
    mime_type: extension for extension, mime_type in MIME_TYPES.items()
}

# S3 prefixes
INSPECTOR_LICENSE_PREFIX: str = 'inspectors/licenses'
INSPECTOR_AVATAR_PREFIX: str = 'inspectors/avatars'