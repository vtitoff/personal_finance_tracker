from pydantic import BaseModel
from schemas.mixins import IdMixin


class IncomingCategory(BaseModel):
    name: str
    description: str | None = None


class CreateIncomingCategorySchema(IncomingCategory):
    pass


class GetIncomingCategorySchema(IdMixin, IncomingCategory):
    class Config:
        from_attributes = True
