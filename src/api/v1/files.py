from fastapi import APIRouter, Depends, UploadFile
from fastapi import File
from fastapi import Form
from fastapi import status
from starlette.responses import FileResponse

from src.core.utils import check_file_size
from src.dependencies.files import get_file_service
from src.models.users import User
from src.schemas.files import FileBase
from src.schemas.users import UserFiles
from src.services.files import FileService
from src.services.users import current_active_user

files_router = APIRouter(prefix='/files', tags=['Files storage'])


@files_router.get(
    '', response_model=UserFiles, status_code=status.HTTP_200_OK,
    description='Get user files list.'
)
async def user_files(
    file_service: FileService = Depends(get_file_service),
    user: User = Depends(current_active_user)
):
    files = await file_service.get(user_id=user.id)
    return UserFiles(
        user_id=user.id,
        files=[FileBase(**file.__dict__) for file in files]
    )


@files_router.post(
    '/upload', status_code=status.HTTP_201_CREATED, response_model=FileBase,
    description='Upload and updating file on server.'
)
async def upload_file(
    file_service: FileService = Depends(get_file_service),
    user: User = Depends(current_active_user),
    file: UploadFile = File(...),
    path: str = Form(None)
):
    check_file_size(file)
    return await file_service.upload(path, file, user)


@files_router.get(
    '/download',
    description='Download files by id, path or full path with compression'
)
async def download_files(
    file_service: FileService = Depends(get_file_service),
    user: User = Depends(current_active_user),
    file_id: str | None = None, path: str | None = None,
    compression: bool = False
) -> FileResponse:
    return await file_service.download(user, file_id, path, compression)
