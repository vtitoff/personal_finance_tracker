import uuid

from models import Base, CurrencyEnum
from sqlalchemy import BigInteger, ForeignKey, String, Text
from sqlalchemy.dialects.postgresql import ENUM
from sqlalchemy.dialects.postgresql import UUID as PgUUID
from sqlalchemy.orm import Mapped, mapped_column


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
    user_id: Mapped[uuid.UUID] = mapped_column(PgUUID, ForeignKey("user.id"))
