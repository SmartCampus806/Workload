from enum import Enum
from typing import Optional

from pydantic import BaseModel

from src.dtos.util_dto import Semester


class CreateWorkload(BaseModel):
    type: str
    workload: int
    lesson_id: int
    employee_id: Optional[int]
    groups: list[int]


class CreateLesson(BaseModel):
    name: str
    year: str
    semester: Semester
    faculty: int


class CreateGroup(BaseModel):
    name: str
    students_count: str
