from datetime import datetime
from typing import Optional

from sqlalchemy import select, delete
from sqlalchemy.exc import IntegrityError

from src.exceptions import UniqueConstraintViolationException, NotNullConstraintViolationException
from src.models import RefreshToken
from src.models.user import User
from src.utils.database_manager import Database
from src.utils.logger import Logger


class RefreshTokenRepository:
    def __init__(self, database: Database, log: Logger):
        self.database = database
        self.log = log

    async def create_token(self, token: RefreshToken) -> RefreshToken:
        async with self.database.session_factory() as session:
            try:
                session.add(token)
                await session.commit()
                await session.refresh(token)
                self.log.info(f"Saved new token. data={token}")
                return token
            except IntegrityError as e:
                await session.rollback()
                if "unique constraint" in str(e.orig):
                    raise UniqueConstraintViolationException(f"Unique constraint violation: {e.orig}")
                elif "not-null constraint" in str(e.orig):
                    raise NotNullConstraintViolationException(f"Not null constraint violation: {e.orig}")
                raise Exception(f"Unknown exception: {e}")

    async def get_by_id(self, id: int) -> RefreshToken:
        async with self.database.session_factory() as session:
            result = await session.execute(select(RefreshToken).where(RefreshToken.id == id))
            return result.scalars().first()

    async def get_by_user(self, user_id: int) -> RefreshToken:
        async with self.database.session_factory() as session:
            result = await session.execute(select(RefreshToken).where(RefreshToken.user_id == user_id))
            return result.scalars().first()

    async def get_by_token(self, token: str) -> RefreshToken:
        async with self.database.session_factory() as session:
            result = await session.execute(select(RefreshToken).where(RefreshToken.token == token))
            return result.scalars().first()

    async def delete_tokens_by_user(self, user_id: int) -> None:
        async with self.database.session_factory() as session:
            try:
                # Выполняем запрос на удаление токенов по user_id
                result = await session.execute(delete(RefreshToken).where(RefreshToken.user_id == user_id))
                await session.commit()
                self.log.info(f"Deleted tokens for user_id={user_id}. Deleted rows: {result.rowcount}")
            except Exception as e:
                await session.rollback()
                self.log.error(f"Error deleting tokens for user_id={user_id}: {e}")
                raise Exception(f"Failed to delete tokens: {e}")

    async def delete_expired_tokens(self) -> None:
        async with self.database.session_factory() as session:
            try:
                # Получаем текущее время
                current_time = datetime.utcnow()

                # Выполняем запрос на удаление истекших токенов
                result = await session.execute(
                    delete(RefreshToken).where(RefreshToken.expired_at < current_time)
                )
                await session.commit()
                self.log.info(f"Deleted expired tokens. Deleted rows: {result.rowcount}")
            except Exception as e:
                await session.rollback()
                self.log.error(f"Error deleting expired tokens: {e}")
                raise Exception(f"Failed to delete expired tokens: {e}")
