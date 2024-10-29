from typing import Optional, List

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import joinedload

from src.exceptions import UniqueConstraintViolationException, NotNullConstraintViolationException, \
    ForeignKeyViolationException
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
                self.log.info(f"Saved new employee. data={employee}")
                return employee
            except IntegrityError as e:
                await session.rollback()
                if "unique constraint" in str(e.orig):
                    raise UniqueConstraintViolationException(f"Unique constraint violation: {e.orig}")
                elif "not-null constraint" in str(e.orig):
                    raise NotNullConstraintViolationException(f"Not null constraint violation: {e.orig}")
                elif "ForeignKeyViolationError" in str(e.orig):
                    raise ForeignKeyViolationException("На найдена свзязь при попытке создания объекта")
                raise Exception(f"Unknown exception: {e}")
            finally:
                await session.close()

    async def create_employees(self, employees: list[Employee]) -> None:
        async with self.database.session_factory() as session:
            try:
                session.add_all(employees)
                await session.commit()
                self.log.info(f"Saved new employee. data={employees}")
            except IntegrityError as e:
                await session.rollback()
                if "unique constraint" in str(e.orig):
                    raise UniqueConstraintViolationException(f"Unique constraint violation: {e.orig}")
                elif "not-null constraint" in str(e.orig):
                    raise NotNullConstraintViolationException(f"Not null constraint violation: {e.orig}")
                elif "ForeignKeyViolationError" in str(e.orig):
                    raise ForeignKeyViolationException("На найдена свзязь при попытке создания объекта")
                raise Exception(f"Unknown exception: {e}")
            finally:
                await session.close()

    async def get_by_id(self, id: int) -> Optional[Employee]:
        async with self.database.session_factory() as session:
            result = await session.execute(select(Employee).where(Employee.id == id))
            res = result.scalars().first()
            await session.close()
            return res

    async def get_by_name(self, name: str) -> Optional[Employee]:
        async with self.database.session_factory() as session:
            result = await session.execute(select(Employee).where(Employee.name == name))
            return result.scalars().first()

    async def get_by_name_like(self, name: str) -> List[Employee]:
        async with self.database.session_factory() as session:
            result = await session.execute(select(Employee).where(Employee.name.like(f'%{name}%')))
            return result.scalars().unique().all()

    async def get_all(self) -> List[Employee]:
        async with self.database.session_factory() as session:
            result = await session.execute(select(Employee).distinct())
            return result.scalars().unique().all()
