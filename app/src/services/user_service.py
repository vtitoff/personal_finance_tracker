from db.postgres import get_postgres_session
from fastapi.params import Depends
from models import Role, User
from schemas.user import CreateUserSchema
from services.exceptions import (ConflictError, ObjectAlreadyExistsException,
                                 ObjectNotFoundError)
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession


class UserService:
    def __init__(self, postgres_session: AsyncSession):
        self.postgres_session = postgres_session

    async def create_user(self, user_data: CreateUserSchema) -> User:
        user = User(
            login=user_data.login,
            password=user_data.password,
            first_name=user_data.first_name,
            last_name=user_data.last_name,
        )
        async with self.postgres_session() as session:
            try:
                session.add(user)
                await session.commit()
                session.refresh(user)
                return user
            except IntegrityError as e:
                raise ObjectAlreadyExistsException()

    async def get_user_by_id(self, user_id: str) -> User:
        async with self.postgres_session() as session:
            stmt = await session.scalars(select(User).filter_by(id=user_id))

            user = stmt.first()

            if user is None:
                raise ObjectNotFoundError("User not found!")

            return user

    async def get_user_by_login(self, user_login: str) -> User:
        async with self.postgres_session() as session:
            stmt = await session.scalars(select(User).filter_by(login=user_login))

            user = stmt.first()

            if user is None:
                raise ObjectNotFoundError("User not found!")

            return user

    async def update_user(self, user_id: str, user_data: CreateUserSchema) -> User:
        async with self.postgres_session() as session:
            stmt = await session.scalars(select(User).filter_by(id=user_id))

            user = stmt.first()

            if user is None:
                raise ObjectNotFoundError("User not found!")

            for field in user_data.model_fields_set:
                field_value = getattr(user_data, field)
                setattr(user, field, field_value)
            try:
                await session.commit()
            except IntegrityError:
                raise ConflictError("ConflictError")
            return user

    async def delete_user(self, user_id: str):
        async with self.postgres_session() as session:
            stmt = await session.scalars(select(User).filter_by(id=user_id))
            user = stmt.first()

            if user is None:
                raise ObjectNotFoundError("User not found!")

            await session.delete(user)
            await session.commit()


def get_user_service(
    postgres_session: AsyncSession = Depends(get_postgres_session),
) -> UserService:
    return UserService(postgres_session=postgres_session)
