from sqlalchemy import Column, BigInteger, String, CheckConstraint, ForeignKey
from sqlalchemy.orm import relationship, Mapped

from src.models import BaseWithId

class WorkloadContainer(BaseWithId):
    __tablename__ = 'workload_container'

    employee_id = Column(BigInteger, ForeignKey('employees.id'), nullable=True)

    employee = relationship("Employee", back_populates="workload_containers", lazy=False)
    workloads = relationship("Workload", back_populates="workload_container", lazy=False)
