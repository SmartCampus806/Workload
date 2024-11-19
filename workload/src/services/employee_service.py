from typing import Optional, List

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

    async def get_by_name_like(self, name: str) -> List[Employee]:
        return await self.employee_repository.get_by_name_like(name)

    async def get_all(self) -> Optional[List[Employee]]:
        return await self.employee_repository.get_all()

    async def get_all_employees_with_real_workload(self) -> None:
        employees = await self.get_all()
        for empl in employees:
            sum_hourse = 0
            for workload in empl.workloads:
                sum_hourse += workload.workload
            print(f'{empl.name}: available horse = {empl.available_workload - sum_hourse}')
