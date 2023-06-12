import uuid
from datetime import datetime

from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Integer, String
from sqlalchemy.dialects.postgresql import UUID

from src.db.db import Base


class FileModel(Base):

    __tablename__ = 'file'
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(100), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    path = Column(String(256), unique=True, nullable=False)
    size = Column(Integer)
    is_downloadable = Column(Boolean, default=True)
    user_id = Column(
        UUID(as_uuid=True), ForeignKey('user.id', ondelete='CASCADE'),
        nullable=False
    )
