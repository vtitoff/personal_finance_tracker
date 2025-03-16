from db.postgres import get_postgres_session
from fastapi.params import Depends
from models.models import PaymentMethod
from schemas.payment_method import CreatePaymentMethodSchema
from services.exceptions import (ObjectAlreadyExistsException,
                                 ObjectNotFoundError)
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession


class PaymentMethodService:
    def __init__(self, postgres_session: AsyncSession):
        self.postgres_session = postgres_session

    async def create_payment_method(
        self, payment_method_data: CreatePaymentMethodSchema
    ):
        payment_method = PaymentMethod(
            name=payment_method_data.name,
            description=payment_method_data.description,
            amount=payment_method_data.amount,
            currency=payment_method_data.currency,
            user_id=payment_method_data.user_id,
        )

        async with self.postgres_session() as session:
            try:
                session.add(payment_method)
                await session.commit()
                await session.refresh(payment_method)
                return payment_method
            except IntegrityError:
                raise ObjectAlreadyExistsException


def get_payment_method_service(
    postgres_session: AsyncSession = Depends(get_postgres_session),
):
    return PaymentMethodService(postgres_session)
