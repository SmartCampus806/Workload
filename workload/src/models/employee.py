from sqlalchemy import Column, BigInteger, String
from sqlalchemy.orm import relationship

from src.models import BaseWithId


class Employee(BaseWithId):
    __tablename__ = 'employees'

    name = Column(String(255), nullable=False)
    available_workload = Column(BigInteger, nullable=False)
    extra_workload = Column(BigInteger, nullable=False)

    workloads = relationship("Workload", back_populates="employee")