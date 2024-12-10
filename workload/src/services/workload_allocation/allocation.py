from sqlalchemy import select, and_
from sqlalchemy.orm import selectinload

from src.models import EmployeePosition, Lesson, WorkloadContainer, Employee
from src.utils import Database
from loguru import logger as log


class AllocationService:
    def __init__(self, database: Database):
        """
        Инициализация сервиса распределения нагрузки.
        :param database: Экземпляр класса для взаимодействия с базой данных
        """
        self.database = database

    async def distribute_workload(self):
        """
        Распределяет нагрузку по преподавателям с учетом их компетенций и доступной нагрузки.
        """
        async with self.database.session_factory() as session:
            employees = await AllocationService._get_employees(session)
            workload_containers = await AllocationService._get_unalocated_workload(session)

            for container in workload_containers:
                lesson = container.workloads[0].lesson  # Дисциплина нагрузки

                suitable_employees = [
                    employee for employee in employees
                    if lesson in employee.employee.lessons and employee.available_workload >= container.sum_workload
                ]
                suitable_employees_tmp = [employee for employee in employees if lesson in employee.employee.lessons]

                if not suitable_employees_tmp and len(suitable_employees_tmp) == 0:
                    log.warning(f"{lesson} нет в таблице!!!!")
                    continue

                if not suitable_employees and len(suitable_employees) == 0:
                    log.warning(f"Не найден преподаватель для нагрузки: {container} по дисциплине {lesson}")
                    continue

                suitable_employees.sort(key=lambda e: e.sum_workload)


                assigned_employee = suitable_employees[0] # Преподавтаель с наименьшей нагрузкой

                container.employee_id = assigned_employee.id
                assigned_employee.workload_containers.append(container)

                log.info(f"нагруза: {container} по дисциплине {lesson} распределена на {assigned_employee.employee.name}")

            await session.commit()

    @staticmethod
    async def _get_employees(session):
        employees = await session.execute(select(EmployeePosition)
            .where(and_(
                EmployeePosition.is_active == True,
                EmployeePosition.department == 'кафедра 806',
                EmployeePosition.post != 'инженер',
                EmployeePosition.post != 'ведущий инженер'
            ))
            .options(selectinload(EmployeePosition.employee).selectinload(Employee.lessons))
            .options(selectinload(EmployeePosition.workload_containers))
            .options(selectinload(EmployeePosition.employee))
            .distinct())
        return employees.scalars().all()

    @staticmethod
    async def _get_unalocated_workload(session):
        lessons = await session.execute(select(WorkloadContainer)
            .where(WorkloadContainer.employee_id == None)
            .distinct())
        return lessons.scalars().unique().all()
