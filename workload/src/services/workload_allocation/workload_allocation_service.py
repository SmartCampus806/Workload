from sqlalchemy import select

from src.services.workload_allocation.allocation_algoritm_1 import Processor1
from src.models import WorkloadContainer, EmployeePosition
from src.utils import Database


class WorkloadAllocationService:
    def __init__(self, database: Database):
        self.database = database
        self.algo = Processor1()

    def process_allocation(self):
        async with self.database.session_factory() as session:
            self.algo.process_data(WorkloadAllocationService.get_unallocated_workloads(session),
                                   WorkloadAllocationService.get_employees_by_caf_806(session))
            session.commit()

    @staticmethod
    def get_unallocated_workloads(session):
        result = session.execute(select(WorkloadContainer)
                                 .where(WorkloadContainer.employee_id.is_not(None))
                                 .distinct())
        return result.scalars().unique().all()

    @staticmethod
    def get_employees_by_caf_806(session):
        result = session.execute(select(EmployeePosition)
                                 .where(EmployeePosition.is_active == True)
                                 .where(EmployeePosition.department == 'каф 806').distinct())
        return result.scalars().unique().all()
