from typing import Optional, List

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError

from src.exceptions import UniqueConstraintViolationException, NotNullConstraintViolationException, \
    ForeignKeyViolationException
from src.models import Lesson
from src.utils.database_manager import Database
from src.utils.logger import Logger


class LessonRepository:
    def __init__(self, database: Database, log: Logger):
        self.database = database
        self.log = log

    async def create(self, lesson: Lesson) -> Lesson:
        async with self.database.session_factory() as session:
            try:
                session.add(lesson)
                await session.commit()
                await session.refresh(lesson)
                self.log.info(f"Saved new lesson. data={lesson}")
                return lesson
            except IntegrityError as e:
                await session.rollback()
                if "unique constraint" in str(e.orig):
                    raise UniqueConstraintViolationException(f"Unique constraint violation: {e.orig}")
                elif "not-null constraint" in str(e.orig):
                    raise NotNullConstraintViolationException(f"Not null constraint violation: {e.orig}")
                elif "ForeignKeyViolationError" in str(e.orig):
                    raise ForeignKeyViolationException("На найдена свзязь при попытке создания объекта")
                raise Exception(f"Unknown exception: {e}")

    async def create_all(self, lessons: list[Lesson]) -> None:
        async with self.database.session_factory() as session:
            try:
                session.add_all(lessons)
                await session.commit()
                self.log.info(f"Saved new lesson. data={lessons}")
            except IntegrityError as e:
                await session.rollback()
                if "unique constraint" in str(e.orig):
                    raise UniqueConstraintViolationException(f"Unique constraint violation: {e.orig}")
                elif "not-null constraint" in str(e.orig):
                    raise NotNullConstraintViolationException(f"Not null constraint violation: {e.orig}")
                elif "ForeignKeyViolationError" in str(e.orig):
                    raise ForeignKeyViolationException("На найдена свзязь при попытке создания объекта")
                raise Exception(f"Unknown exception: {e}")

    async def get_by_id(self, id: int) -> Optional[Lesson]:
        async with self.database.session_factory() as session:
            result = await session.execute(select(Lesson).where(Lesson.id == id))
            res = result.scalars().first()
            await session.close()
            return res

    async def get_by_name(self, name: str) -> Optional[Lesson]:
        async with self.database.session_factory() as session:
            result = await session.execute(select(Lesson).where(Lesson.name == name))
            return result.scalars().first()

    async def get_by_name_like(self, name: str) -> List[Lesson]:
        async with self.database.session_factory() as session:
            result = await session.execute(select(Lesson).where(Lesson.name.like(f'%{name}%')))
            return result.scalars().unique().all()

    async def get_all(self) -> List[Lesson]:
        async with self.database.session_factory() as session:
            result = await session.execute(select(Lesson).distinct())
            return result.scalars().unique().all()
