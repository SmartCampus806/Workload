from sqlalchemy import Column, BigInteger, String, CheckConstraint, ForeignKey, Table, Integer
from sqlalchemy.orm import relationship, mapped_column

from src.models.BaseWithId import Base

group_workload_association = Table(
    'group_workload',
    Base.metadata,
    Column('group_id', BigInteger, ForeignKey('groups.id'), primary_key=True),
          Column('workload_id', BigInteger, ForeignKey('workloads.id'), primary_key=True)

)