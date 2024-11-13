from typing import Any

from sqlalchemy import Column, BigInteger, String, CheckConstraint
from sqlalchemy.orm import relationship

from src.models import BaseWithId

class Lesson(BaseWithId):
    __tablename__ = 'Lesson'

    stream = Column(String(255), nullable=False)
    name = Column(String(255), nullable=False)
    year = Column(String(255), comment='2023/2024 или 2024/2025', nullable=False)
    semestr = Column(BigInteger, CheckConstraint("semestr IN ('Осенний', 'Весенний')"), nullable=False)
    faculty = Column(BigInteger, nullable=False)

    workloads = relationship("Workload", back_populates="lesson", lazy=False)

    def __repr__(self):
        return f'{self.name}'
