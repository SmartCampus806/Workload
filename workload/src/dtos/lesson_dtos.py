from src.dtos.util_dto import Model, GroupDTO, EmployeeDTO


class WorkloadDTO(Model):
    type: str
    workload: int
    groups: list[GroupDTO]
    employee: EmployeeDTO


class SmallLesson(Model):
    name: str
    year: str
    semestr: str
    faculty: int


class FullLesson(SmallLesson):
    workloads: list[WorkloadDTO]
