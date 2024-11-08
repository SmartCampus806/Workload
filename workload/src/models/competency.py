from sqlalchemy import Column, String
from sqlalchemy.orm import relationship, Mapped

from src.models import BaseWithId
from src.models.workload_group import competency_workload_association, \
    competency_employee_association


class Competency(BaseWithId):
    __tablename__ = 'competencies'
    name = Column(String(64), nullable=False)

    workloads: Mapped[list['Workload']] = relationship(
        'Workload',
        secondary=competency_workload_association,
        back_populates='competencies',
        lazy=False
    )

    employees: Mapped[list['Employee']] = relationship(
        'Employee',
        secondary=competency_employee_association,
        back_populates='competencies',
        lazy=False
    )
    def __repr__(self):
        return self.name
