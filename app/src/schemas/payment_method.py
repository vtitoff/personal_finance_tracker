from models import CurrencyEnum
from pydantic import BaseModel
from schemas.mixins import IdMixin, UserIdMixin


class PaymentMethod(BaseModel):
    name: str
    description: str | None = None
    amount: int
    currency: CurrencyEnum


class CreatePaymentMethodSchema(PaymentMethod, UserIdMixin):
    pass


class GetPaymentMethodSchema(PaymentMethod, IdMixin, UserIdMixin):
    class Config:
        from_attributes = True


class UpdatePaymentMethodSchema(PaymentMethod):
    pass
