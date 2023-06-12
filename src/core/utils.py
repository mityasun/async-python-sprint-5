from fastapi import HTTPException
from fastapi import status

from core.config import app_settings


def check_file_size(file):
    """Check maximum file size"""

    file.file.seek(0, 2)
    if file.file.tell() > app_settings.max_file_size:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f'File size cannot exceed {app_settings.max_file_size} byte'
        )
    file.file.seek(0)
