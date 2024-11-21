from typing import Any

from sqlalchemy import Column, BigInteger, String, CheckConstraint
from sqlalchemy.orm import relationship, Mapped

from src.models.workload_group import competency_lesson_association
from src.models import BaseWithId

class Lesson(BaseWithId):
    __tablename__ = 'lessons'

    stream = Column(String(255), nullable=False)
    name = Column(String(255), nullable=False)
    year = Column(String(255), comment='2023/2024 или 2024/2025', nullable=False)
    semester = Column(BigInteger, nullable=False)
    faculty = Column(BigInteger, nullable=False)

    workloads = relationship("Workload", back_populates="lesson", lazy=False)
    competences: Mapped[list['Competency']] = relationship(
        'Competency',
        secondary=competency_lesson_association,
        back_populates='lessons',
        lazy=False
    )

    def __repr__(self):
        return f'{self.name}'
