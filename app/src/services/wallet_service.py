from db.postgres import get_postgres_session
from fastapi.params import Depends
from models import Wallet
from schemas.wallet import CreateWalletSchema, UpdateWalletSchema
from services.exceptions import (ConflictError, ObjectAlreadyExistsException,
                                 ObjectNotFoundError)
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession


class WalletService:
    def __init__(self, postgres_session: AsyncSession):
        self.postgres_session = postgres_session

    async def create_wallet(self, wallet_data: CreateWalletSchema):
        wallet = Wallet(
            name=wallet_data.name,
            description=wallet_data.description,
            amount=wallet_data.amount,
            currency=wallet_data.currency,
            user_id=wallet_data.user_id,
        )

        async with self.postgres_session() as session:
            try:
                session.add(wallet)
                await session.commit()
                await session.refresh(wallet)
                return wallet
            except IntegrityError:
                raise ObjectAlreadyExistsException

    async def get_wallet_by_id(self, wallet_id: str):
        async with self.postgres_session() as session:
            stmt = await session.scalars(select(Wallet).filter_by(id=wallet_id))
            wallet = stmt.first()

            if wallet is None:
                raise ObjectNotFoundError("Wallet not found")

            return wallet

    async def get_wallets_by_user_id(self, user_id: str):
        async with self.postgres_session() as session:
            stmt = await session.scalars(select(Wallet).filter_by(user_id=user_id))
            wallets = stmt.all()

            if wallets is None:
                raise ObjectNotFoundError("Wallets not found")

            return wallets

    async def update_wallet(self, wallet_id: str, wallet_data: UpdateWalletSchema):
        async with self.postgres_session() as session:
            stmt = await session.scalars(select(Wallet).filter_by(id=wallet_id))

            wallet = stmt.first()

            if wallet is None:
                raise ObjectNotFoundError("Wallet not found!")

            for field in wallet_data.model_fields_set:
                field_value = getattr(wallet_data, field)
                setattr(wallet, field, field_value)
            try:
                await session.commit()
            except IntegrityError:
                raise ConflictError("Conflict Error")
            return wallet

    async def delete_wallet(self, wallet_id: str):
        async with self.postgres_session() as session:
            stmt = await session.scalars(select(Wallet).filter_by(id=wallet_id))
            wallet = stmt.first()

            if wallet is None:
                raise ObjectNotFoundError("Wallet not found")

            await session.delete(wallet)
            await session.commit()


def get_wallet_service(
    postgres_session: AsyncSession = Depends(get_postgres_session),
):
    return WalletService(postgres_session)
