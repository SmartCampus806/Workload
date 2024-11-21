from sqlalchemy import Column, String
from sqlalchemy.orm import relationship, Mapped

from src.models import BaseWithId
from src.models.workload_group import competency_lesson_association, \
    competency_employee_association


class Competency(BaseWithId):
    __tablename__ = 'competences'
    name = Column(String(64), nullable=False)

    lessons: Mapped[list['Lesson']] = relationship(
        'Lesson',
        secondary=competency_lesson_association,
        back_populates='competences',
        lazy=False
    )

    employees: Mapped[list['Employee']] = relationship(
        'Employee',
        secondary=competency_employee_association,
        back_populates='competences',
        lazy=False
    )
    def __repr__(self):
        return self.name
