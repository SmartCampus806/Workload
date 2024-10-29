from typing import Optional, List

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import joinedload

from src.exceptions import UniqueConstraintViolationException, NotNullConstraintViolationException, \
    ForeignKeyViolationException
from src.models import Groups
from src.utils.database_manager import Database
from src.utils.logger import Logger


class GroupRepository:
    def __init__(self, database: Database, log: Logger):
        self.database = database
        self.log = log

    async def create(self, group: Groups) -> Groups:
        async with self.database.session_factory() as session:
            try:
                session.add(group)
                await session.commit()
                await session.refresh(group)
                self.log.info(f"Saved new group. data={group}")
                return group
            except IntegrityError as e:
                await session.rollback()
                if "unique constraint" in str(e.orig):
                    raise UniqueConstraintViolationException(f"Unique constraint violation: {e.orig}")
                elif "not-null constraint" in str(e.orig):
                    raise NotNullConstraintViolationException(f"Not null constraint violation: {e.orig}")
                elif "ForeignKeyViolationError" in str(e.orig):
                    raise ForeignKeyViolationException("На найдена свзязь при попытке создания объекта")
                raise Exception(f"Unknown exception: {e}")

    async def create_all(self, groups: list[Groups]) -> None:
        async with self.database.session_factory() as session:
            try:
                session.add_all(groups)
                await session.commit()
                self.log.info(f"Saved new group. data={groups}")
            except IntegrityError as e:
                await session.rollback()
                if "unique constraint" in str(e.orig):
                    raise UniqueConstraintViolationException(f"Unique constraint violation: {e.orig}")
                elif "not-null constraint" in str(e.orig):
                    raise NotNullConstraintViolationException(f"Not null constraint violation: {e.orig}")
                elif "ForeignKeyViolationError" in str(e.orig):
                    raise ForeignKeyViolationException("На найдена свзязь при попытке создания объекта")
                raise Exception(f"Unknown exception: {e}")

    async def get_by_id(self, id: int) -> Optional[Groups]:
        async with self.database.session_factory() as session:
            result = await session.execute(select(Groups).where(Groups.id == id))
            res = result.scalars().first()
            await session.close()
            return res

    async def get_by_name(self, name: str) -> Optional[Groups]:
        async with self.database.session_factory() as session:
            result = await session.execute(select(Groups).where(Groups.name == name))
            return result.scalars().first()

    async def get_by_name_like(self, name: str) -> List[Groups]:
        async with self.database.session_factory() as session:
            result = await session.execute(select(Groups).where(Groups.name.like(f'%{name}%')))
            return result.scalars().unique().all()

    async def get_all(self) -> List[Groups]:
        async with self.database.session_factory() as session:
            result = await session.execute(select(Groups).distinct())
            return result.scalars().unique().all()
