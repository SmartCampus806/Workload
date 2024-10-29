from enum import Enum

from pydantic import BaseModel

from src.dtos.employees import CreateEmployee


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
