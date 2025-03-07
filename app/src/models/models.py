import enum
import uuid
from datetime import datetime, timezone
from typing import List

from sqlalchemy import BigInteger, ForeignKey, String, Text, func
from sqlalchemy.dialects.postgresql import ENUM, TIMESTAMP
from sqlalchemy.dialects.postgresql import UUID as PgUUID
from sqlalchemy.ext.declarative import declared_attr
from sqlalchemy.orm import (DeclarativeBase, Mapped, mapped_column,
                            relationship, validates)
from werkzeug.security import check_password_hash, generate_password_hash

from models.sqlalchemy_utils.email import EmailType


class CurrencyEnum(enum.Enum):
    USD = "USD"
    EUR = "EUR"
    RUB = "RUB"
    BYN = "BYN"
    KZT = "KZT"


class Base(DeclarativeBase):
    @declared_attr.directive
    def __tablename__(cls):
        return f"{cls.__name__.lower()}"

    id: Mapped[uuid.UUID] = mapped_column(PgUUID, primary_key=True, default=uuid.uuid4)
    created_at: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True),
        server_default=func.current_timestamp(),
    )
    updated_at: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True),
        server_default=func.current_timestamp(),
        server_onupdate=func.current_timestamp(),
    )


class Payment(Base):
    amount: Mapped[int] = mapped_column(BigInteger)
    currency: Mapped[CurrencyEnum] = mapped_column(
        ENUM(
            CurrencyEnum,
            values_callable=lambda obj: [e.value for e in obj],
            name="currency",
        ),
        default=CurrencyEnum.RUB.value,
    )
    description: Mapped[str] = mapped_column(Text, nullable=True)
    date: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True), server_default=func.current_timestamp()
    )
    category_id: Mapped[uuid.UUID] = mapped_column(
        PgUUID, ForeignKey("paymentcategory.id")
    )
    category: Mapped[List["PaymentCategory"]] = relationship(
        back_populates="paymentcategories"
    )
    payment_method_id: Mapped[uuid.UUID] = mapped_column(
        PgUUID, ForeignKey("paymentmethod.id")
    )
    payment_method: Mapped[List["PaymentMethod"]] = relationship(
        back_populates="paymentmethods"
    )

    @validates("date")
    def validate_date(self, key, value):
        if value.tzinfo is None:
            raise ValueError("Date must contain time zone.")

        utc_time = value.astimezone(timezone.utc)
        current_utc = datetime.now(timezone.utc)

        if utc_time > current_utc.now(timezone.utc):
            raise ValueError("Date cannot be less than current date.")
        return value

    @validates("amount")
    def validate_amount(self, key, amount):
        if amount <= 0:
            raise ValueError("Amount must be a positive number.")
        return amount


class PaymentCategory(Base):
    name: Mapped[str] = mapped_column(String)
    description: Mapped[str] = mapped_column(Text, nullable=True)


class PaymentMethod(Base):
    name: Mapped[str] = mapped_column(String)
    description: Mapped[str] = mapped_column(Text, nullable=True)
    amount: Mapped[int] = mapped_column(BigInteger)
    currency: Mapped[CurrencyEnum] = mapped_column(
        ENUM(
            CurrencyEnum,
            values_callable=lambda obj: [e.value for e in obj],
            name="currency",
        )
    )


class User(Base):
    login: Mapped[str] = mapped_column(String, nullable=False, unique=True)
    password: Mapped[str] = mapped_column(String, nullable=False)
    first_name: Mapped[str] = mapped_column(String, nullable=True)
    last_name: Mapped[str] = mapped_column(String, nullable=True)
    email: Mapped[str] = mapped_column(EmailType)

    def __init__(
        self, login: str, password: str, first_name: str, last_name: str
    ) -> None:
        self.login = login
        self.password = generate_password_hash(password)
        self.first_name = first_name
        self.last_name = last_name

    def check_password(self, password: str) -> bool:
        return check_password_hash(self.password, password)

    def __repr__(self) -> str:
        return f"<User {self.login}>"
