from unicodedata import category
from uuid import UUID

from db.postgres import get_postgres_session
from fastapi import Depends
from models.models import PaymentCategory
from schemas.payment_category import CreatePaymentCategorySchema
from services.exceptions import (ObjectAlreadyExistsException,
                                 ObjectNotFoundError)
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession


class CategoryService:
    def __init__(self, postgres_session: AsyncSession):
        self.postgres_session = postgres_session

    async def create_category(self, category_data: CreatePaymentCategorySchema):
        payment_category = PaymentCategory(
            name=category_data.name,
            description=category_data.description,
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
            categories_data = await session.scalars(select(PaymentCategory))
            return categories_data.all()

    async def get_category_by_id(self, category_id: str):
        async with self.postgres_session() as session:
            categories_data = await session.scalars(
                select(PaymentCategory).filter_by(id=category_id)
            )

            category = categories_data.first()

            if category is None:
                raise ObjectNotFoundError("Category not found")

            return category

    async def delete_category(self, category_id: UUID):
        async with self.postgres_session() as session:
            categories_data = await session.scalars(
                select(PaymentCategory).filter_by(id=category_id)
            )
            category = categories_data.first()

            if category is None:
                raise ObjectNotFoundError("Category not found")

            await session.delete(category)
            await session.commit()


def get_category_service(
    postgres_session: AsyncSession = Depends(get_postgres_session),
) -> CategoryService:
    return CategoryService(postgres_session)
