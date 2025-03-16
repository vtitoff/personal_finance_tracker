from pydantic import BaseModel
from schemas.mixins import IdMixin


class PaymentCategory(BaseModel):
    name: str
    description: str


class CreatePaymentCategorySchema(PaymentCategory):
    pass


class GetPaymentCategorySchema(PaymentCategory, IdMixin):
    pass
