from typing import Optional, List

from asyncpg import ForeignKeyViolationError
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.inspection import inspect

from src.exceptions import UniqueConstraintViolationException, NotNullConstraintViolationException, \
    ForeignKeyViolationException
from src.models import Workload
from src.utils.database_manager import Database
from src.utils.logger import Logger


class WorkloadRepository:
    def __init__(self, database: Database, log: Logger):
        self.database = database
        self.log = log

    async def create(self, workload: Workload) -> Workload:
        async with self.database.session_factory() as session:
            try:
                session.add(workload)
                await session.commit()
                await session.refresh(workload)
                self.log.info(f"Saved new workload. data={workload}")
                return workload
            except IntegrityError as e:
                await session.rollback()
                if "unique constraint" in str(e.orig):
                    raise UniqueConstraintViolationException(f"Unique constraint violation: {e.orig}")
                elif "not-null constraint" in str(e.orig):
                    raise NotNullConstraintViolationException(f"Not null constraint violation: {e.orig}")
                elif "ForeignKeyViolationError" in str(e.orig):
                    raise ForeignKeyViolationException("На найдена свзязь при попытке создания объекта")
                raise Exception(f"Unknown exception: {e}")

    async def create_all(self, workloads: list[Workload]) -> None:
        async with self.database.session_factory() as session:
            try:
                session.add_all(workloads)
                await session.commit()
                self.log.info(f"Saved new workload. data={workloads}")
            except IntegrityError as e:
                await session.rollback()
                if "unique constraint" in str(e.orig):
                    raise UniqueConstraintViolationException(f"Unique constraint violation: {e.orig}")
                elif "not-null constraint" in str(e.orig):
                    raise NotNullConstraintViolationException(f"Not null constraint violation: {e.orig}")
                elif "ForeignKeyViolationError" in str(e.orig):
                    raise ForeignKeyViolationException("На найдена свзязь при попытке создания объекта")
                raise Exception(f"Unknown exception: {e}")


    async def get_by_id(self, id: int) -> Optional[Workload]:
        async with self.database.session_factory() as session:
            result = await session.execute(select(Workload).where(Workload.id == id))
            res = result.scalars().first()
            await session.close()
            return res

    async def get_by_type(self, type: str) -> Optional[Workload]:
        async with self.database.session_factory() as session:
            result = await session.execute(select(Workload).where(Workload.type == type))
            return result.scalars().first()

    async def get_by_employee_id(self, employee_id: int) -> Optional[Workload]:
        async with self.database.session_factory() as session:
            result = await session.execute(select(Workload).where(Workload.employee_id == employee_id))
            return result.scalars().first()

    async def get_by_lesson_id(self, lesson_id: int) -> Optional[Workload]:
        async with self.database.session_factory() as session:
            result = await session.execute(select(Workload).where(Workload.lesson_id == lesson_id))
            return result.scalars().first()

    async def get_all(self) -> List[Workload]:
        async with self.database.session_factory() as session:
            result = await session.execute(select(Workload).distinct())
            return result.scalars().unique().all()
