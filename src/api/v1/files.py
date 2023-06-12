from fastapi import APIRouter, Depends, UploadFile
from fastapi import File
from fastapi import Form
from fastapi import status
from sqlalchemy.ext.asyncio import AsyncSession
from starlette.responses import FileResponse

from core.utils import check_file_size
from models.files import FileModel
from models.users import User
from schemas.files import FileBase
from schemas.users import UserFiles
from services.files import FileService
from services.users import current_active_user
from src.db.db import get_session

files_router = APIRouter(prefix='/files', tags=['Files storage'])


@files_router.get(
    '', response_model=UserFiles, status_code=status.HTTP_200_OK,
    description='Get user files list.'
)
async def user_files(
    db: AsyncSession = Depends(get_session),
    user: User = Depends(current_active_user)
):
    files = await FileService(db, FileModel).get(user_id=user.id)
    return UserFiles(
        user_id=user.id,
        files=[FileBase(**file.__dict__) for file in files]
    )


@files_router.post(
    '/upload', status_code=status.HTTP_201_CREATED, response_model=FileBase,
    description='Upload and updating file on server.'
)
async def upload_file(
    db: AsyncSession = Depends(get_session),
    user: User = Depends(current_active_user),
    file: UploadFile = File(...),
    path: str = Form(None)
):
    check_file_size(file)
    return await FileService(db, FileModel).upload(path, file, user)


@files_router.get(
    '/download',
    description='Download files by id, path or full path with compression'
)
async def download_files(
    db: AsyncSession = Depends(get_session),
    user: User = Depends(current_active_user),
    file_id: str | None = None, path: str | None = None,
    compression: bool = False
) -> FileResponse:

    return await FileService(db, FileModel).download(
        user, file_id, path, compression
    )
