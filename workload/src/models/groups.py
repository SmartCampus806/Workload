from sqlalchemy import Column, BigInteger, String
from sqlalchemy.orm import relationship

from src.models import BaseWithId

class Groups(BaseWithId):
    __tablename__ = 'groups'

    name = Column(String(255), nullable=False)
    students_count = Column(BigInteger, nullable=False)

    workload_groups = relationship("WorkloadGroup", back_populates="group")