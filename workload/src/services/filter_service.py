from typing import Type, Dict, Any, Optional, Tuple, List
from sqlalchemy.future import select
from sqlalchemy import and_, asc, desc
from sqlalchemy.orm import aliased

from src.utils import Database

class FilterService:
    """
    Класс для фильтрации записей в базе данных с поддержкой сортировки и пагинации.
    """

    def __init__(self, database: Database):
        self.database = database

    async def search(
            self,
            model: Type,
            filters: Dict[str, Any],
            sort_by: Optional[Tuple[str, str]] = None,
            pagination: Optional[Tuple[int, int]] = None
    ) -> List:
        """
        Метод для поиска записей в базе данных.

        :param model: Модель SQLAlchemy, по которой выполняется запрос.
        :param filters: Словарь фильтров для применения.
        :param sort_by: Кортеж (поле, направление) для сортировки.
        :param pagination: Кортеж (страница, размер страницы) для пагинации.
        :return: Список найденных записей.
        """
        query = select(model)
        if filters is not None:
            query = self._apply_filters_v2(query, model, filters)
        if sort_by is not None:
            query = self._apply_sorting(query, model, sort_by)
        if pagination is not None:
            query = self._apply_pagination(query, pagination)

        result = await self.database.execute(query)
        return result.scalars().unique().all()

    def _apply_filters(self, query, model, filters: Dict[str, Any]):
        conditions = []
        for field, filter_value in filters.items():
            column = getattr(model, field)

            if isinstance(filter_value, dict):
                for operator, value in filter_value.items():
                    condition = self._build_condition(column, operator, value)
                    if condition is not None:
                        conditions.append(condition)
            else:
                # Простое сравнение для "field": value
                conditions.append(column == filter_value)

        if conditions:
            query = query.where(and_(*conditions))
        return query

    def _build_condition(self, column, operator: str, value: Any):
        """
        Создает SQLAlchemy-условие на основе оператора.
        """
        operators = {
            "==": lambda c, v: c == v,
            "!=": lambda c, v: c != v,
            ">": lambda c, v: c > v,
            ">=": lambda c, v: c >= v,
            "<": lambda c, v: c < v,
            "<=": lambda c, v: c <= v,
            "in": lambda c, v: c.in_(v),
            "like": lambda c, v: c.like(v),
            "ilike": lambda c, v: c.ilike(v),
            "is": lambda c, v: c.is_(v),
        }
        return operators.get(operator, lambda c, v: None)(column, value)

    def _apply_filters_v2(self, query, model, filters: Dict[str, Any]):
        conditions = []
        joins = {}

        for field, filter_value in filters.items():
            *relations, attr = field.split("__")

            current_model = model
            for relation in relations:
                if relation not in joins:
                    related_model = getattr(current_model, relation).property.mapper.class_
                    joins[relation] = aliased(related_model)
                    query = query.join(joins[relation], getattr(current_model, relation))
                current_model = joins[relation]

            column = getattr(current_model, attr)

            if isinstance(filter_value, dict):
                for operator, value in filter_value.items():
                    condition = self._build_condition(column, operator, value)
                    if condition is not None:
                        conditions.append(condition)
            else:
                conditions.append(column == filter_value)

        if conditions:
            query = query.where(and_(*conditions))

        return query
    def _apply_sorting(self, query, model, sort_by: Optional[Tuple[str, str]]):
        if sort_by:
            field, direction = sort_by
            order_func = asc if direction.lower() == 'asc' else desc
            query = query.order_by(order_func(getattr(model, field)))
        return query

    def _apply_sorting_v2(self, query, model, sort_by: Optional[Tuple[str, str]]):
        if sort_by:
            joins = {}
            field, direction = sort_by

            *relations, attr = field.split("__")

            current_model = model
            for relation in relations:
                if relation not in joins:
                    related_model = getattr(current_model, relation).property.mapper.class_
                    joins[relation] = aliased(related_model)
                    query = query.join(joins[relation], getattr(current_model, relation))
                current_model = joins[relation]

            column = getattr(current_model, attr)

            order_func = asc if direction.lower() == 'asc' else desc
            query = query.order_by(order_func(column))

        return query

    def _apply_pagination(self, query, pagination: Optional[Tuple[int, int]]):
        if pagination:
            page, page_size = pagination
            offset = (page - 1) * page_size
            query = query.offset(offset).limit(page_size)
        return query
