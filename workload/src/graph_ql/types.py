import strawberry
from typing import List, Optional


@strawberry.type
class CompetencyQ:
    id: int
    name: str
    workloads: List['WorkloadQ']
    employees: List['EmployeeQ']

@strawberry.type
class EmployeeQ:
    id: int
    name: str
    competencies: List[CompetencyQ]
    positions: List['EmployeePositionQ']

@strawberry.type
class EmployeePositionQ:
    extra_workload: int
    rate: float
    type_of_employment: str
    post: str
    department: str
    workload_containers: List['WorkloadContainerQ']
    workload: float

@strawberry.type
class GroupsQ:
    id: int
    name: str
    students_count: int
    workloads: List['WorkloadQ']

@strawberry.type
class LessonQ:
    id: int
    stream: str
    name: str
    year: str
    semestr: int
    faculty: str
    workloads: List['WorkloadQ']

@strawberry.type
class WorkloadQ:
    id: int
    type: str
    workload: int
    lesson: LessonQ
    workload_container: 'WorkloadContainerQ'
    groups: List[GroupsQ]
    competencies: List[CompetencyQ]

@strawberry.type
class WorkloadContainerQ:
    id: int
    type: str
    employee: Optional[EmployeeQ]
    workloads: List[WorkloadQ]

    @strawberry.field
    def sum_workload(self) -> int:
        total_sum = 0
        max_lecture_workload = 0
        for workload in self.workloads:
            if workload.type != 'Лекция':
                total_sum += workload.workload
            else:
                max_lecture_workload = max(max_lecture_workload, workload.workload)
        return total_sum + max_lecture_workload

    @strawberry.field
    def workload_type(self) -> str | None:
        for workload in self.workloads:
            if workload.type == 'Лекция':
                return 'Лекция'
            elif workload.type == 'Практическое занятие':
                return 'Практическое занятие'
            elif workload.type == 'Лекционное занятие':
                return 'Лекционное занятие'
        return None
