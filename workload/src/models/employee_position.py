
from sqlalchemy import String, Date, BigInteger, Float, ForeignKey, Boolean
from sqlalchemy.orm import relationship, Mapped, mapped_column
from typing import Any

from src.models import BaseWithId

class EmployeePosition(BaseWithId):
    __tablename__ = 'employee_positions'

    extra_workload: Mapped[int] = mapped_column(Float, nullable=False)
    rate: Mapped[float] = mapped_column(Float, nullable=False)
    type_of_employment: Mapped[str] = mapped_column(String(255), nullable=False)  # вид занятости
    post: Mapped[str] = mapped_column(String(255), nullable=False)  # должность
    department: Mapped[str] = mapped_column(String(255), nullable=False, default='кафедра 806')
    contract_end_date: Mapped[Date] = mapped_column(Date, nullable=True)
    is_active : Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)

    employee_id: Mapped[int] = mapped_column(ForeignKey('employees.id'))
    employee: Mapped['Employee'] = relationship('Employee', back_populates='positions')

    workload_containers = relationship("WorkloadContainer", back_populates="employee", lazy=True)

    def __init__(self, extra_workload: int, rate: float, type_of_employment: str, post: str, department: str, **kw: Any):
        super().__init__(**kw)
        self.extra_workload = extra_workload
        self.rate = rate
        self.type_of_employment = type_of_employment
        self.post = post
        self.department = department

    @property
    def acceptable_workload(self):
        return self.rate * 830

    @property
    def sum_workload(self):
        return sum(workload.sum_workload for workload in self.workload_containers)

    @property
    def available_workload(self):
        sum_workload = sum(workload.sum_workload for workload in self.workload_containers)
        return self.acceptable_workload - sum_workload

    def __repr__(self):
        return f'{self.post} in {self.department}'
