
from src.models import Groups, Workload, Lesson, WorkloadContainer
from src.utils.configuration import AppConfig
from src.utils.database_manager import Database
from sqlalchemy.future import select
from src.services.parser import parse_raw_file
from sqlalchemy import text


class ParseWorkloadService:
    def __init__(self, database: Database, config: AppConfig):
        self.database = database
        self.config = config

        self.general_workloads = [("Практическое занятие", "Практические занятия нагрузка"),
                                  ("Лабораторная работа", "Лабораторные работы нагрузка")]

        self.individual_workloads = [("Курсовая работа", "Курсовая работа "),
                                     ("Курсовой проект", "Курсовой проект "),
                                     ("Консультация", "Конс "),
                                     ("Рейтинг", "Рейтинг "),
                                     ("Зачёт", "Зачёт "),
                                     ("Экзамен", "Экзамен ")]
        self.students_workloads = [()]

    async def create_group(self, session, name: str, number_of_students: int):
        new_group = Groups(name=name, students_count=number_of_students)
        session.add(new_group)
        await session.flush()
        return new_group

    async def find_group(self, session, name: str):
        stmt = select(Groups).filter_by(name=name)
        result = await session.execute(stmt)
        group = result.scalars().first()
        return group

    async def find_lesson(self, session, stream: str, name: str, semestr: int, faculty: int) -> bool:
        stmt = select(Lesson).filter_by(stream=stream, name=name, semestr=semestr, faculty=faculty)
        result = await session.execute(stmt)
        lesson = result.scalars().first()
        return lesson

    async def create_lesson(self, session, stream: str, name: str, semestr: int, faculty: int, year="2024/2025"):
        new_lesson = Lesson(stream=stream, name=name, year=year, semestr=semestr, faculty=faculty)
        session.add(new_lesson)
        await session.flush()
        return new_lesson

    async def create_mega_workload(self, session, employee_id=None):
        new_mega_workload = WorkloadContainer(employee_id=employee_id)
        session.add(new_mega_workload)
        return new_mega_workload

    async def create_workload(self, session, type_w: str, workload: int, lesson: Lesson, groups: [Groups]):
        new_workload = Workload(
            type=type_w,
            workload=workload,
            lesson=lesson,
            groups=groups
        )
        session.add(new_workload)
        return new_workload

    async def clear_tables(self, session):
        await session.execute(text("DELETE FROM group_workload"))
        await session.execute(text("DELETE FROM workloads"))
        await session.execute(text("DELETE FROM groups"))
        await session.execute(text("DELETE FROM workload_container"))
        await session.execute(text('DELETE FROM "Lesson"'))

    async def parse_and_save_workload(self, file_data):
        df = parse_raw_file(file_data)

        async with (self.database.session_factory() as session):

            await self.clear_tables(session)
            df.columns.values[5] = "to_drop"
            df = df.fillna(0)

            df = df.sort_values(["Поток ", "Название предмета", "Семестр ", "Лекции план"],
                                ascending=[True, True, True, False])
            df = df.reset_index(drop=True)

            for index, row in df.iterrows():
                if row['Поток '] != 0:

                    group_name = row['Название']
                    number_of_students = row['Студентов ']
                    if not await self.find_group(session, group_name):
                        group = await self.create_group(session, group_name, number_of_students)
                    else:
                        group = await self.find_group(session, group_name)

                    discipline_name = row['Название предмета']
                    semestr = row['Семестр ']
                    faculty = int(row['Факультет'].replace("№", '').split()[-1])
                    stream = str(row['Поток '])

                    if not await self.find_lesson(session, stream, discipline_name, semestr, faculty):

                        lesson = await self.create_lesson(session, stream, discipline_name, semestr, faculty)
                        workload_lection = await self.create_workload(session, type_w="Лекция",
                                                                      workload=row["Лекции план"],
                                                                      lesson=lesson, groups=[group])
                        megaworkload_ind = await self.create_mega_workload(session)
                        workload_lection.workload_container = megaworkload_ind

                    else:
                        workload_lection.groups.append(group)

                    for type_of_single_workload in self.general_workloads + self.individual_workloads:
                        if row[type_of_single_workload[1]] != 0:
                            workload = await self.create_workload(session, type_w=type_of_single_workload[0],
                                                                  workload=row[type_of_single_workload[1]],
                                                                  lesson=lesson,
                                                                  groups=[group])

                            if type_of_single_workload[0] == "Практическое занятие" or type_of_single_workload[0] == "Лабораторная работа":
                                megaworkload_pract_lab = await self.create_mega_workload(session)
                                workload.workload_container = megaworkload_pract_lab

                            else:
                                workload.workload_container = megaworkload_ind

            await session.commit()
