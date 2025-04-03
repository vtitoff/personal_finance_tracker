from typing import List

from db.postgres import get_postgres_session
from fastapi.params import Depends
from models import Role, User
from schemas.role import CreateRoleSchema, UpdateRoleSchema
from services.exceptions import (ConflictError, ObjectAlreadyExistsException,
                                 ObjectNotFoundError)
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession


class RoleService:
    def __init__(self, postgres_session: AsyncSession):
        self.postgres_session = postgres_session

    async def create_role(self, data: CreateRoleSchema) -> User:
        role = Role(
            title=data.title,
        )
        async with self.postgres_session() as session:
            try:
                session.add(role)
                await session.commit()
                await session.refresh(role)
                return role
            except IntegrityError as e:
                raise ObjectAlreadyExistsException()

    async def get_all_roles(self) -> List[Role]:
        async with self.postgres_session() as session:
            stmt = await session.scalars(select(Role))
            roles = stmt.all()

            if roles is None:
                raise ObjectNotFoundError("Roles not found!")

            return roles

    async def get_role_by_id(self, role_id: str) -> Role:
        async with self.postgres_session() as session:
            stmt = await session.scalars(select(Role).filter_by(id=role_id))

            role = stmt.first()

            if role is None:
                raise ObjectNotFoundError("Role not found!")

            return role

    async def update_role(self, role_id: str, data: UpdateRoleSchema) -> Role:
        async with self.postgres_session() as session:
            stmt = await session.scalars(select(Role).filter_by(id=role_id))

            role = stmt.first()

            if role is None:
                raise ObjectNotFoundError("Role not found!")

            for field in data.model_fields_set:
                field_value = getattr(data, field)
                setattr(role, field, field_value)
            try:
                await session.commit()
            except IntegrityError:
                raise ConflictError("ConflictError")
            return role

    async def delete_role(self, role_id: str):
        async with self.postgres_session() as session:
            stmt = await session.scalars(select(Role).filter_by(id=role_id))
            role = stmt.first()

            if role is None:
                raise ObjectNotFoundError("Role not found!")

            await session.delete(role)
            await session.commit()

    async def get_user_roles(self, user_id: str) -> List[Role]:
        async with self.postgres_session() as session:
            stmt = await session.scalars(select(User).filter_by(id=user_id))
            user = stmt.first()

            if user is None:
                raise ObjectNotFoundError("User not found!")

            return user.roles

    async def assign_role_to_user(self, user_id: str, role_id: str):
        async with self.postgres_session() as session:
            async with session.begin():
                stmt = await session.scalars(select(User).filter_by(id=user_id))
                user = stmt.first()
                if user is None:
                    raise ObjectNotFoundError("User not found!")

                stmt = await session.scalars(select(Role).filter_by(id=role_id))
                role = stmt.first()
                if role is None:
                    raise ObjectNotFoundError("Role not found!")

                if role not in user.roles:
                    user.roles.append(role)
                    await session.commit()

    async def remove_role_from_user(self, user_id: str, role_id: str):
        async with self.postgres_session() as session:
            async with session.begin():
                stmt = await session.scalars(select(User).filter_by(id=user_id))
                user = stmt.first()
                if user is None:
                    raise ObjectNotFoundError("User not found!")

                stmt = await session.scalars(select(Role).filter_by(id=role_id))
                role = stmt.first()
                if role is None:
                    raise ObjectNotFoundError("Role not found!")

                if role in user.roles:
                    user.roles.remove(role)
                    await session.commit()


def get_role_service(
    postgres_session: AsyncSession = Depends(get_postgres_session),
) -> RoleService:
    return RoleService(postgres_session=postgres_session)
