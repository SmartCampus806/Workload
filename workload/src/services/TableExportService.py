from tempfile import NamedTemporaryFile

from openpyxl.styles import Alignment
from openpyxl.workbook import Workbook
from sqlalchemy import select

from src.models import *
from src.utils import Database


class ExportService:
    def __init__(self, database: Database):
        self.db = database

    async def export_workload(self) -> str:
        wb = Workbook()
        sheet = wb.active
        sheet.title = "Лекциии"

        headers = ["Факультет", "Семестр", "Поток", "Наименование", "Преподаватель", "Нагрузка", "Тип", "Группы", ""]
        sheet.append(headers)

        async with self.db.session_factory() as session:
            containers = await session.execute(select(WorkloadContainer).distinct())
            containers: list[WorkloadContainer] = containers.scalars().unique().all()
            for container in containers:
                groups =  set()
                for workload in container.workloads:
                    groups.update([group.name for group in workload.groups])

                lessons: set[Lesson] = set()
                for workload in container.workloads:
                    lessons.add(workload.lesson)

                sheet.append([
                    ", ".join([str(lesson.faculty) for lesson in lessons]) if len(lessons) != 0 else "",
                    ", ".join([str(lesson.semester) for lesson in lessons]) if len(lessons) != 0 else "",
                    ", ".join([str(lesson.stream) for lesson in lessons]) if len(lessons) != 0 else "",
                    ", ".join([lesson.name for lesson in lessons]) if len(lessons) != 0 else "",
                    container.employee.name if container.employee is not None else "",
                    container.sum_workload,
                    container.workload_type if container.workload_type is not None else "",
                    ", ".join(groups) if len(groups) != 0 else "",
                    "Объединенный поток!!!" if len(lessons) != 1 else "",
                ])

        ExportService.set_width_and_alignment(sheet, [10, 10, 7, 40, 40, 10, 15, 10])
        temp_file = NamedTemporaryFile(delete=False, suffix=".xlsx")
        wb.save(temp_file.name)
        temp_file.close()

        return temp_file.name

    async def export_employees(self) -> str:
        """
        :return: имя файла для экспорта
        """

        wb = Workbook()
        sheet = wb.active
        sheet.title = "Лекциии"

        headers = ["id", "Имя", "Ставка", "Общая нагрузка", "Доступная нагрузка", "Доступная переработка", "???",
                   "Должность", "Департамент", "Завершение контракта", "День рождения", "Номер", "Почта", "Пол",
                   "Предпочитаемый факультет"]

        sheet.append(headers)

        async with self.db.session_factory() as session:
            employees = await session.execute(select(Employee).distinct())
            employees = employees.scalars().unique().all()

            for employee in employees:
                sheet.append([
                    employees.id,
                    employees.name,
                    employees.rate,
                    employees.workload,
                    employees.available_workload,
                    employees.extra_workload,
                    employees.type_of_employment,
                    employees.post,
                    employees.department,
                    employees.contract_end_date,
                    employees.birthday,
                    employees.phone,
                    employees.mail,
                    employees.gender,
                    employees.preferred_faculty
                ])
                
        ExportService.set_width_and_alignment(sheet, [5, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20,])
        temp_file = NamedTemporaryFile(delete=False, suffix=".xlsx")
        wb.save(temp_file.name)
        temp_file.close()

        return temp_file.name

    async def export_lessons(self) -> str:
        """
        Поля таблицы: "id", "Наименование", "Факультет", "Семестр", "Год", "Компетенции"
        :return: имя файла для экспорта
        """

        wb = Workbook()
        sheet = wb.active
        sheet.title = "Лекциии"

        headers = ["id", "Наименование", "Факультет", "Семестр", "Год", "Компетенции", "Поток"]
        sheet.append(headers)

        ExportService.set_width_and_alignment(sheet, [8, 60, 15, 5, 12, 30])
        async with self.db.session_factory() as session:
            lessons = await session.execute(select(Lesson).distinct())
            lessons = lessons.scalars().unique().all()

            for lesson in lessons:
                sheet.append([
                    lesson.id,
                    lesson.name,
                    lesson.faculty,
                    lesson.semestr,
                    lesson.year,
                    ", ".join(lesson.competences.name) if len(lesson.competences) != 0 else "",
                    lesson.stream
                ])

        temp_file = NamedTemporaryFile(delete=False, suffix=".xlsx")
        wb.save(temp_file.name)
        temp_file.close()

        return temp_file.name

    @staticmethod
    def set_width_and_alignment(sheet: Workbook.active, wights: list[int]) -> None:
        for i, width in enumerate(wights, start=1):
            col_letter = chr(64 + i)
            for cell in sheet[col_letter]:
                cell.alignment = Alignment(horizontal="left")
            sheet.column_dimensions[col_letter].width = width
