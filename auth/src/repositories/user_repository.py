from typing import Optional

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError

from src.dtos import UserCreate, UserDto
from src.exceptions import UniqueConstraintViolationException, NotNullConstraintViolationException
from src.models.user import User
from src.utils.database_manager import Database
from src.utils.logger import Logger


class UserRepository:
    def __init__(self,database: Database, log: Logger):
        self.database = database
        self.log = log

    async def create_user(self, user: User) -> User:
        async with self.database.session_factory() as session:
            try:
                session.add(user)
                await session.commit()
                await session.refresh(user)
                self.log.info(f"Saved new user. data={user}")
                return user
            except IntegrityError as e:
                await session.rollback()
                if "unique constraint" in str(e.orig):
                    raise UniqueConstraintViolationException(f"Unique constraint violation: {e.orig}")
                elif "not-null constraint" in str(e.orig):
                    raise NotNullConstraintViolationException(f"Not null constraint violation: {e.orig}")
                raise Exception(f"Unknown exception: {e}")

    async def get_by_id(self, id: int) -> Optional[User]:
        async with self.database.session_factory() as session:
            result = await session.execute(select(User).where(User.id == id))
            return result.scalars().first()

    async def get_by_email(self, email: str) -> Optional[User]:
        async with self.database.session_factory() as session:
            result = await session.execute(select(User).where(User.email == email))
            return result.scalars().first()
