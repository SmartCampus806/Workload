from typing import Optional

import pandas as pd
from sqlalchemy import select

from src.models import Employee, Lesson
from src.utils import Database
from loguru import logger as log


class ParseEmployeeLessonService:
    def __init__(self, database: Database):
        self.database = database

    async def parse(self, file_data):
        try:
            data_frame = pd.read_excel(file_data, sheet_name=2, skiprows=1)
        except Exception as e:
            log.error(f"Ошибка при чтении Excel файла: {e}")
            raise ValueError(f"Ошибка при чтении Excel файла: {e}")

        async with self.database.session_factory() as session:
            for index, row in data_frame.iterrows():
                try:
                    name = row[0]
                    lessons = []
                    if str(row[1]) != 'nan':
                        lessons: list[str] = [lesson.strip() for lesson in str(row[1]).split(",")]
                    #TODO: где может вести

                    if len(lessons) == 0:
                        continue

                    employee = await self.find_employee(session, name)
                    if employee is None:
                        continue

                    for lesson_name in lessons:
                        employee = await ParseEmployeeLessonService._add_lesson_to_employee(lesson_name, employee, session)
                except Exception as ex:
                    log.error(f"Exception on parsing: {ex}")
            await session.commit()



    async def find_employee(self, session, name) -> Optional[Employee]:
        employee = await session.execute(select(Employee).where(Employee.name == name).distinct())
        return employee.scalars().first()

    @staticmethod
    async def _add_lesson_to_employee(lesson_name: str, employee: Employee, session) -> Employee:
        lessons = await ParseEmployeeLessonService._get_lessons_by_name(lesson_name, session)
        employee.lessons += lessons
        await session.commit()
        log.info(f"add {len(lessons)} lessons with name={lesson_name} "
                 f"to employee with id={employee.id} and name={employee.name}")
        return employee

    @staticmethod
    async def _get_lessons_by_name(name: str, session) -> list[Lesson]:
        lessons = await session.execute(select(Lesson).where(Lesson.name == name).distinct())
        return lessons.scalars().unique().all()
