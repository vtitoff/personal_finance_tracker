from datetime import datetime
from uuid import UUID

from pydantic import BaseModel
from schemas.mixins import IdMixin


class IncomingTransaction(BaseModel):
    amount: int
    description: str
    category_id: UUID
    wallet_id: UUID
    user_id: UUID
    date: datetime | None = None


class CreateIncomingTransactionSchema(IncomingTransaction):
    pass


class GetIncomingTransactionSchema(IdMixin, IncomingTransaction):
    class Config:
        from_attributes = True


class UpdateIncomingTransactionSchema(IncomingTransaction):
    pass
