import re

from src.models import Groups, Workload, Lesson, WorkloadContainer
from src.models.lesson import StageOfEducation
from src.utils.configuration import AppConfig
from src.utils.database_manager import Database
from sqlalchemy.future import select
from src.services.parser import parse_raw_file
from sqlalchemy import text
from datetime import datetime


class ParseWorkloadService:
    def __init__(self, database: Database, config: AppConfig):
        self.database = database
        self.config = config

        self.general_workloads = [("Практическое занятие", "Практические занятия нагрузка"),
                                  ("Лабораторная работа", "Лабораторные работы нагрузка"),
                                  ("Курсовая работа", "Курсовая работа "),
                                  ("Курсовой проект", "Курсовой проект ")]

        self.individual_workloads = [("Консультация", "Конс "),
                                     ("Рейтинг", "Рейтинг "),
                                     ("Зачёт", "Зачёт "),
                                     ("Экзамен", "Экзамен ")]

        self.students_workloads = [("Самостоятельная Работа", "СРС "),
                                   ("Практика", "Практика "),
                                   ("Диплом", "Диплом "),
                                   ("Прочее", "Прочее ")]

    def parse_stage(self, group_name):
        string = group_name.split('-')[1]
        match = re.search(r'[а-яёА-ЯЁ]+', string).group(0)

        if match in ['Б', 'Бк', 'Бки']:
            return StageOfEducation.Bachelor
        elif match in ['М', 'Мки']:
            return StageOfEducation.Master
        elif match in ['С']:
            return StageOfEducation.Speciality
        elif match in ['БВ', 'БВк']:
            return StageOfEducation.BasicHigherEd
        elif match in ['СВ', 'СВк']:
            return StageOfEducation.SpecialHigherEd
        elif match in ['А']:
            return StageOfEducation.Postgraduate
        return StageOfEducation.Other

    def get_academic_year(self):
        now = datetime.now()
        current_year = now.year
        # Учебный год начинается 1 сентября и заканчивается 31 июля
        if now.month >= 8:  # Август и позже
            return f"{current_year}/{current_year + 1}"
        else:  # Январь - Июль
            return f"{current_year - 1}/{current_year}"

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

    async def find_lesson(self, session, stream: str, name: str, semester: int, faculty: int, stage) -> bool:
        stmt = select(Lesson).filter_by(stream=stream,
                                        name=name,
                                        semester=semester,
                                        faculty=faculty,
                                        stage_of_education=stage)
        result = await session.execute(stmt)
        lesson = result.scalars().first()
        return lesson

    async def create_lesson(self, session, stream: str, name: str, semester: int, faculty: int, stage):
        year = self.get_academic_year()
        new_lesson = Lesson(stream=stream,
                            name=name,
                            year=year,
                            semester=semester,
                            faculty=faculty,
                            tm=True,
                            stage_of_education=stage)
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
        await session.execute(text("DELETE FROM workload_container"))
        await session.execute(text('UPDATE "lessons" SET tm = false'))

    async def parse_and_save_workload(self, file_data):
        df = parse_raw_file(file_data)

        async with (self.database.session_factory() as session):
            await self.clear_tables(session)

            df.columns.values[5] = "to_drop"
            df = df.fillna(0)
            df = df.sort_values(["Поток ", "Название предмета", "Семестр ", "Лекции план"],
                                ascending=[True, True, True, False])
            df = df.reset_index(drop=True)

            groups_set = set()
            lessons_set = set()

            for index, row in df.iterrows():
                group_name = row['Название']
                number_of_students = row['Студентов ']

                if group_name not in groups_set:
                    if not await self.find_group(session, group_name):
                        group = await self.create_group(session, group_name, number_of_students)
                    else:
                        group = await self.find_group(session, group_name)
                    groups_set.add(group_name)
                else:
                    group = await self.find_group(session, group_name)

                discipline_name = row['Название предмета']
                semester = row['Семестр ']
                faculty = int(row['Факультет'].replace("№", '').split()[-1])
                stream = str(row['Поток '])
                stage = self.parse_stage(group_name)

                check_lesson = (stream, discipline_name, semester, faculty, stage)

                if row['Поток '] != 0:
                    if check_lesson not in lessons_set:
                        if not await self.find_lesson(session, stream, discipline_name, semester, faculty, stage):
                            lesson = await self.create_lesson(session, stream, discipline_name, semester, faculty, stage)
                        else:
                            lesson = await self.find_lesson(session, stream, discipline_name, semester, faculty, stage)
                            lesson.tm = True
                        lessons_set.add(check_lesson)

                        workload_lection = await self.create_workload(session, type_w="Лекция",
                                                                      workload=row["Лекции план"],
                                                                      lesson=lesson, groups=[group])
                        megaworkload_ind = await self.create_mega_workload(session)
                        
                        if workload_lection.workload != 0:
                            workload_lection.workload_container = megaworkload_ind

                    else:
                        workload_lection.groups.append(group)

                    for type_of_single_workload in self.general_workloads + self.individual_workloads:
                        if row[type_of_single_workload[1]] != 0:
                            workload = await self.create_workload(session, type_w=type_of_single_workload[0],
                                                                  workload=row[type_of_single_workload[1]],
                                                                  lesson=lesson,
                                                                  groups=[group])

                            general_workloads_list = [elem[0] for elem in self.general_workloads]
                            individual_workloads_list = [elem[0] for elem in self.individual_workloads]

                            if type_of_single_workload[0] in general_workloads_list:
                                megaworkload_gen = await self.create_mega_workload(session)
                                workload.workload_container = megaworkload_gen

                            elif type_of_single_workload[0] in individual_workloads_list:
                                workload.workload_container = megaworkload_ind

                elif row['Поток '] == 0:
                    if not await self.find_lesson(session, stream, discipline_name, semester, faculty, stage):
                        lesson = await self.create_lesson(session, stream, discipline_name, semester, faculty, stage)
                    else:
                        lesson = await self.find_lesson(session, stream, discipline_name, semester, faculty, stage)
                        lesson.tm = True

                    for type_of_single_workload in self.general_workloads + self.individual_workloads:
                        if row[type_of_single_workload[1]] != 0:
                            megaworkload_zero_stream = await self.create_mega_workload(session)
                            workload_zero_stream = await self.create_workload(session,
                                                                              type_w=type_of_single_workload[0],
                                                                              workload=row[type_of_single_workload[1]],
                                                                              lesson=lesson,
                                                                              groups=[group])
                            workload_zero_stream.workload_container = megaworkload_zero_stream

            await session.execute(text('DELETE FROM "lessons" WHERE tm = false'))
            await session.commit()
