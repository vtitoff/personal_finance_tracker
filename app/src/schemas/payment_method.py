from models import CurrencyEnum
from pydantic import BaseModel
from schemas.mixins import IdMixin, UserIdMixin


class PaymentMethod(BaseModel):
    name: str
    description: str
    amount: int
    currency: CurrencyEnum


class CreatePaymentMethodSchema(PaymentMethod, UserIdMixin):
    pass


class GetPaymentMethodSchema(PaymentMethod, IdMixin, UserIdMixin):
    pass


class UpdatePaymentMethodSchema(PaymentMethod):
    pass
