from typing import Optional

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError

from src.exceptions import UniqueConstraintViolationException, NotNullConstraintViolationException
from src.models.employee import Employee
from src.utils.database_manager import Database
from src.utils.logger import Logger


class EmployeeRepository:
    def __init__(self, database: Database, log: Logger):
        self.database = database
        self.log = log

    async def create_employee(self, employee: Employee) -> Employee:
        async with self.database.session_factory() as session:
            try:
                session.add(employee)
                await session.commit()
                await session.refresh(employee)
                self.log.info(f"Saved new user. data={employee}")
                return employee
            except IntegrityError as e:
                await session.rollback()
                if "unique constraint" in str(e.orig):
                    raise UniqueConstraintViolationException(f"Unique constraint violation: {e.orig}")
                elif "not-null constraint" in str(e.orig):
                    raise NotNullConstraintViolationException(f"Not null constraint violation: {e.orig}")
                raise Exception(f"Unknown exception: {e}")

    async def get_by_id(self, id: int) -> Optional[Employee]:
        async with self.database.session_factory() as session:
            result = await session.execute(select(Employee).where(Employee.id == id))
            return result.scalars().first()

    async def get_by_name(self, name: str) -> Optional[Employee]:
        async with self.database.session_factory() as session:
            result = await session.execute(select(Employee).where(Employee.name == name))
            return result.scalars().first()
