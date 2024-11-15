from sqlalchemy import Column, BigInteger, String
from sqlalchemy.orm import relationship, Mapped

from src.models.workload_group import competency_employee_association
from src.models import BaseWithId


class Employee(BaseWithId):
    __tablename__ = 'employees'  # Убедитесь, что это точно совпадает

    name = Column(String(255), nullable=False, unique=True)
    available_workload = Column(BigInteger, nullable=False)
    extra_workload = Column(BigInteger, nullable=False)

    workload_containers = relationship("WorkloadContainer", back_populates="employee", lazy=False)

    competencies: Mapped[list['Competency']] = relationship(
        'Competency',
        secondary=competency_employee_association,
        back_populates='employees',
        lazy=False
    )
    def __repr__(self):
        return f'{self.name}'

