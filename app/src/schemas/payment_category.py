from schemas.mixins import IdMixin


class PaymentCategorySchema(IdMixin):
    name: str
    description: str
