from uuid import UUID

from pydantic import BaseModel


class IdMixin(BaseModel):
    id: UUID


class UserIdMixin(BaseModel):
    user_id: UUID
