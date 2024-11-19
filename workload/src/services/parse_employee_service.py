import pandas as pd

from src.repositories import EmployeeRepository
from src.utils import Database, Logger
from src.models import Employee


class ParseEmployeeService:
    def __init__(self, employee_repo: EmployeeRepository, log: Logger):
        self.log = log
        self.employee_repo = employee_repo

    async def parse(self, file_data) -> None:
        """
        Парсинг файла с данными о пед. составе 806 кафедры
        :param file_data: excel файл с данными
        :return: Список объектов преподавателей
        """
        try:
            data_frame = pd.read_excel(file_data, skiprows=1)
        except Exception as e:
            raise ValueError(f"Ошибка при чтении Excel файла: {e}")

        employees = []
        for _, row in data_frame.iterrows():
            try:
                if str(row[3]) == 'nan':
                    type_of_employment = None
                else:
                    type_of_employment = row[3].strip()

                employee = Employee(name=row[1].strip(), rate=float(row[2]), extra_workload=0, type_of_employment=type_of_employment,
                               post=row[4].strip(), department=row[6].strip())

                employees.append(employee)
            except IndexError as e:
                print(f"Ошибка обработки строки: {row}. {e}")

        await self.employee_repo.create_employees(employees)
