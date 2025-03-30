from abc import ABC, abstractmethod

from db.postgres import get_postgres_session
from fastapi import Depends
from models import IncomeCategory, PaymentCategory
from schemas.income_category import CreateIncomeCategorySchema
from schemas.payment_category import CreatePaymentCategorySchema
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


class PaymentCategoryService(AbstractCategoryService):
    def __init__(self, postgres_session: AsyncSession):
        self.postgres_session = postgres_session

    async def create_category(self, data: CreatePaymentCategorySchema):
        payment_category = PaymentCategory(
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
            stmt = await session.scalars(select(PaymentCategory))
            return stmt.all()

    async def get_category_by_id(self, category_id: str):
        async with self.postgres_session() as session:
            stmt = await session.scalars(
                select(PaymentCategory).filter_by(id=category_id)
            )

            category = stmt.first()

            if category is None:
                raise ObjectNotFoundError("Category not found")

            return category

    async def update_category(
        self, category_id: str, data: CreatePaymentCategorySchema
    ):
        async with self.postgres_session() as session:
            stmt = await session.scalars(
                select(PaymentCategory).filter_by(id=category_id)
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
                select(PaymentCategory).filter_by(id=category_id)
            )
            category = stmt.first()

            if category is None:
                raise ObjectNotFoundError("Category not found")

            await session.delete(category)
            await session.commit()


class IncomeCategoryService(AbstractCategoryService):
    def __init__(self, postgres_session: AsyncSession):
        self.postgres_session = postgres_session

    async def create_category(self, data: CreateIncomeCategorySchema):
        category = IncomeCategory(
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
            stmt = await session.scalars(select(IncomeCategory))
            return stmt.all()

    async def get_category_by_id(self, category_id: str):
        async with self.postgres_session() as session:
            stmt = await session.scalars(
                select(IncomeCategory).filter_by(id=category_id)
            )

            category = stmt.first()

            if category is None:
                raise ObjectNotFoundError("Category not found")

            return category

    async def update_category(self, category_id: str, data: CreateIncomeCategorySchema):
        async with self.postgres_session() as session:
            stmt = await session.scalars(
                select(IncomeCategory).filter_by(id=category_id)
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
                select(IncomeCategory).filter_by(id=category_id)
            )
            category = stmt.first()

            if category is None:
                raise ObjectNotFoundError("Category not found")

            await session.delete(category)
            await session.commit()


def get_payment_category_service(
    postgres_session: AsyncSession = Depends(get_postgres_session),
) -> PaymentCategoryService:
    return PaymentCategoryService(postgres_session)


def get_income_category_service(
    postgres_session: AsyncSession = Depends(get_postgres_session),
) -> IncomeCategoryService:
    return IncomeCategoryService(postgres_session)
