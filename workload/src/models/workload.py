from sqlalchemy import Column, BigInteger, String, CheckConstraint, ForeignKey
from sqlalchemy.orm import relationship, Mapped

from src.models import BaseWithId
from src.models.workload_group import group_workload_association, competency_workload_association


class Workload(BaseWithId):
    __tablename__ = 'workloads'  # Используйте согласованную конвенцию именования
    # __table_args__ = {'extend_existing': True}  # Добавление extend_existing

    type = Column(String(255), nullable=False)
    workload = Column(BigInteger, nullable=False)
    employee_id = Column(BigInteger, ForeignKey('employees.id'), nullable=True)  # Исправленная ссылка
    lesson_id = Column(BigInteger, ForeignKey('Lesson.id'), nullable=False)
    mega_workload_id = Column(BigInteger, ForeignKey('mega_workloads.id'), nullable=True)

    employee = relationship("Employee", back_populates="workloads", lazy=False)
    lesson = relationship("Lesson", back_populates="workloads", lazy=False)
    mega_workload = relationship("MegaWorkload", back_populates="workloads", lazy=False)
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
        return f'{self.type}(workload={self.workload}, id={self.id})'