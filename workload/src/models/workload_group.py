from sqlalchemy import Column, BigInteger, ForeignKey, Table

from src.models.BaseWithId import Base

group_workload_association = Table(
    'group_workload',
    Base.metadata,
    Column('group_id', BigInteger, ForeignKey('groups.id'), primary_key=True),
    Column('workload_id', BigInteger, ForeignKey('workloads.id'), primary_key=True)
)

competency_lesson_association = Table(
    'competency_lesson',
    Base.metadata,
    Column('competency_id', BigInteger, ForeignKey('competences.id'), primary_key=True),
          Column('lesson_id', BigInteger, ForeignKey('lessons.id'), primary_key=True)

)

competency_employee_association = Table(
    'competency_employee',
    Base.metadata,
    Column('competency_id', BigInteger, ForeignKey('competences.id'), primary_key=True),
          Column('employee_id', BigInteger, ForeignKey('employees.id'), primary_key=True)

)