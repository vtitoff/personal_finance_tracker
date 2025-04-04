from datetime import datetime
from uuid import UUID

from pydantic import BaseModel
from schemas.mixins import IdMixin


class OutgoingTransaction(BaseModel):
    amount: int
    description: str
    category_id: UUID
    wallet_id: UUID
    user_id: UUID | None = None
    date: datetime | None = None


class CreateOutgoingTransactionSchema(OutgoingTransaction):
    pass


class GetOutgoingTransactionSchema(IdMixin, OutgoingTransaction):
    class Config:
        from_attributes = True


class UpdateOutgoingTransactionSchema(OutgoingTransaction):
    pass
