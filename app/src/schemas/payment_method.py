from uuid import UUID

from models.models import CurrencyEnum
from pydantic import BaseModel
from schemas.mixins import IdMixin


class PaymentMethod(BaseModel):
    name: str
    description: str
    amount: int
    currency: CurrencyEnum
    user_id: UUID


class CreatePaymentMethodSchema(PaymentMethod):
    pass


class GetPaymentMethodSchema(PaymentMethod, IdMixin):
    pass
