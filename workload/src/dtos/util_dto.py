from enum import Enum

from pydantic import BaseModel


class CreateEmployee(BaseModel):
    name: str
    available_workload: int
    extra_workload: int

class Semester(str, Enum):
    autumn = 'Осенний'
    spring = 'Весенний'

class Model(BaseModel):
    id: int

    class Config:
        from_attributes = True

class GroupDTO(BaseModel):
    name: str
    students_count: int

class EmployeeDTO(Model, CreateEmployee):
    pass
