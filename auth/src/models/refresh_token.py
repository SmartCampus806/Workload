from datetime import datetime

from sqlalchemy import String, Integer, DateTime
from sqlalchemy.orm import Mapped, mapped_column, DeclarativeBase

from .Base import Base


class RefreshToken(Base):
    __tablename__ = 'refresh_tokens'

    token: Mapped[str] = mapped_column(String, unique=True, nullable=False)
    user_id: Mapped[int] = mapped_column(Integer, nullable=False)  # Идентификатор пользователя
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    expired_at: Mapped[datetime] = mapped_column(DateTime) # Время истечения токена