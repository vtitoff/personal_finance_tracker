from pydantic import BaseModel
from schemas.mixins import IdMixin


class IncomeCategory(BaseModel):
    name: str
    description: str | None = None


class CreateIncomeCategorySchema(IncomeCategory):
    pass


class GetIncomeCategorySchema(IncomeCategory, IdMixin):
    class Config:
        from_attributes = True
