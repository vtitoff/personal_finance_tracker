from abc import ABC, abstractmethod

from db.postgres import get_postgres_session
from fastapi import Depends
from models import IncomingTransaction, OutgoingTransaction, Wallet
from schemas.incoming_transaction import (CreateIncomingTransactionSchema,
                                          UpdateIncomingTransactionSchema)
from schemas.outgoing_transaction import (CreateOutgoingTransactionSchema,
                                          UpdateOutgoingTransactionSchema)
from services.exceptions import ConflictError, ObjectNotFoundError
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession


class AbstractTransactionService(ABC):
    @abstractmethod
    async def create_transaction(self, data):
        pass

    @abstractmethod
    async def update_transaction(self, transaction_id, data):
        pass

    @abstractmethod
    async def delete_transaction(self, transaction_id):
        pass

    @abstractmethod
    async def get_transaction_by_id(self, transaction_id):
        pass

    @abstractmethod
    async def get_user_transactions(self, user_id):
        pass


class OutgoingTransactionService(AbstractTransactionService):
    def __init__(self, postgres_session: AsyncSession):
        self.postgres_session = postgres_session

    async def create_transaction(self, data: CreateOutgoingTransactionSchema):
        transaction = OutgoingTransaction(
            amount=data.amount,
            description=data.description,
            category_id=data.category_id,
            wallet_id=data.wallet_id,
            user_id=data.user_id,
        )
        if data.date:
            transaction.date = data.date

        async with self.postgres_session() as session:
            async with session.begin():
                stmt = await session.scalars(
                    select(Wallet).filter_by(id=transaction.wallet_id)
                )
                wallet = stmt.first()
                if wallet is None:
                    raise ObjectNotFoundError("Wallet not found!")
                wallet.amount -= transaction.amount
                session.add(transaction)
            return transaction

    async def update_transaction(
        self, transaction_id, data: UpdateOutgoingTransactionSchema
    ):
        async with self.postgres_session() as session:
            stmt = await session.scalars(
                select(OutgoingTransaction).filter_by(id=transaction_id)
            )

            transaction = stmt.first()

            if transaction is None:
                raise ObjectNotFoundError("Transaction not found!")

            for field in data.model_fields_set:
                field_value = getattr(data, field)
                setattr(transaction, field, field_value)
            try:
                await session.commit()
            except IntegrityError:
                raise ConflictError("ConflictError")
            return transaction

    async def delete_transaction(self, transaction_id: str):
        async with self.postgres_session() as session:
            stmt = await session.scalars(
                select(OutgoingTransaction).filter_by(id=transaction_id)
            )
            transaction = stmt.first()

            if transaction is None:
                raise ObjectNotFoundError("Transaction not found!")

            await session.delete(transaction)
            await session.commit()

    async def get_transaction_by_id(self, transaction_id: str):
        async with self.postgres_session() as session:
            stmt = await session.scalars(
                select(OutgoingTransaction).filter_by(id=transaction_id)
            )

            transaction = stmt.first()

            if transaction is None:
                raise ObjectNotFoundError("Transaction not found!")

            return transaction

    async def get_user_transactions(self, user_id: str):
        async with self.postgres_session() as session:
            stmt = await session.scalars(
                select(OutgoingTransaction).filter_by(user_id=user_id)
            )
            transactions = stmt.all()

            if transactions is None:
                raise ObjectNotFoundError("Transactions not found!")

            return transactions


class IncomingTransactionService(AbstractTransactionService):
    def __init__(self, postgres_session: AsyncSession):
        self.postgres_session = postgres_session

    async def create_transaction(self, data: CreateIncomingTransactionSchema):
        transaction = IncomingTransaction(
            amount=data.amount,
            description=data.description,
            category_id=data.category_id,
            wallet_id=data.wallet_id,
            user_id=data.user_id,
        )

        if data.date:
            transaction.date = data.date

        async with self.postgres_session() as session:
            async with session.begin():
                stmt = await session.scalars(
                    select(Wallet).filter_by(id=transaction.wallet_id)
                )
                wallet = stmt.first()
                if wallet is None:
                    raise ObjectNotFoundError("Wallet not found!")
                wallet.amount += transaction.amount
                session.add(transaction)
            return transaction

    async def update_transaction(
        self, transaction_id: str, data: UpdateIncomingTransactionSchema
    ):
        async with self.postgres_session() as session:
            stmt = await session.scalars(
                select(IncomingTransaction).filter_by(id=transaction_id)
            )

            transaction = stmt.first()

            if transaction is None:
                raise ObjectNotFoundError("Transaction not found!")

            for field in data.model_fields_set:
                field_value = getattr(data, field)
                setattr(transaction, field, field_value)
            try:
                await session.commit()
            except IntegrityError:
                raise ConflictError("ConflictError")
            return transaction

    async def delete_transaction(self, transaction_id: str):
        async with self.postgres_session() as session:
            stmt = await session.scalars(
                select(IncomingTransaction).filter_by(id=transaction_id)
            )
            transaction = stmt.first()

            if transaction is None:
                raise ObjectNotFoundError("Transaction not found!")

            await session.delete(transaction)
            await session.commit()

    async def get_transaction_by_id(self, transaction_id: str):
        async with self.postgres_session() as session:
            stmt = await session.scalars(
                select(IncomingTransaction).filter_by(id=transaction_id)
            )

            transaction = stmt.first()

            if transaction is None:
                raise ObjectNotFoundError("Transaction not found!")

            return transaction

    async def get_user_transactions(self, user_id: str):
        async with self.postgres_session() as session:
            stmt = await session.scalars(
                select(IncomingTransaction).filter_by(user_id=user_id)
            )
            transactions = stmt.all()

            if transactions is None:
                raise ObjectNotFoundError("Transactions not found!")

            return transactions


def get_outgoing_transaction_service(
    postgres_session: AsyncSession = Depends(get_postgres_session),
) -> OutgoingTransactionService:
    return OutgoingTransactionService(postgres_session)


def get_incoming_transaction_service(
    postgres_session: AsyncSession = Depends(get_postgres_session),
) -> IncomingTransactionService:
    return IncomingTransactionService(postgres_session)
