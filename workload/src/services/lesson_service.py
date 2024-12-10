from typing import Optional

from sqlalchemy import select

from src.models import Lesson, Employee
from src.utils import Database

from loguru import logger as log


class LessonService:
    def __init__(self, database: Database):
        self.database = database

    async def add_lesson_to_employee(self, lesson_name: str, employee_id: int) -> Employee:
        async with self.database.session_factory() as session:
            lessons = await LessonService._get_lessons_by_name(lesson_name, session)
            employee = await LessonService._get_employee_by_id(employee_id, session)
            if employee is None:
                raise ValueError("employee not found")

            employee.lesson_competences += lessons
            await session.commit()
            log.info(f"add {len(lessons)} lessons with name={lesson_name} "
                     f"to employee with id={employee_id} and name={employee.name}")
            return employee

    async def remove_lesson_to_employee(self, lesson_name: str, employee_id: int) -> Employee:
        async with self.database.session_factory() as session:
            lessons = await LessonService._get_lessons_by_name(lesson_name, session)
            employee = await LessonService._get_employee_by_id(employee_id, session)
            if employee is None:
                raise ValueError("employee not found")

            result_lesson_competences = []
            for lesson in employee.lesson_competences:
                if lesson not in lessons:
                    result_lesson_competences.append(lesson)
            employee.lesson_competences = result_lesson_competences
            await session.commit()

            log.info(f"remove {len(lessons)} lessons with name={lesson_name} "
                     f"from employee with id={employee_id} and name={employee.name}")
            return employee

    async def get_unique_lessons(self) -> list[Lesson]:
        async with self.database.session_factory() as session:
            lessons = await session.execute(select(Lesson.name).distinct())
            return [name for (name,) in lessons.scalars().all()]

    @staticmethod
    async def _get_lessons_by_name(name: str, session) -> list[Lesson]:
        lessons = await session.execute(select(Lesson).where(Lesson.name == name).distinct())
        return lessons.scalars().first()

    @staticmethod
    async def _get_employee_by_id(id: int, session) -> Optional[Employee]:
        employee = await session.execute(select(Employee).where(Employee.id == id))
        return employee.scalars().first()
