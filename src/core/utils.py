from fastapi import HTTPException
from fastapi import status

from src.core.config import app_settings


def check_file_size(file):
    """Check maximum file size"""

    file.file.seek(0, 2)
    if file.file.tell() > app_settings.max_file_size:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail=f'File size cannot exceed {app_settings.max_file_size} byte'
        )
    file.file.seek(0)
