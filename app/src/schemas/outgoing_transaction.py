from pydantic import BaseModel
from schemas.mixins import IdMixin


class OutgoingTransaction(BaseModel):
    amount: str
    description: str
    category_id: str
    wallet_id: str
    user_id: str


class CreateOutgoingTransactionSchema(IdMixin, OutgoingTransaction):
    pass


class GetOutgoingTransactionSchema(IdMixin, OutgoingTransaction):
    class Config:
        from_attributes = True


class UpdateOutgoingTransactionSchema(OutgoingTransaction):
    pass
