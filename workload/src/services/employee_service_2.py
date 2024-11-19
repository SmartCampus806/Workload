import time

from sqlalchemy import select
from sqlalchemy import and_
from sqlalchemy.orm import InstrumentedAttribute, selectinload

from src.models import Employee
from src.utils import Logger, Database


class EmployeeService2:
    def __init__(self, database: Database, log: Logger):
        self.log = log
        self.db = database

    async def search(self, model, filters: dict):
        """
        Универсальный метод поиска педагогов в базе.
        :param filters: dict - словарь с фильтрами
        filters = {
            "name": {"op": "like", "value": "%Иван%"},  # Фильтр по подстроке в поле name
            "extra_workload": {"op": ">", "value": 10},  # Фильтр по дополнительной нагрузке, больше 10 часов
            "rate": {"op": "<", "value": 1.0},  # Фильтр по ставке, меньше 1.0
            "type_of_employment": {"op": "in", "value": ["full-time", "part-time"]},  # Фильтр по типу занятости
            "post": {"op": "like", "value": "%teacher%"},  # Фильтр по должности, содержащей "teacher"
            "department": {"op": "==", "value": "кафедра 806"},  # Фильтр по отделу
            "contract_end_date": {"op": ">=", "value": "2025-01-01"},  # Фильтр по дате окончания контракта
            "birthday": {"op": "<", "value": "1990-01-01"},  # Фильтр по дате рождения (меньше 1990)
            "phone": {"op": "like", "value": "%123%"},  # Фильтр по телефону, содержащему "123"
            "mail": {"op": "like", "value": "%@gmail.com"},  # Фильтр по почте с доменом gmail
            "gender": {"op": "==", "value": "male"},  # Фильтр по полу
            "preferred_faculty": {"op": "is", "value": None},  # Фильтр по предпочтению факультета, где значение None
        }
        :return: list[model] - список сущностей, соответствующих условиям.
        """

        query = select(model) #.options(selectinload(Employee.competencies))

        filter_conditions = []
        joins = []

        for field, condition in filters.items():
            if "." in field:
                related_field, related_column = field.split(".", 1)
                join_info = self._build_related_filter(model, related_field, related_column, condition)
                if join_info:
                    joins.append(join_info)
            else:
                filter_condition = self._build_filter(model, field, condition)
                if filter_condition is not None:
                    filter_conditions.append(filter_condition)

        for related_attr, related_condition in joins:
            query = query.join(related_attr).where(related_condition)

        if filter_conditions:
            query = query.where(and_(*filter_conditions))

        async with self.db.session_factory() as session:
            start_time = time.perf_counter()
            result = await session.execute(query)
            result = result.scalars().unique().all()
            elapsed_time = time.perf_counter() - start_time
            self.log.info(f"Поиск завершен. Найдено записей: {len(result)}. Время выполнения поиска:{elapsed_time:.4f} секунд")
            return result

    def _build_filter(self, model, field, condition):
        if not hasattr(model, field):
            self.log.warn(f"Поле {field} отсутствует в модели {model.__name__}")
            return None

        column = getattr(model, field)
        op = condition.get("op", "==")
        value = condition.get("value")

        if value is None:
            return None

        if op == "==":
            return column == value
        elif op == "!=":
            return column != value
        elif op == ">":
            return column > value
        elif op == "<":
            return column < value
        elif op == ">=":
            return column >= value
        elif op == "<=":
            return column <= value
        elif op == "in":
            return column.in_(value)
        elif op == "not_in":
            return column.not_in(value)
        elif op == "like":
            return column.like(value)
        elif op == "is":
            if value is 'None':
                return column.is_(None)
            else:
                return column.is_(value)
        elif op == "is_not":
            if value is 'None':
                return column.is_not(None)
            else:
                return column.is_not(value)
        else:
            self.log.warn(f"Неизвестный оператор: {op} для поля {field}")
            return None

    def _build_related_filter(self, model, related_field, related_column, condition):
        if not hasattr(model, related_field):
            self.log.warn(f"Связь {related_field} отсутствует в модели {model.__name__}")
            return None

        related_attr = getattr(model, related_field)

        if not isinstance(related_attr, InstrumentedAttribute):
            self.log.warn(f"{related_field} не является валидным отношением в модели {model.__name__}")
            return None

        related_model = related_attr.property.mapper.class_
        if not hasattr(related_model, related_column):
            self.log.warn(f"Поле {related_column} отсутствует в модели {related_model.__name__}")
            return None

        column = getattr(related_model, related_column)
        op = condition.get("op", "==")
        value = condition.get("value")

        if value is None:
            return None

        if op == "==":
            related_condition = column == value
        elif op == "!=":
            related_condition = column != value
        elif op == "in":
            related_condition = column.in_(value)
        elif op == "not_in":
            related_condition = ~column.in_(value)
        elif op == "like":
            related_condition = column.like(value)
        else:
            self.log.warn(f"Неизвестный оператор: {op} для связанного поля {related_field}.{related_column}")
            return None

        return related_attr, related_condition
