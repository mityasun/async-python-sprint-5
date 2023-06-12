import uuid

from fastapi import Depends
from fastapi_users_db_sqlalchemy import (SQLAlchemyBaseUserTableUUID,
                                         SQLAlchemyUserDatabase)
from fastapi_users_db_sqlalchemy.access_token import (
    SQLAlchemyAccessTokenDatabase, SQLAlchemyBaseAccessTokenTableUUID
)
from sqlalchemy import Column
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import relationship

from src.db.db import Base, get_session


class User(SQLAlchemyBaseUserTableUUID, Base):
    """User model"""

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    files = relationship('FileModel', backref='file')


class AccessToken(SQLAlchemyBaseAccessTokenTableUUID, Base):
    pass


async def get_user_db(session: AsyncSession = Depends(get_session)):
    yield SQLAlchemyUserDatabase(session, User)


async def get_access_token_db(
    session: AsyncSession = Depends(get_session),
):
    yield SQLAlchemyAccessTokenDatabase(session, AccessToken)
