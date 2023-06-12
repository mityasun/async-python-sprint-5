import io
import logging
import os
import zipfile
from logging import config as logging_config
from pathlib import Path
from typing import Union

import aiofiles
from fastapi import HTTPException
from fastapi import UploadFile
from fastapi import status
from fastapi.responses import FileResponse
from fastapi.responses import StreamingResponse

from core.config import app_settings
from core.logger import LOGGING
from models.users import User
from schemas.files import FileUpload, FileBase
from services.base import BaseService

logging_config.dictConfig(LOGGING)
logger = logging.getLogger(__name__)


class FileService(BaseService):

    async def upload(
            self, path: str | None, file: UploadFile, user: User
    ) -> FileBase:
        """Upload and updating files to server"""

        path = f'{path}/' if path else ''
        file_path = (
            f'{app_settings.file_folder}/{user.id}/{path}{file.filename}'
        )
        existing_file = await self.get(is_one=True, path=file_path)
        if existing_file:
            existing_file.size = len(await file.read())
            await self.db.commit()
            logger.info(f'File {existing_file.id} was updated.')
            await self.upload_update_file(file, file_path)
            logger.info(f'File {existing_file.id} was uploaded.')
            return FileBase(**existing_file.__dict__)

        else:
            file_in_db = await self.create(obj_in=FileUpload(
                name=file.filename, path=file_path,
                size=len(await file.read()), user_id=user.id
            ))
            logger.info(f'File {file_in_db.id} created.')
            await self.upload_update_file(file, file_path)
            logger.info(f'File {file_in_db.id} uploaded.')
            return FileBase(**file_in_db.__dict__)

    @staticmethod
    async def upload_update_file(file, file_path):
        """Upload and updating file on server"""

        file.file.seek(0)
        content = file.file.read()
        p = Path(file_path)
        try:
            if not Path.exists(p.parent):
                Path(p.parent).mkdir(parents=True, exist_ok=True)
                logger.info(f'Create dir: {p} dir.')
            async with aiofiles.open(p, "wb") as f:
                await f.write(content)
                logger.info(f'Write file: {file}.')
        except Exception:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail='File not saved'
            )

    async def download(
            self, user: User, file_id: str | None = None,
            path: str | None = None, compression: bool = False
    ):
        """Download files by id, path or full path with optional compression"""

        if path:
            full_path = Path(app_settings.file_folder) / str(user.id) / path
            if not full_path.exists():
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail='File not found'
                )
            if full_path.is_file():
                return await self.create_file_response(full_path, compression)
            elif full_path.is_dir():
                if compression:
                    return self.create_dir_archive(full_path)
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail='You cant download folder without compression'
                )
        elif file_id:
            try:
                file = await self.get(is_one=True, id=file_id)
                return await self.create_file_response(
                    Path(file.path), compression
                )
            except Exception:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail='File not found'
                )

    async def create_file_response(
            self, full_path, compression: bool
    ) -> Union[FileResponse, StreamingResponse]:
        """Create a file response"""

        if compression:
            return self.create_file_archive(full_path)
        else:
            logger.info(f'Get direct file: {full_path.name}.')
            return FileResponse(
                path=full_path, filename=full_path.name,
                media_type="application/octet-stream"
            )

    @staticmethod
    def create_file_archive(full_path):
        """Create archive for one file"""

        file_dirname, file_basename = os.path.split(full_path)
        zip_filename = file_basename + '.zip'
        zip_data = io.BytesIO()
        with zipfile.ZipFile(
                zip_data, mode="w", compression=zipfile.ZIP_DEFLATED
        ) as z:
            z.write(full_path, arcname=file_basename)
            logger.info(f'Created archive with file: {file_basename}.')
        zip_data.seek(0)
        logger.info(f'Sent archive with file: {file_basename}.')
        return StreamingResponse(
            zip_data, media_type="application/zip",
            headers={
                "Content-Disposition": f"attachment; filename={zip_filename}"
            }
        )

    @staticmethod
    def create_dir_archive(full_path):
        """Create archive for dir"""

        zip_data = io.BytesIO()
        with zipfile.ZipFile(
                zip_data, mode="w", compression=zipfile.ZIP_DEFLATED
        ) as zipf:
            for file in os.listdir(full_path):
                zipf.write(os.path.join(full_path, file), file)
        logger.info(f'Created archive with dir: {full_path}.')
        zip_data.seek(0)
        logger.info(f'Sent archive with dir: {full_path}.')
        return StreamingResponse(
            zip_data, media_type="application/zip",
            headers={
                "Content-Disposition":
                f"attachment; filename={os.path.basename(full_path)}.zip"
            }
        )
