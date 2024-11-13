from sqlalchemy import Column, BigInteger, String, CheckConstraint, ForeignKey
from sqlalchemy.orm import relationship, Mapped

from src.models import BaseWithId

class MegaWorkload(BaseWithId):
    __tablename__ = 'mega_workloads'

    type = Column(String(255), CheckConstraint("type IN ('Индивидуальная', 'Практика', 'Лабораторная')"), nullable=True)
    employee_name = Column(String(255), nullable=True)
    workloads = relationship("Workload", back_populates="mega_workload", lazy=False)
