from pydantic import BaseModel
from schemas.mixins import IdMixin


class OutgoingCategory(BaseModel):
    name: str
    description: str | None = None


class CreateOutgoingCategorySchema(OutgoingCategory):
    pass


class GetOutgoingCategorySchema(OutgoingCategory, IdMixin):
    class Config:
        from_attributes = True
