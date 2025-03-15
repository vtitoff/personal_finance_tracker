from functools import lru_cache

from fastapi import Depends
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from db.postgres import get_postgres_session
from models.models import PaymentCategory
from schemas.payment_category import CreatePaymentCategorySchema
from services.exceptions import ObjectAlreadyExistsException


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


@lru_cache()
def get_category_service(
    postgres_session: AsyncSession = Depends(get_postgres_session),
) -> CategoryService:
    return CategoryService(postgres_session)
