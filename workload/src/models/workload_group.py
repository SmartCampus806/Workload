from sqlalchemy import Column, BigInteger, String, CheckConstraint, ForeignKey
from sqlalchemy.orm import relationship

from src.models.BaseWithId import Base
class WorkloadGroup(Base):
    __tablename__ = 'workload_groups'

    group_id = Column(BigInteger, ForeignKey('Groups.id'), primary_key=True)
    workload_group = Column(BigInteger, ForeignKey('Workload.id'), primary_key=True)

    group = relationship("Groups", back_populates="workload_groups")