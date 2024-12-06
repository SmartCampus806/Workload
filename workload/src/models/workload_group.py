from sqlalchemy import Column, BigInteger, ForeignKey, Table

from src.models.BaseWithId import Base

group_workload_association = Table(
    'group_workload',
    Base.metadata,
    Column('group_id', BigInteger, ForeignKey('groups.id'), primary_key=True),
    Column('workload_id', BigInteger, ForeignKey('workloads.id'), primary_key=True)
)

employee_lesson_association = Table(
    'employee_lesson',
    Base.metadata,
    Column('employee_id', BigInteger, ForeignKey('employees.id'), primary_key=True),
          Column('lesson_id', BigInteger, ForeignKey('lessons.id'), primary_key=True)
)
