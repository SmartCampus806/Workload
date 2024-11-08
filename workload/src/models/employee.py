from sqlalchemy import Column, BigInteger, String
from sqlalchemy.orm import relationship

from src.models import BaseWithId
from sqladmin import ModelView


class Employee(BaseWithId):
    __tablename__ = 'employees'  # Убедитесь, что это точно совпадает

    name = Column(String(255), nullable=False, unique=True)
    available_workload = Column(BigInteger, nullable=False)
    extra_workload = Column(BigInteger, nullable=False)

    workloads = relationship("Workload", back_populates="employee", lazy=False)

    def __repr__(self):
        return f'{self.name}'

