from pydantic import BaseModel
from schemas.mixins import IdMixin


class UserSchema(BaseModel):
    login: str
    first_name: str | None = None
    last_name: str | None = None
    email: str | None = None


class CreateUserSchema(UserSchema):
    password: str


class GetUserSchema(IdMixin, UserSchema):
    class Config:
        from_attributes: True
