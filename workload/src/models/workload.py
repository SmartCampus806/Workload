from sqlalchemy import Column, BigInteger, String, CheckConstraint, ForeignKey
from sqlalchemy.orm import relationship, Mapped
from enum import Enum

from src.models import BaseWithId
from src.models.workload_group import group_workload_association


class WorkloadType(Enum):
    PRACTICAL = "Практическое занятие"
    LABORATORY = "Лабораторная работа"
    COURSE_WORK = "Курсовая работа"
    COURSE_PROJECT = "Курсовой проект"
    CONSULTATION = "Консультация"
    RATING = "Рейтинг"
    CREDIT = "Зачёт"
    EXAM = "Экзамен"
    LECTURE = "Лекция"


class Workload(BaseWithId):
    __tablename__ = 'workloads'  # Используйте согласованную конвенцию именования

    type = Column(Enum(WorkloadType), nullable=False)
    workload = Column(BigInteger, nullable=False)
    lesson_id = Column(BigInteger, ForeignKey('lessons.id'), nullable=False)
    workload_container_id = Column(BigInteger, ForeignKey('workload_container.id'), nullable=True)

    lesson = relationship("Lesson", back_populates="workloads", lazy=False)

    workload_container = relationship("WorkloadContainer", back_populates="workloads", lazy=False)

    groups: Mapped[list['Groups']] = relationship(
        'Groups',
        secondary=group_workload_association,
        back_populates='workloads',
        lazy=False
    )

    def __repr__(self):
        return f'{self.type}(lesson={self.lesson.name}, workload={self.workload})'