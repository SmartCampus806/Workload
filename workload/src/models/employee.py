import re
from sqlalchemy import String, Date, BigInteger, Float, Integer, ForeignKey, Enum
from sqlalchemy.orm import relationship, Mapped, mapped_column, validates
from typing import Any, List
import enum

from src.models.workload_group import employee_lesson_association
from src.models import BaseWithId


class GenderEnum(enum.Enum):
    MALE = 'male'
    FEMALE = 'female'

class Employee(BaseWithId):
    __tablename__ = 'employees'

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    birthday: Mapped[Date] = mapped_column(Date, nullable=True)
    phone: Mapped[str] = mapped_column(String(12), nullable=True)
    mail: Mapped[str] = mapped_column(String(255), nullable=True)
    gender: Mapped[GenderEnum] = mapped_column(Enum(GenderEnum, create_type=True), nullable=True)
    preferred_faculty: Mapped[int] = mapped_column(Integer, nullable=True)

    positions: Mapped[List['EmployeePosition']] = relationship(
        'EmployeePosition', back_populates='employee', lazy=True
    )

    lessons: Mapped[list['Lesson']] = relationship(
        'Lesson',
        secondary=employee_lesson_association,
        back_populates='employees',
        lazy=False
    )

    @property
    def workload(self):
        return sum(position.workload for position in self.positions)

    def __init__(self, name: str, **kw: Any):
        super().__init__(**kw)
        self.name = name

    @validates('phone')
    def validate_phone(self, key, phone):
        phone_pattern = re.compile(r'^\+?[1-9]\d{1,14}$')
        if not phone_pattern.match(phone):
            raise ValueError(f"Invalid phone number: {phone}")
        return phone

    @validates('mail')
    def validate_mail(self, key, mail):
        email_pattern = re.compile(r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$')
        if not email_pattern.match(mail):
            raise ValueError(f"Invalid email address: {mail}")
        return mail

    def __repr__(self):
        return f'{self.name}'
