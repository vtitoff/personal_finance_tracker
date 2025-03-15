from schemas.mixins import IdMixin


class CreatePaymentCategorySchema(IdMixin):
    name: str
    description: str


class GetPaymentCategorySchema(IdMixin):
    name: str
    description: str
