from pydantic import BaseModel
from schemas.mixins import IdMixin


class PaymentCategory(BaseModel):
    name: str
    description: str | None = None


class CreatePaymentCategorySchema(PaymentCategory):
    pass


class GetPaymentCategorySchema(PaymentCategory, IdMixin):
    class Config:
        from_attributes = True
