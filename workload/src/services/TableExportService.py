from openpyxl.workbook import Workbook
from sqlalchemy import select

from src.utils import Database
from src.models import *

class ExportService:
    def __init__(self, database: Database):
        self.db = database

    async def export_lessons(self):
        """
        Поля для экспорта: Предмет(название, год, семестр, факультет), компетенции, все виды нагрузок
        :return:
        """

        wb = Workbook()
        sheet = wb.active  # Получаем активный лист
        sheet.title = "Данные"  # Устанавливаем название листа

        # Добавляем заголовки столбцов
        headers = ["Дисциплина", "Возраст", "Должность", "Зарплата"]
        sheet.append(headers)

        async with self.db.session_factory() as session:
            containers: list[WorkloadContainer] = await session.execute(select(Employee).distinct()).scalars().unique().all()


