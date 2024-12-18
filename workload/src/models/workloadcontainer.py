from sqlalchemy import Column, BigInteger, String, CheckConstraint, ForeignKey
from sqlalchemy.orm import relationship, Mapped

from src.models import BaseWithId


class WorkloadContainer(BaseWithId):
    __tablename__ = 'workload_container'

    employee_id = Column(BigInteger, ForeignKey('employee_positions.id'), nullable=True)

    employee = relationship("EmployeePosition", back_populates="workload_containers", lazy=False)
    workloads = relationship("Workload", back_populates="workload_container", lazy=False)

    @property
    def sum_workload(self):
        total_sum = 0
        max_lecture_workload = 0

        for workload in self.workloads:
            if workload.type != 'Лекция':
                total_sum += workload.workload
            else:
                max_lecture_workload = max(max_lecture_workload, workload.workload)

        return total_sum + max_lecture_workload

    @property
    def workload_type(self):
        for workload in self.workloads:
            if workload.type == 'Лекция':
                return 'Лекция'
            elif workload.type == 'Практическое занятие':
                return 'Практическое занятие'
            elif workload.type == 'Лекционное занятие':
                return 'Лекционное занятие'
            elif workload.type == 'Лабораторная работа':
                return 'Лабораторная работа'
            else:
                continue
        return None

    def __repr__(self):
        return f"workload={self.sum_workload}, type={self.workload_type}"
