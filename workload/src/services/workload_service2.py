from src.dtos.create_dtos import CreateWorkload
from src.exceptions.all_exceptions import GroupNotFound
from src.models import Workload
from src.repositories import LessonRepository, EmployeeRepository
from src.repositories.group_repository import GroupRepository
from src.repositories.workload_repository import WorkloadRepository
from src.utils.database_manager import Database
from src.utils.logger import Logger


class WorkloadService2:
    def __init__(self, workload_repository: WorkloadRepository, group_repository: GroupRepository,
                 employee_repository: EmployeeRepository, lesson_repository: LessonRepository, log: Logger):
        self.group_repository = group_repository
        self.workload_repository = workload_repository
        self.employee_repository = employee_repository
        self.lesson_repository = lesson_repository
        self.log = log

    async def create_workload(self, workload_dto: CreateWorkload):
        groups = []
        for group_id in workload_dto.groups:
            group = await self.group_repository.get_by_id(group_id)
            if group is None:
                raise GroupNotFound("Group not found")
            groups.append(group)

        workload = Workload(type=workload_dto.type, workload=workload_dto.workload,
                            employee_id=workload_dto.employee_id, lesson_id=workload_dto.lesson_id, groups=groups)

        return await self.workload_repository.create(workload)

