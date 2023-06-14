from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.db.db import get_session
from src.models.files import FileModel
from src.services.files import FileService


async def get_file_service(db: AsyncSession = Depends(get_session)):
    return FileService(db, FileModel)
