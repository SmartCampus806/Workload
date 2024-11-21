import time

from sqlalchemy import select, and_, or_
from sqlalchemy.orm import InstrumentedAttribute, joinedload, selectinload

from src.utils import Database, Logger

"""
TODO: если ошибка при парсинге фильтра, кинуть ошибку
более точное логирование (первичная модель фильтр)
"""
import time

from sqlalchemy import select, and_
from sqlalchemy.orm import InstrumentedAttribute, selectinload

class EmployeeService2:
    def __init__(self, database, log):
        self.log = log
        self.db = database

    async def search(self, model, filters: dict):
        """
        Универсальный метод поиска сущностей в базе с поддержкой глубоких связей и сложных фильтров.
        """
        query = select(model)

        # Собираем фильтры и join'ы
        filter_conditions = []
        joins = []

        for field, condition in filters.items():
            if "." in field:
                join_path, join_condition = self._process_related_field(model, field, condition)
                if join_path:
                    joins.append((join_path, join_condition))
            else:
                filter_condition = self._build_filter(model, field, condition)
                if filter_condition is not None:
                    filter_conditions.append(filter_condition)

        # Добавляем join'ы и условия
        for join_path, join_condition in joins:
            query = query.join(*join_path)
            if join_condition is not None:
                query = query.where(join_condition)

        if filter_conditions:
            query = query.where(and_(*filter_conditions))

        query = query.options(selectinload("*"))

        async with self.db.session_factory() as session:
            start_time = time.perf_counter()
            result = await session.execute(query)
            result = result.scalars().unique().all()
            elapsed_time = time.perf_counter() - start_time
            self.log.info(f"Поиск завершен. Найдено записей: {len(result)}. Время выполнения поиска: {elapsed_time:.4f} секунд")
            return result

    def _build_filter(self, model, field, condition):
        """Создание фильтра для одного поля."""
        if not hasattr(model, field):
            self.log.warn(f"Поле {field} отсутствует в модели {model.__name__}")
            return None

        column = getattr(model, field)
        op = condition.get("op", "==")
        value = condition.get("value")

        if value is None:
            return None
        if value == 'None':
            value = None

        operators = {
            "==": lambda: column == value,
            "!=": lambda: column != value,
            ">": lambda: column > value,
            "<": lambda: column < value,
            ">=": lambda: column >= value,
            "<=": lambda: column <= value,
            "in": lambda: column.in_(value),
            "not_in": lambda: ~column.in_(value),
            "like": lambda: column.like(value),
            "is": lambda: column.is_(value),
            "is_not": lambda: column.is_not(value),
        }

        return operators.get(op, lambda: None)()

    def _process_related_field(self, model, field_path, condition):
        """Обработка фильтров для связанных моделей."""
        fields = field_path.split(".")
        related_model = model
        join_path = []  # Список для хранения цепочки join'ов

        for field in fields[:-1]:
            if not hasattr(related_model, field):
                self.log.warn(f"Связь {field} отсутствует в модели {related_model.__name__}")
                return None, None
            related_attr = getattr(related_model, field)
            if not isinstance(related_attr, InstrumentedAttribute):
                self.log.warn(f"{field} не является валидным отношением в модели {related_model.__name__}")
                return None, None

            # Добавляем к пути отношения
            join_path.append(related_attr)
            related_model = related_attr.property.mapper.class_

        related_column = fields[-1]
        if not hasattr(related_model, related_column):
            self.log.warn(f"Поле {related_column} отсутствует в модели {related_model.__name__}")
            return None, None

        column = getattr(related_model, related_column)
        related_condition = self._build_filter(related_model, related_column, condition)

        # Возвращаем только путь для join и условие для where
        return join_path, related_condition
