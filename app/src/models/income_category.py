from models import Base
from sqlalchemy import String, Text
from sqlalchemy.orm import Mapped, mapped_column


class IncomeCategory(Base):
    name: Mapped[str] = mapped_column(String, unique=True)
    description: Mapped[str] = mapped_column(Text, nullable=True)
