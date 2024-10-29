from sqlalchemy import Column, BigInteger, String, CheckConstraint, ForeignKey
from sqlalchemy.orm import relationship, Mapped

from src.models import BaseWithId
from src.models.workload_group import group_workload_association


class Workload(BaseWithId):
    __tablename__ = 'workloads'  # Используйте согласованную конвенцию именования

    type = Column(String(255), nullable=False)
    workload = Column(BigInteger, nullable=False)
    employee_id = Column(BigInteger, ForeignKey('employees.id'), nullable=True)  # Исправленная ссылка
    lesson_id = Column(BigInteger, ForeignKey('Lesson.id'), nullable=False)

    employee = relationship("Employee", back_populates="workloads", lazy=False)
    lesson = relationship("Lesson", back_populates="workloads", lazy=False)
    groups: Mapped[list['Groups']] = relationship(
        'Groups',
        secondary=group_workload_association,
        back_populates='workloads',
        lazy=False
    )

    def __repr__(self):
        return f'Workload<id={self.id}, type={self.type}, workload={self.workload}'