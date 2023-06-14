import datetime
from typing import Any, Dict, Type, TypeVar

from fastapi.encoders import jsonable_encoder
from pydantic import BaseModel
from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from src.db.db import Base

ModelType = TypeVar("ModelType", bound=Base)
SchemaType = TypeVar("SchemaType", bound=BaseModel)
CreateSchemaType = TypeVar("CreateSchemaType", bound=BaseModel)
UpdateSchemaType = TypeVar("UpdateSchemaType", bound=BaseModel)


class BaseService:
    def __init__(self, db: AsyncSession, model: Type[ModelType] | None = None):
        self.db = db
        self.model = model

    async def get(
            self, is_one: bool = False, **kwargs: Dict[str, Any]
    ) -> Type[ModelType] | None:
        """Get one or several objects."""

        statement = select(self.model).where(
            *[getattr(
                self.model, key
            ) == value for key, value in kwargs.items()]
        )
        result = await self.db.execute(statement=statement)
        if is_one:
            return result.scalar_one_or_none()
        return result.scalars().all()

    async def create(self, *, obj_in: CreateSchemaType) -> ModelType:
        obj_in_data = jsonable_encoder(
            obj_in, custom_encoder={datetime.datetime: lambda date: date}
        )
        """Create object"""

        db_obj = self.model(**obj_in_data)
        self.db.add(db_obj)
        await self.db.commit()
        await self.db.refresh(db_obj)
        return db_obj

    async def update(
            self, *, db_obj: Type[ModelType],
            obj_in: Type[SchemaType] | Dict[str, Any]
    ) -> Type[ModelType]:
        """Update object"""

        statement = (
            update(self.model).where(self.model.id == db_obj.id).
            values(obj_in.dict(exclude_unset=True)).returning(self.model)
        )
        await self.db.execute(statement=statement)
        await self.db.commit()
        return db_obj
