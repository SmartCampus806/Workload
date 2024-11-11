import pandas as pd

from src.models import Groups, Workload, Lesson, MegaWorkload
from src.utils.configuration import AppConfig
from src.utils.database_manager import Database
from sqlalchemy.future import select
from src.raw_file_parsing.parser import parse_raw_file
from sqlalchemy.exc import NoResultFound


class WorkloadService:
    def __init__(self, database:Database, config: AppConfig):
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

    async def group_exists(self, session, name: str) -> bool:
        result = await session.execute(select(Groups).filter(Groups.name == name))
        return result.scalars().first() is not None

    async def create_group(self, session, name: str, number_of_students: int):
        new_group = Groups(name=name, students_count=number_of_students)
        session.add(new_group)
        return new_group

    async def find_group(self, session, name: str):
        group = await session.execute(select(Groups).filter(Groups.name == name))
        group = group.scalars().first()

        if group is None:
            raise NoResultFound(f"Группа с названием '{name}' не найдена.")

        return group

    async def lesson_exists(self, session, name: str, semestr: int, faculty: str) -> bool:
        result = await session.execute(select(Lesson).filter(
            Lesson.name == name,
            Lesson.semestr == semestr,
            Lesson.faculty == faculty
        ))
        return result.scalars().first() is not None

    async def create_lesson(self, session, name: str, semestr: int, faculty: str, year="2024/2025"):
        new_lesson = Lesson(name=name, year=year, semestr=semestr, faculty=faculty)
        session.add(new_lesson)
        return new_lesson

    async def find_lesson(self, session, name: str, semestr: int, faculty: str):
        lesson = await session.execute(select(Lesson).filter(Lesson.name == name,
                                                        Lesson.semestr == semestr,
                                                        Lesson.faculty == faculty))
        lesson = lesson.scalars().first()

        if lesson is None:
            raise NoResultFound(f"Дисциплина с названием '{name}' не найдена.")

        return lesson

    async def mega_workload_exists(self, session, lesson_name: str, type_m: str, semestr: int, faculty: str) -> bool:
        result = await session.execute(select(MegaWorkload).filter(
            MegaWorkload.lesson_name == lesson_name,
            MegaWorkload.type == type_m,
            MegaWorkload.semestr == semestr,
            MegaWorkload.faculty == faculty
        ))
        return result.scalars().first() is not None

    async def create_mega_workload(self, session, lesson_name: str, type_m: str, semestr: int, faculty: str):
        new_mega_workload = MegaWorkload(lesson_name=lesson_name, type=type_m, semestr=semestr, faculty=faculty)
        session.add(new_mega_workload)

    async def find_mega_workload(self, session, lesson_name: str, type_m: str, semestr: int, faculty: str):
        mega_workload = await session.execute(select(MegaWorkload).filter(MegaWorkload.lesson_name == lesson_name,
                                                                     MegaWorkload.type == type_m,
                                                                     MegaWorkload.semestr == semestr,
                                                                     MegaWorkload.faculty == faculty))
        mega_workload = mega_workload.scalars().first()

        if mega_workload is None:
            raise NoResultFound(f"Нагрузка с названием '{lesson_name}' не найдена.")

        return mega_workload

    async def create_workload(self, session, type_w: str, workload: int, lesson: Lesson, groups: [Groups]):
        new_workload = Workload(
            type=type_w,
            workload=workload,
            lesson=lesson,
            groups=groups
        )
        session.add(new_workload)
        return new_workload

    async def parse_and_save_workload(self, file_data):
        df = parse_raw_file(file_data)

        async with self.database.session_factory() as session:
            for index, row in df.iterrows():
                group_name = row['Название']
                number_of_students = row['Студентов ']
                if not await self.group_exists(session, group_name):
                    group = await self.create_group(session, group_name, number_of_students)
                else:
                    group = await self.find_group(session, group_name)

                discipline_name = row['Название предмета']
                semestr = row['Семестр ']
                faculty = row['Факультет']
                if not await self.lesson_exists(session, discipline_name, semestr, faculty):
                    lesson = await self.create_lesson(session, discipline_name, semestr, faculty)
                else:
                    lesson = await self.find_lesson(session, discipline_name, semestr, faculty)

                for type_of_single_workload in self.general_workloads + self.individual_workloads:
                    if row[type_of_single_workload[1]] != 0:
                        await self.create_workload(session, type_w=type_of_single_workload[0],
                                              workload=row[type_of_single_workload[1]], lesson=lesson,
                                              groups=[group])

                        if type_of_single_workload[0] == "Практическое занятие":
                            type_m = "Практика"

                        elif type_of_single_workload[0] == "Лабораторная работа":
                            type_m = "Лабораторная"
                        else:
                            type_m = "Индивидуальная"
                        if not await self.mega_workload_exists(session, discipline_name, type_m, row['Семестр '], faculty):
                            await self.create_mega_workload(session, discipline_name, type_m, row['Семестр '], faculty)

            df.columns.values[6] = "to_drop"
            df = df.drop(df.columns[0], axis=1)

            n = 0
            index_of_sem = df.columns.get_loc("Семестр ")
            index_of_stream = df.columns.get_loc("Поток ")

            index_of_group = df.columns.get_loc("Название")

            index_of_dicsipline = df.columns.get_loc("Название предмета")
            index_of_faculty = df.columns.get_loc("Факультет")

            lection_workload = df.columns.get_loc("Лекции нагрузка")

            df = df.sort_values(["Поток ", "Название предмета", "Семестр "])
            df = df.reset_index(drop=True)

            df.loc[len(df)] = 0
            len_df = df.shape[0]

            groups_list = []

            while n < len_df - 1:

                while df.iloc[n, index_of_stream] == 0:
                    n += 1

                lesson = await self.find_lesson(session, df.iloc[n, index_of_dicsipline], df.iloc[n, index_of_sem],
                                           df.iloc[n, index_of_faculty])
                lec_workload = df.iloc[n, lection_workload]

                while (df.iloc[n, index_of_sem],
                       df.iloc[n, index_of_stream],
                       df.iloc[n, index_of_dicsipline]) == (df.iloc[n + 1, index_of_sem],
                                                            df.iloc[n + 1, index_of_stream],
                                                            df.iloc[n + 1, index_of_dicsipline]):
                    group = await self.find_group(session, df.iloc[n, index_of_group])
                    groups_list.append(group)
                    n += 1

                group = await self.find_group(session, df.iloc[n, index_of_group])
                groups_list.append(group)

                await self.create_workload(session, type_w="Лекция", workload=lec_workload, lesson=lesson, groups=groups_list)

                groups_list.clear()

                n += 1

            workloads = await session.execute(select(Workload))
            workloads = workloads.unique().scalars().all()

            for workload in workloads:
                if workload.type == "Практическое занятие":
                    type_m = "Практика"

                elif workload.type == "Лабораторная работа":
                    type_m = "Лабораторная"
                else:
                    type_m = "Индивидуальная"

                mega_workload = await self.find_mega_workload(db, workload.lesson.name, type_m, workload.lesson.semestr,
                                                   workload.lesson.faculty)

                workload.mega_workload = mega_workload

            await session.commit()


    async def test(self):
        async with self.database.session_factory() as session:
            group = Groups(name="test_group", students_count=12)
            session.add(group)
            group2 = Groups(name="test_group2", students_count=12)
            session.add(group2)

            lesson = Lesson(name='lesson1', year='2024/2025', semestr='Осенний', faculty=8)
            session.add(lesson)

            workload = Workload(type='Лекция', workload=12, lesson=lesson, groups=[group, group2])
            session.add(workload)

            lesson.workloads = [workload]
            group.workloads =[workload]

            await session.commit()



