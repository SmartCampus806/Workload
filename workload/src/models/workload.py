from sqlalchemy import Column, BigInteger, String, CheckConstraint, ForeignKey
from sqlalchemy.orm import relationship, Mapped

from src.models import BaseWithId
from src.models.workload_group import group_workload_association, competency_workload_association


class Workload(BaseWithId):
    __tablename__ = 'workloads'  # Используйте согласованную конвенцию именования

    type = Column(String(255), nullable=False)
    workload = Column(BigInteger, nullable=False)
    lesson_id = Column(BigInteger, ForeignKey('Lesson.id'), nullable=False)
    workload_container_id = Column(BigInteger, ForeignKey('workload_container.id'), nullable=True)

    lesson = relationship("Lesson", back_populates="workloads", lazy=False)
    workload_container = relationship("WorkloadContainer", back_populates="workloads", lazy=False)
    groups: Mapped[list['Groups']] = relationship(
        'Groups',
        secondary=group_workload_association,
        back_populates='workloads',
        lazy=False
    )

    competencies: Mapped[list['Competency']] = relationship(
        'Competency',
        secondary=competency_workload_association,
        back_populates='workloads',
        lazy=False
    )

    def __repr__(self):
        return f'{self.type}(lesson={self.lesson.name}, workload={self.workload})'