import uuid
from datetime import datetime, timezone

from models import Base, CurrencyEnum
from sqlalchemy import BigInteger, ForeignKey, Text, func
from sqlalchemy.dialects.postgresql import ENUM, TIMESTAMP
from sqlalchemy.dialects.postgresql import UUID as PgUUID
from sqlalchemy.orm import Mapped, mapped_column, validates


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
        PgUUID, ForeignKey("paymentcategory.id", ondelete="SET NULL")
    )
    payment_method_id: Mapped[uuid.UUID] = mapped_column(
        PgUUID, ForeignKey("paymentmethod.id", ondelete="SET NULL")
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
