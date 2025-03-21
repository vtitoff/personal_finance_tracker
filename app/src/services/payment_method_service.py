from db.postgres import get_postgres_session
from fastapi.params import Depends
from models import PaymentMethod
from schemas.payment_method import (CreatePaymentMethodSchema,
                                    UpdatePaymentMethodSchema)
from services.exceptions import (ConflictError, ObjectAlreadyExistsException,
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

    async def get_payment_method_by_id(self, payment_method_id: str):
        async with self.postgres_session() as session:
            stmt = await session.scalars(
                select(PaymentMethod).filter_by(id=payment_method_id)
            )
            payment_method = stmt.first()

            if payment_method is None:
                raise ObjectNotFoundError("Payment method not found")

            return payment_method

    async def get_payment_methods_by_user_id(self, user_id: str):
        async with self.postgres_session() as session:
            stmt = await session.scalars(
                select(PaymentMethod).filter_by(user_id=user_id)
            )
            payment_methods = stmt.all()

            if payment_methods is None:
                raise ObjectNotFoundError("Payment methods not found")

            return payment_methods

    async def update_payment_method(
        self, payment_method_id: str, payment_method_data: UpdatePaymentMethodSchema
    ):
        async with self.postgres_session() as session:
            stmt = await session.scalars(
                select(PaymentMethod).filter_by(id=payment_method_id)
            )

            payment_method = stmt.first()

            if payment_method is None:
                raise ObjectNotFoundError("Payment method not found!")

            for field in payment_method_data.model_fields_set:
                field_value = getattr(payment_method_data, field)
                setattr(payment_method, field, field_value)
            try:
                await session.commit()
            except IntegrityError:
                raise ConflictError("Conflict Error")
            return payment_method

    async def delete_payment_method(self, payment_method_id: str):
        async with self.postgres_session() as session:
            stmt = await session.scalars(
                select(PaymentMethod).filter_by(id=payment_method_id)
            )
            payment_method = stmt.first()

            if payment_method is None:
                raise ObjectNotFoundError("Payment method not found")

            await session.delete(payment_method)
            await session.commit()


def get_payment_method_service(
    postgres_session: AsyncSession = Depends(get_postgres_session),
):
    return PaymentMethodService(postgres_session)
