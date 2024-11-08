from sqlalchemy import Column, BigInteger, ForeignKey, Table

from src.models.BaseWithId import Base

group_workload_association = Table(
    'group_workload',
    Base.metadata,
    Column('group_id', BigInteger, ForeignKey('groups.id'), primary_key=True),
          Column('workload_id', BigInteger, ForeignKey('workloads.id'), primary_key=True)

)

competency_workload_association = Table(
    'competency_workload',
    Base.metadata,
    Column('competency_id', BigInteger, ForeignKey('competencies.id'), primary_key=True),
          Column('workload_id', BigInteger, ForeignKey('workloads.id'), primary_key=True)

)

competency_employee_association = Table(
    'competency_employee',
    Base.metadata,
    Column('competency_id', BigInteger, ForeignKey('competencies.id'), primary_key=True),
          Column('employee_id', BigInteger, ForeignKey('employees.id'), primary_key=True)

)