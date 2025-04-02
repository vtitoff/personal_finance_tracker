from models import CurrencyEnum
from pydantic import BaseModel
from schemas.mixins import IdMixin, UserIdMixin


class Wallet(BaseModel):
    name: str
    description: str | None = None
    amount: int
    currency: CurrencyEnum


class CreateWalletSchema(UserIdMixin, Wallet):
    pass


class GetWalletSchema(IdMixin, UserIdMixin, Wallet):
    class Config:
        from_attributes = True


class UpdateWalletSchema(Wallet):
    pass
