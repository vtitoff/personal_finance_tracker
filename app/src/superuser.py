import asyncio

import typer
from core.config import settings
from db import postgres
from models import Role, User
from sqlalchemy import select
from sqlalchemy.ext.asyncio import (AsyncSession, async_sessionmaker,
                                    create_async_engine)

app = typer.Typer()


async def create_superuser(login: str, password: str):
    try:
        engine = create_async_engine(
            postgres.dsn, echo=settings.engine_echo, future=True
        )
        async_session = async_sessionmaker(
            bind=engine, expire_on_commit=False, class_=AsyncSession
        )  # type: ignore[assignment]

        async with async_session() as session:
            stmt = await session.scalars(select(Role).filter_by(title="admin"))
            admin_role = stmt.first()
            if admin_role is None:
                admin_role = Role(title="admin")
                session.add(admin_role)
                await session.commit()
            superuser = User(
                login=login, password=password, first_name=None, last_name=None
            )
            superuser.roles.append(admin_role)
            session.add(superuser)
            await session.commit()
    except Exception as e:
        print(e)


@app.command()
def superuser(login: str, password: str):
    asyncio.run(create_superuser(login, password))
    typer.echo("Superuser created successfully.")


if __name__ == "__main__":
    app()
