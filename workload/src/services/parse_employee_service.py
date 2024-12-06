import time
from typing import Optional

import pandas as pd
from sqlalchemy import select, and_, update
from sqlalchemy.ext.asyncio import AsyncSession

from src.utils import Logger, Database
from src.models import Employee, EmployeePosition


class ParseEmployeeService:
    def __init__(self, database: Database, log: Logger):
        self.log = log
        self.database = database

    async def parse(self, file_data) -> None:
        """
        Парсинг файла с данными о пед. составе
        :param file_data: excel файл с данными
        :return: None
        """
        start_time = time.time()

        try:
            data_frame = pd.read_excel(file_data, skiprows=1)
        except Exception as e:
            self.log.error(f"Ошибка при чтении Excel файла: {e}")
            raise ValueError(f"Ошибка при чтении Excel файла: {e}")

        employees = {}

        async with self.database.session_factory() as session:
            for index, row in data_frame.iterrows():
                try:
                    name = row[1].strip()
                    rate = float(row[2]) if pd.notna(row[2]) else None
                    extra_workload = 300
                    type_of_employment = row[3].strip() if pd.notna(row[3]) else None
                    post = row[4].strip() if pd.notna(row[4]) else None
                    department = row[6].strip() if pd.notna(row[6]) else None

                    employee = await self.getEmployeeByName(name, session, employees)
                    if employee is None:
                        employee = Employee(name=name)
                        session.add(employee)
                        employees[name] = employee

                    position = await self.findEmployeePosition(rate, type_of_employment, post, department,
                                                         employee.id, session)
                    if position is None:
                        position = EmployeePosition(
                            extra_workload=extra_workload,
                            rate=rate,
                            type_of_employment=type_of_employment,
                            post=post,
                            department=department,
                            employee=employee
                        )
                        session.add(position)
                    position.is_active = True
                    await session.commit()
                except Exception as e:
                    self.log.warn(f"Ошибка обработки строки {index + 1}: {e}")

            try:
                await session.commit()
            except Exception as e:
                self.log.error(f"Ошибка при сохранении данных в базу: {e}")
                raise

        end_time = time.time()
        self.log.info(f"Парсинг завершен за {end_time - start_time:.2f} секунд")

    async def getEmployeeByName(self, name: str, session: AsyncSession, employees: dict) -> Optional[Employee]:
        if name in employees:
            return employees[name]

        async with session as session:
            result = await session.execute(select(Employee).where(Employee.name == name))
            employee = result.scalars().first()
            if employee is not None:
                employees[employee.name] = employee
            return employee

    async def markEployeePositionAsUnactive(self, session: AsyncSession):
        async with session as session:
            await session.execute(update(EmployeePosition).values(is_active=False))

    async def findEmployeePosition(self, rate: float, type_of_employment: str, post: str, department: str,
                                   employee_id: int, session: AsyncSession) -> Optional[EmployeePosition]:
        if employee_id is None:
            return None

        async with session as session:
            result = await session.execute(select(EmployeePosition).where(and_(
                EmployeePosition.rate == rate,
                EmployeePosition.type_of_employment == type_of_employment,
                EmployeePosition.post == post,
                EmployeePosition.department == department,
                EmployeePosition.employee_id == employee_id
            )))
            return result.scalars().first()
