from typing import Any

from sqlalchemy import Column, BigInteger, String, Float, Date, Integer
from sqlalchemy.orm import relationship, Mapped

from src.models.workload_group import competency_employee_association
from src.models import BaseWithId


class Employee(BaseWithId):
    __tablename__ = 'employees'

    name = Column(String(255), nullable=False)
    extra_workload = Column(BigInteger, nullable=False)
    rate = Column(Float, nullable=False)
    type_of_employment = Column(String(255), nullable=False)
    post = Column(String(255), nullable=False)
    department = Column(String(255), nullable=False, default='кафедра 806')
    contract_end_date = Column(Date, nullable=True)
    birthday = Column(Date, nullable=True)
    phone = Column(String(12), nullable=True)
    mail = Column(String(255), nullable=True)
    gender = Column(String(6), nullable=True)
    preferred_faculty = Column(Integer, nullable=True)

    workload_containers = relationship("WorkloadContainer", back_populates="employee", lazy=False)

    competences: Mapped[list['Competency']] = relationship(
        'Competency',
        secondary=competency_employee_association,
        back_populates='employees',
        lazy=False
    )

    @property
    def workload(self):
        return self.rate * 830

    @property
    def available_workload(self):
        sum = 0
        for workload in self.workload_containers:
            sum += workload.sum_workload
        return self.workload - sum

    def __init__(self, name: str, rate: float, extra_workload: int, type_of_employment: str, post: str,
                 department: str, **kw: Any):
        super().__init__(**kw)
        self.name = name
        self.rate = rate
        self.extra_workload = extra_workload
        self.type_of_employment = type_of_employment
        self.post = post
        self.department = department

    def __repr__(self):
        return f'{self.name}'

