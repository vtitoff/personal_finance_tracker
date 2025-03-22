import uuid
from datetime import datetime

from models import Base
from sqlalchemy import DateTime, ForeignKey, String
from sqlalchemy.dialects.postgresql import UUID as PgUUID
from sqlalchemy.orm import Mapped, mapped_column, relationship


class RefreshToken(Base):
    user_id: Mapped[uuid.UUID] = mapped_column(
        PgUUID, ForeignKey("user.id"), nullable=False
    )
    token: Mapped[str] = mapped_column(String(255), nullable=False)
    expires_at: Mapped[datetime] = mapped_column(DateTime, nullable=False)

    def __repr__(self) -> str:
        return f"<RefreshToken {self.token} for User {self.user_id}>"
