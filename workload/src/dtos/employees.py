from pydantic import BaseModel
from typing import List, Optional

from src.dtos.util_dto import Model, GroupDTO, EmployeeDTO


class CreateEmployee(BaseModel):
    name: str
    available_workload: int
    extra_workload: int

class LessonDTO(Model):
    name: str
    year: str
    semestr: str
    faculty: int

class WorkloadDTO(Model):
    type: str
    workload: int
    lesson: LessonDTO
    groups: List[GroupDTO]

class EmployeeWithWorkloadDTO(EmployeeDTO):
    workloads: List[WorkloadDTO] = []