import datetime
import logging
from logging import config as logging_config

from fastapi import APIRouter, Depends
from fastapi import status
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.logger import LOGGING
from src.db.db import get_session

logging_config.dictConfig(LOGGING)
logger = logging.getLogger(__name__)
ping_router = APIRouter()


@ping_router.get(
    '/ping', status_code=status.HTTP_200_OK,
    tags=['Services ping'],
    description='Return services access time.'
)
async def ping(db: AsyncSession = Depends(get_session)):
    """Get services access time"""

    statement = text("""SELECT 1""")
    start = datetime.datetime.now()
    await db.execute(statement)
    logger.info('Get db access time')
    return {'database': datetime.datetime.now() - start}
