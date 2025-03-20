from pydantic import BaseModel
from schemas.mixins import IdMixin


class UserSchema(BaseModel):
    login: str
    password: str
    first_name: str | None = None
    last_name: str | None = None
    email: str | None = None


class CreateUserSchema(UserSchema):
    pass


class GetUserSchema(IdMixin, UserSchema):
    pass
