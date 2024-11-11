from sqlalchemy import Column, BigInteger, String, CheckConstraint, ForeignKey
from sqlalchemy.orm import relationship, Mapped

from src.models import BaseWithId

class MegaWorkload(BaseWithId):
    __tablename__ = 'mega_workloads'

    lesson_name = Column(String(255), nullable=False)
    employee_name = Column(String(255), nullable=True)
    type = Column(String(255), CheckConstraint("type IN ('Индивидуальная', 'Практика', 'Лабораторная')"), nullable=False)
    semestr = Column(BigInteger, nullable=False)
    faculty = Column(String(255), nullable=False)

    workloads = relationship("Workload", back_populates="mega_workload", lazy=False)


    def __repr__(self):
        return f'MegaWorkload<lesson_name={self.lesson_name}, type={self.type}'