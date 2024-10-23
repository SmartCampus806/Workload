from sqlalchemy import Column, BigInteger, String, CheckConstraint, ForeignKey
from sqlalchemy.orm import relationship

from src.models import BaseWithId

class Workload(BaseWithId):
    __tablename__ = 'Workload'

    type = Column(String(255), CheckConstraint("type IN ('Лекция', 'Практика', 'Лабораторная', 'Сессия', 'Курсовая', 'Диплом', 'Другое')"), nullable=False)
    workload = Column(BigInteger, nullable=False)
    employee_id = Column(BigInteger, ForeignKey('Employe.id'), nullable=True)
    lesson_id = Column(BigInteger, ForeignKey('Lesson.id'), nullable=False)

    employee = relationship("Employe", back_populates="workloads")
    lesson = relationship("Lesson", back_populates="workloads")