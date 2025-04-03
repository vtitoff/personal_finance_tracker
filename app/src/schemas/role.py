from pydantic import BaseModel
from schemas.mixins import IdMixin


class Role(BaseModel):
    title: str


class CreateRoleSchema(Role):
    pass


class GetRoleSchema(IdMixin, Role):
    pass


class UpdateRoleSchema(Role):
    pass
