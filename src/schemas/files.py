from datetime import datetime

from pydantic import UUID4, BaseModel


class FileBase(BaseModel):
    """Base file for response"""

    id: UUID4
    name: str
    created_at: datetime
    path: str
    size: int
    is_downloadable: bool


class FileUpload(BaseModel):
    """Upload and update file"""

    name: str
    path: str
    size: int
    user_id: UUID4
