import pandas as pd

from src.models import Groups, Workload, Lesson
from src.utils.configuration import AppConfig
from src.utils.database_manager import Database
from sqlalchemy.future import select


class WorkloadService:
    def __init__(self, database: Database, config: AppConfig):
        self.database = database
        self.config = config

    async def group_exists(self, session, name: str) -> bool:
        result = await session.execute(select(Groups).filter(Groups.name == name))
        return result.scalars().first() is not None

    async def create_group(self, session, name: str, number_of_students: int):
        new_group = Groups(name=name, students_count=number_of_students)
        session.add(new_group)

    async def discipline_exists(self, session, name: str, semestr: str, faculty: str) -> bool:
        result = await session.execute(select(Lesson).filter(
            Lesson.name == name,
            Lesson.semestr == semestr,
            Lesson.faculty == faculty
        ))
        return result.scalars().first() is not None

    async def create_lesson(self, session, name: str, semestr: str, faculty: str, year="2024/2025"):
        new_lesson = Lesson(name=name, year=year, semestr=semestr, faculty=faculty)
        session.add(new_lesson)

    async def parse_and_save_workload(self, file_data):
        df = pd.read_excel(file_data)

        async with self.database.session_factory() as session:
            for index, row in df.iterrows():
                group_name = row['Название']
                number_of_students = row['Студентов ']
                if not await self.group_exists(session, group_name):
                    await self.create_group(session, group_name, number_of_students)

                discipline_name = row['Название предмета']
                semestr = row['семестр'].split()[0]
                faculty = row['Факультет']
                if not await self.discipline_exists(session, discipline_name, semestr, faculty):
                    await self.create_lesson(session, discipline_name, semestr, faculty)

                group = await session.execute(select(Groups).filter(Groups.name == row['Название']))
                group = group.scalars().first()

                lesson = await session.execute(select(Lesson).filter(
                    Lesson.name == row['Название предмета'],
                    Lesson.semestr == row['семестр'].split()[0],
                    Lesson.faculty == row['Факультет']
                ))
                lesson = lesson.scalars().first()

                for type_of_single_workload in [
                    ("Практическое занятие", "Практические занятия нагрузка"),
                    ("Лабораторная работа", "Лабораторные работы нагрузка"),
                    ("Курсовая работа", "Курсовая работа "),
                    ("Курсовой проект", "Курсовой проект "),
                    ("Консультация", "Конс "),
                    ("Рейтинг", "Рейтинг "),
                    ("Зачёт", "Зачёт "),
                    ("Экзамен", "Экзамен ")
                ]:
                    if row[type_of_single_workload[1]] != 0:
                        workload = Workload(
                            type=type_of_single_workload[0],
                            workload=row[type_of_single_workload[1]],
                            lesson=lesson,
                            groups=[group]
                        )
                        session.add(workload)

            df.columns.values[6] = "to_drop"
            df = df.drop(df.columns[0], axis=1)

            n = 0
            index_of_sem = df.columns.get_loc("Семестр ")
            index_of_stream = df.columns.get_loc("Поток ")

            index_of_group = df.columns.get_loc("Название")

            index_of_dicsipline = df.columns.get_loc("Название предмета")
            index_of_faculty = df.columns.get_loc("Факультет")
            index_of_season = df.columns.get_loc("семестр")

            lection_workload = df.columns.get_loc("Лекции нагрузка")

            df = df.sort_values(["Поток ", "Название предмета", "Семестр "])
            df = df.reset_index(drop=True)

            df.loc[len(df)] = 0
            len_df = df.shape[0]

            lesson = ''
            groups_list = []

            while n < len_df - 1:

                while df.iloc[n, index_of_stream] == 0:
                    n += 1

                lesson = await session.execute(select(Lesson).filter(
                    Lesson.name == df.iloc[n, index_of_dicsipline],
                    Lesson.semestr == df.iloc[n, index_of_season].split()[0],
                    Lesson.faculty == df.iloc[n, index_of_faculty]
                ))
                lesson = lesson.scalars().first()
                lec_workload = df.iloc[n, lection_workload]

                while (df.iloc[n, index_of_sem],
                       df.iloc[n, index_of_stream],
                       df.iloc[n, index_of_dicsipline]) == (df.iloc[n + 1, index_of_sem],
                                                            df.iloc[n + 1, index_of_stream],
                                                            df.iloc[n + 1, index_of_dicsipline]):
                    group = await session.execute(select(Groups).filter(Groups.name == df.iloc[n, index_of_group]))
                    group = group.scalars().first()

                    groups_list.append(group)
                    n += 1

                group = await session.execute(select(Groups).filter(Groups.name == df.iloc[n, index_of_group]))
                group = group.scalars().first()
                groups_list.append(group)

                workload = Workload(
                    type="Лекция",
                    workload=lec_workload,
                    lesson=lesson,
                    groups=groups_list
                )
                session.add(workload)

                lesson = ""
                groups_list.clear()

                n += 1

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



