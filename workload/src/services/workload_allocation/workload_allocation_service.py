from sqlalchemy import select

from src.services.workload_allocation.genetic_algoritm import GeneticProcessor
from src.services.workload_allocation.allocation_algoritm_1 import Processor1
from src.models import WorkloadContainer, EmployeePosition
from src.utils import Database

from loguru import logger as log

class WorkloadAllocationService:
    def __init__(self, database: Database):
        self.database = database
        self.algo = Processor1()
        self.genetic = GeneticProcessor()

    def process_allocation(self):
        async with self.database.session_factory() as session:
            self.genetic.process_data(WorkloadAllocationService.get_unallocated_workloads(session),
                                      WorkloadAllocationService.get_employees_by_caf_806(session))
            session.commit()

    @staticmethod
    def get_unallocated_workloads(session):
        result_set = session.execute(select(WorkloadContainer)
                                 .where(WorkloadContainer.employee_id.is_not(None))
                                 .distinct())
        workloads:list[WorkloadContainer] = result_set.scalars().unique().all()
        result = []
        for container in workloads:
            if len(container.workloads) != 0 and len(container.workloads[0].lesson.employees) != 0:
                result.append(container)
            else:
                log.info(f"Нагрузка по дисциплине {container.workloads[0].lesson.name} не распределена по причине отсутствия доступных педагогов")
        return result
    @staticmethod
    def get_employees_by_caf_806(session):
        result = session.execute(select(EmployeePosition)
                                 .where(EmployeePosition.is_active == True)
                                 .where(EmployeePosition.department == 'каф 806').distinct())
        return result.scalars().unique().all()
