import enum
from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, LargeBinary
from sqlalchemy.orm import relationship, Mapped
from sqlalchemy.orm import mapped_column

from .Base import Base

class UserRole(enum.Enum):
    user = 'USER'
    admin = 'ADMIN'
    load_service = 'LOAD_SERVICE'

class User(Base):
    __tablename__ = 'users'

    email: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    hashed_password: Mapped[LargeBinary] = mapped_column(LargeBinary, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow,
                                                 nullable=False)
    role: Mapped[UserRole] = mapped_column(String(30), default=str(UserRole.load_service.value), nullable=False)

    def __repr__(self):
        return f"<User(id={self.id}, email={self.email}, role={self.role}, created_at={self.created_at}, updated_at={self.updated_at})>"