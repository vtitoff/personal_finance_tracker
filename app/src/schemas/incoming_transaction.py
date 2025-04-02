from pydantic import BaseModel
from schemas.mixins import IdMixin


class IncomingTransaction(BaseModel):
    amount: str
    description: str
    category_id: str
    wallet_id: str
    user_id: str


class CreateIncomingTransactionSchema(IdMixin, IncomingTransaction):
    pass


class GetIncomingTransactionSchema(IdMixin, IncomingTransaction):
    class Config:
        from_attributes = True


class UpdateIncomingTransactionSchema(IncomingTransaction):
    pass
