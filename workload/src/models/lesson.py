from typing import Any
from enum import Enum

from sqlalchemy import Column, BigInteger, String, CheckConstraint, Boolean, Enum as SQLEnum
from sqlalchemy.orm import relationship, Mapped

from src.models.workload_group import employee_lesson_association
from src.models import BaseWithId


class StageOfEducation(Enum):
    Bachelor = 'Бакалавриат'
    Master = 'Магистратура'
    Postgraduate = 'Аспирантура'
    Speciality = 'Специалитет'
    BasicHigherEd = 'Базовое Высшее Образование'
    SpecialHigherEd = 'Специализироавнное Высшее Образование'
    Other = 'Другое'


class Lesson(BaseWithId):
    __tablename__ = 'lessons'

    stream = Column(String(255), nullable=False)
    name = Column(String(255), nullable=False)
    year = Column(String(255), nullable=False)
    semester = Column(BigInteger, nullable=False)
    faculty = Column(BigInteger, nullable=False)
    tm = Column(Boolean, nullable=True)
    stage_of_education = Column(SQLEnum(StageOfEducation), nullable=False)

    workloads = relationship("Workload", back_populates="lesson", lazy=False)
    employees: Mapped[list['Employee']] = relationship(
        'Employee',
        secondary=employee_lesson_association,
        back_populates='lessons',
        lazy=False
    )

    def __repr__(self):
        return f'{self.name}'
