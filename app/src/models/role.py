from models import Base
from sqlalchemy import Column, DateTime, ForeignKey, String, Table, func
from sqlalchemy.dialects.postgresql import UUID as PgUUID
from sqlalchemy.orm import Mapped, mapped_column

user_role = Table(
    "user_role",
    Base.metadata,
    Column("user_id", PgUUID(), ForeignKey("user.id"), primary_key=True),
    Column("role_id", PgUUID(), ForeignKey("role.id"), primary_key=True),
    Column("created_at", DateTime, server_default=func.now()),
)


class Role(Base):
    title: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
