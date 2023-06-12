from typing import List

from fastapi_users import schemas
from pydantic import UUID4, BaseModel

from schemas.files import FileBase


class UserRead(schemas.BaseUser):
    """User read"""
    pass


class UserCreate(schemas.BaseUserCreate):
    """Create user"""
    pass


class UserUpdate(schemas.BaseUserUpdate):
    """Update user"""
    pass


class UserFiles(BaseModel):
    """List of user files"""

    user_id: UUID4
    files: List[FileBase]
