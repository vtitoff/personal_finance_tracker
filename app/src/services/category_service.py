from abc import ABC, abstractmethod

from db.postgres import get_postgres_session
from fastapi import Depends
from models import IncomingCategory, OutgoingCategory
from schemas.incoming_category import CreateIncomingCategorySchema
from schemas.outgoing_category import CreateOutgoingCategorySchema
from services.exceptions import (ConflictError, ObjectAlreadyExistsException,
                                 ObjectNotFoundError)
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession


class AbstractCategoryService(ABC):
    @abstractmethod
    async def create_category(self, data):
        pass

    @abstractmethod
    async def get_all_categories(self):
        pass

    @abstractmethod
    async def get_category_by_id(self, category_id):
        pass

    @abstractmethod
    async def update_category(self, category_id, data):
        pass

    @abstractmethod
    async def delete_category(self, category_id):
        pass


class OutgoingCategoryService(AbstractCategoryService):
    def __init__(self, postgres_session: AsyncSession):
        self.postgres_session = postgres_session

    async def create_category(self, data: CreateOutgoingCategorySchema):
        payment_category = OutgoingCategory(
            name=data.name,
            description=data.description,
        )

        async with self.postgres_session() as session:
            try:
                session.add(payment_category)
                await session.commit()
                await session.refresh(payment_category)
                return payment_category
            except IntegrityError:
                raise ObjectAlreadyExistsException

    async def get_all_categories(self):
        async with self.postgres_session() as session:
            stmt = await session.scalars(select(OutgoingCategory))
            return stmt.all()

    async def get_category_by_id(self, category_id: str):
        async with self.postgres_session() as session:
            stmt = await session.scalars(
                select(OutgoingCategory).filter_by(id=category_id)
            )

            category = stmt.first()

            if category is None:
                raise ObjectNotFoundError("Category not found")

            return category

    async def update_category(
        self, category_id: str, data: CreateOutgoingCategorySchema
    ):
        async with self.postgres_session() as session:
            stmt = await session.scalars(
                select(OutgoingCategory).filter_by(id=category_id)
            )

            category = stmt.first()

            if category is None:
                raise ObjectNotFoundError("Category not found")

            for field in data.model_fields_set:
                field_value = getattr(data, field)
                setattr(category, field, field_value)
            try:
                await session.commit()
            except IntegrityError:
                raise ConflictError("ConflictError")
            return category

    async def delete_category(self, category_id: str):
        async with self.postgres_session() as session:
            stmt = await session.scalars(
                select(OutgoingCategory).filter_by(id=category_id)
            )
            category = stmt.first()

            if category is None:
                raise ObjectNotFoundError("Category not found")

            await session.delete(category)
            await session.commit()


class IncomingCategoryService(AbstractCategoryService):
    def __init__(self, postgres_session: AsyncSession):
        self.postgres_session = postgres_session

    async def create_category(self, data: CreateIncomingCategorySchema):
        category = IncomingCategory(
            name=data.name,
            description=data.description,
        )

        async with self.postgres_session() as session:
            try:
                session.add(category)
                await session.commit()
                await session.refresh(category)
                return category
            except IntegrityError:
                raise ObjectAlreadyExistsException

    async def get_all_categories(self):
        async with self.postgres_session() as session:
            stmt = await session.scalars(select(IncomingCategory))
            return stmt.all()

    async def get_category_by_id(self, category_id: str):
        async with self.postgres_session() as session:
            stmt = await session.scalars(
                select(IncomingCategory).filter_by(id=category_id)
            )

            category = stmt.first()

            if category is None:
                raise ObjectNotFoundError("Category not found")

            return category

    async def update_category(
        self, category_id: str, data: CreateIncomingCategorySchema
    ):
        async with self.postgres_session() as session:
            stmt = await session.scalars(
                select(IncomingCategory).filter_by(id=category_id)
            )

            category = stmt.first()

            if category is None:
                raise ObjectNotFoundError("Category not found")

            for field in data.model_fields_set:
                field_value = getattr(data, field)
                setattr(category, field, field_value)
            try:
                await session.commit()
            except IntegrityError:
                raise ConflictError("ConflictError")
            return category

    async def delete_category(self, category_id: str):
        async with self.postgres_session() as session:
            stmt = await session.scalars(
                select(IncomingCategory).filter_by(id=category_id)
            )
            category = stmt.first()

            if category is None:
                raise ObjectNotFoundError("Category not found")

            await session.delete(category)
            await session.commit()


def get_outgoing_category_service(
    postgres_session: AsyncSession = Depends(get_postgres_session),
) -> OutgoingCategoryService:
    return OutgoingCategoryService(postgres_session)


def get_incoming_category_service(
    postgres_session: AsyncSession = Depends(get_postgres_session),
) -> IncomingCategoryService:
    return IncomingCategoryService(postgres_session)
