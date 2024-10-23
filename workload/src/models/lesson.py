from sqlalchemy import Column, BigInteger, String, CheckConstraint
from sqlalchemy.orm import relationship

from src.models import BaseWithId

class Lesson(BaseWithId):
    __tablename__ = 'Lesson'

    name = Column(String(255), nullable=False)
    year = Column(String(255), comment='2023/2024 или 2024/2025', nullable=False)
    semestr = Column(String(255), CheckConstraint("semestr IN ('Осенний', 'весенний')"), nullable=False)
    faculty = Column(BigInteger, nullable=False)

    workloads = relationship("Workload", back_populates="lesson")