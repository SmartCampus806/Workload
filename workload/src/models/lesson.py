from typing import Any

from sqlalchemy import Column, BigInteger, String, CheckConstraint, Boolean
from sqlalchemy.orm import relationship, Mapped

from src.models.workload_group import employee_lesson_association
from src.models import BaseWithId


class Lesson(BaseWithId):
    __tablename__ = 'lessons'

    stream = Column(String(255), nullable=False)
    name = Column(String(255), nullable=False)
    year = Column(String(255), nullable=False)
    semester = Column(BigInteger, nullable=False)
    faculty = Column(BigInteger, nullable=False)
    tm = Column(Boolean, nullable=True)

    workloads = relationship("Workload", back_populates="lesson", lazy=False)
    employees: Mapped[list['Employee']] = relationship(
        'Employee',
        secondary=employee_lesson_association,
        back_populates='lessons',
        lazy=False
    )

    def __repr__(self):
        return f'{self.name}'
