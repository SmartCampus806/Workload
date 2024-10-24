from typing import Optional

import pandas as pd

from src.models import Employee
from src.repositories import EmployeeRepository
from src.utils.logger import Logger


class EmployeeService:
    def __init__(self, employee_repository: EmployeeRepository, log: Logger):
        self.employee_repository = employee_repository
        self.log = log

    def parse_and_save_employees(self, file_data):
        df = pd.read_excel(file_data)
        #TODO: логика парсинга и сохранения

    async def parse_and_save_employee_list(self):
        pass

    async def create_employee(self, employee: Employee) -> Employee:
        return await self.employee_repository.create_employee(employee)

    async def get_by_id(self, id: int) -> Optional[Employee]:
        return await self.employee_repository.get_by_id(id)

    async def get_by_name(self, name: str) -> Optional[Employee]:
        return await self.employee_repository.get_by_name(name)
