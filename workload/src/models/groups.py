from sqlalchemy import Column, BigInteger, String
from sqlalchemy.orm import relationship, Mapped

from src.models import BaseWithId
from src.models.workload_group import group_workload_association


class Groups(BaseWithId):
    __tablename__ = 'groups'
    # __table_args__ = {'extend_existing': True}  # Добавление extend_existing

    name = Column(String(255), nullable=False)
    students_count = Column(BigInteger, nullable=False)

    workloads: Mapped[list["Workload"]] = relationship(
        'Workload',
        secondary=group_workload_association,
        back_populates='groups',
        lazy=False
    )

    def __repr__(self):
        return self.name
